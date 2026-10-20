#!/usr/bin/env python3
"""Frame time and peak memory of one process per frame, one at a time: `timing.py build keysfile framings...`
appends to timing.jsonl rows {key, framing, build, frame_ms, peak_footprint, peak_graphics, max_sigma_px}.
max_sigma_px is the largest feGaussianBlur sigma of the file in device pixels at that framing (box fit times zoom)."""
import json, os, re, subprocess, sys
sys.path.insert(0, '/Users/matt/src/femtovg-wt/da/harness/corpus_run')
os.environ.setdefault('CORPUS_RUN_OUT', os.path.dirname(os.path.abspath(__file__)))
from common import *
R = os.environ['CORPUS_RUN_OUT']
build, keys = sys.argv[1], set(json.load(open(sys.argv[2])))
framings = sys.argv[3:] or ['hd']
done = set()
path = f'{R}/timing.jsonl'
if os.path.exists(path):
    for line in open(path):
        r = json.loads(line); done.add((r['key'], r['framing'], r['build']))
out = open(path, 'a')
def max_sigma(f, framing):
    t = open(f['path'], errors='replace').read()
    sds = [float(v) for s in re.findall(r'stdDeviation="([^"]*)"', t) for v in s.replace(',', ' ').split()]
    if not sds: return 0.0
    m = re.search(r"<svg\b([^>]*)>", t).group(1)
    vb = re.search(r'viewBox="([^"]*)"', m)
    vw, vh = ([float(x) for x in vb.group(1).replace(',', ' ').split()][2:4]) if vb else (100.0, 100.0)
    fr, z = FRAMINGS[framing]
    return max(sds) * float(fr['BOX']) / max(vw, vh) * z
n = 0
for f in files():
    if f['key'] not in keys: continue
    for framing in framings:
        if (f['key'], framing, build) in done: continue
        binary, extra = BUILDS[build]; fr, z = FRAMINGS[framing]
        ppm = f'{R}/tmp_timing.ppm'
        r = subprocess.run([binary, f'{z:g}', ppm, f['path']], env={**os.environ, **fr, **SWEEP_ENV, **extra, 'MEM_PEAKS': '1', 'MEM_SETTLE_MS': '0'}, capture_output=True, text=True, timeout=600)
        row = {'key': f['key'], 'framing': framing, 'build': build, 'max_sigma_px': round(max_sigma(f, framing), 1)}
        m = re.search(r'^MEM (.*)$', r.stderr, re.M)
        if m:
            row.update({k: float(v) for k, v in re.findall(r'(\w+)=([\d.]+)', m.group(1)) if k in ('frame_ms', 'peak_footprint', 'peak_graphics', 'peak_cpu')})
        else:
            row['error'] = r.stderr.strip()[-200:]
        if os.path.exists(ppm): os.remove(ppm)
        out.write(json.dumps(row) + '\n'); out.flush(); n += 1
print(build, n, 'frames timed')
