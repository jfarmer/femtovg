#!/usr/bin/env python3
"""Transient-image need per frame: every corpus file at the four framings with the budget lifted, recording the
bytes charged to the budget at the flush (the pool's high-water mark) and the layer counts.
  needs.py BUILD OUT.jsonl"""
import json, os, re, subprocess, sys
sys.path.insert(0, '/Users/matt/src/femtovg-wt/da/harness/corpus_run')
os.environ.setdefault('CORPUS_RUN_OUT', os.path.dirname(os.path.abspath(__file__)))
from common import FRAMINGS, SWEEP_ENV, BUILDS, OUT as R
binary, extra = BUILDS[sys.argv[1]]
out = open(sys.argv[2], 'a')
for f in json.load(open(f'{R}/files.json')):
    text = open(f['path'], errors='replace').read()
    if not re.search(r'filter=|mask=|opacity=|mix-blend-mode|<filter', text): continue   # no layer, no transient image
    for framing in ('z1', 'z2', 'z4', 'hd'):
        fr, z = FRAMINGS[framing]
        ppm = f'{R}/tmp/needs.ppm'
        r = subprocess.run([binary, f'{z:g}', ppm, f['path']], env={**os.environ, **fr, **SWEEP_ENV, **extra, 'TRANSIENT_BUDGET_MB': '16384'}, capture_output=True, text=True, timeout=900)
        st = {k: int(v) for k, v in re.findall(r'(layers begun|layers passed through|transient bytes held at flush): (\d+)', r.stderr)}
        out.write(json.dumps({'key': f['key'], 'group': f['group'], 'framing': framing, 'need': st.get('transient bytes held at flush', 0), 'layers': st.get('layers begun', 0), 'passed': st.get('layers passed through', 0)}) + '\n'); out.flush()
print('NEEDS_DONE')
