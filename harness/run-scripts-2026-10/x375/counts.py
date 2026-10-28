#!/usr/bin/env python3
"""counts.py OUT.jsonl - for every BuseyBench portrait at the four framings, per build variant: render passes,
command buffers, page faults while the GPU runs the frame (wait phase, the last of FRAMES), from the fault-counting
binaries xm14 (master) and xpc14 (#368 merged). Deterministic counts, so the machine's load does not matter."""
import json, os, re, subprocess, sys
sys.path.insert(0, '/Users/matt/src/femtovg-wt/da/harness/corpus_run')
os.environ.setdefault('CORPUS_RUN_OUT', '/Users/matt/src/femtovg-wt/runs/pm14')
from common import *
VARIANTS = {'master': ('xm14', {}), 'unsliced': ('xpc14', {'NO_SLICES': '1'}), 'sliced64': ('xpc14', {}),
            'sliced200': ('xpc14', {'SLICE_PASSES': '200'})}
out_path = sys.argv[1]
done = set()
if os.path.exists(out_path):
    for l in open(out_path):
        r = json.loads(l); done.add((r['key'], r['framing'], r['variant']))
out = open(out_path, 'a')
for f in [f for f in files() if f['group'] == 'buseybench']:
    for framing in DEFAULT_FRAMINGS:
        for v, (b, extra) in VARIANTS.items():
            if (f['key'], framing, v) in done:
                continue
            fr, z = FRAMINGS[framing]
            ppm = f'/Users/matt/src/femtovg-wt/runs/x375/c_{os.getpid()}.ppm'
            r = subprocess.run([f'{BIN}/_logos_full_{b}', f'{z:g}', ppm, f['path']], capture_output=True, text=True,
                               env={**os.environ, **fr, **SWEEP_ENV, **extra, 'XFAULTS': '1', 'MEM_PEAKS': '1',
                                    'MEM_SETTLE_MS': '0', 'FRAMES': '6'})
            xf = [l for l in r.stderr.splitlines() if l.startswith('XF ')]
            mem = re.search(r'passes=(\d+) command_buffers=(\d+)', r.stderr)
            row = {'key': f['key'], 'framing': framing, 'variant': v,
                   'faults': int(re.search(r'wait=(\d+)', xf[-1]).group(1)) if xf else None,
                   'passes': int(mem.group(1)) if mem else None, 'buffers': int(mem.group(2)) if mem else None}
            out.write(json.dumps(row) + '\n'); out.flush()
            if os.path.exists(ppm): os.remove(ppm)
