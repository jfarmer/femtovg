#!/usr/bin/env python3
"""mem14.py OUT.jsonl - peak footprint of one frame, one process per frame and one at a time, for every BuseyBench
portrait at the four framings under master (m14), #368 merged unsliced (pc14 NO_SLICES) and sliced (pc14): the
method of the 2026-10-02 corpus run (MEM_PEAKS samples the task ledgers; FRAMES=1). Builds alternate per frame."""
import json, os, re, subprocess, sys
sys.path.insert(0, '/Users/matt/src/femtovg-wt/da/harness/corpus_run')
os.environ.setdefault('CORPUS_RUN_OUT', '/Users/matt/src/femtovg-wt/runs/pm14')
from common import *
VARIANTS = [('master', 'm14', {}), ('unsliced', 'pc14', {'NO_SLICES': '1'}), ('sliced', 'pc14', {})]
out_path = sys.argv[1]
done = set()
if os.path.exists(out_path):
    for l in open(out_path):
        r = json.loads(l); done.add((r['key'], r['framing'], r['variant']))
out = open(out_path, 'a')
for i, f in enumerate([f for f in files() if f['group'] == 'buseybench']):
    for framing in DEFAULT_FRAMINGS:
        order = VARIANTS if i % 2 == 0 else VARIANTS[::-1]
        for v, b, extra in order:
            if (f['key'], framing, v) in done:
                continue
            fr, z = FRAMINGS[framing]
            ppm = f'/Users/matt/src/femtovg-wt/runs/x375/m_{os.getpid()}.ppm'
            r = subprocess.run([f'{BIN}/_logos_full_{b}', f'{z:g}', ppm, f['path']], capture_output=True, text=True,
                               env={**os.environ, **fr, **SWEEP_ENV, **extra, 'MEM_PEAKS': '1', 'MEM_SETTLE_MS': '0',
                                    'FRAMES': '1'})
            m = re.search(r'peak_footprint=(\d+) peak_graphics=(\d+)', r.stderr)
            p = re.search(r'passes=(\d+) command_buffers=(\d+)', r.stderr)
            out.write(json.dumps({'key': f['key'], 'framing': framing, 'variant': v,
                                  'peak_footprint': int(m.group(1)) if m else None,
                                  'peak_graphics': int(m.group(2)) if m else None,
                                  'passes': int(p.group(1)) if p else None}) + '\n')
            out.flush()
            if os.path.exists(ppm): os.remove(ppm)
