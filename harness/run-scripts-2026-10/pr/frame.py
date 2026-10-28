#!/usr/bin/env python3
"""Render one corpus file with a build at a framing, as accuracy.py does, to a PNG.
  frame.py <build> <key> <framing> <out.png>"""
import json, os, subprocess, sys
sys.path.insert(0, '/Users/matt/src/femtovg-wt/da/harness/corpus_run')
os.environ.setdefault('CORPUS_RUN_OUT', os.path.dirname(os.path.abspath(__file__)))
from common import FRAMINGS, SWEEP_ENV, BUILDS
from PIL import Image
build, key, framing, out = sys.argv[1:5]
f = {x['key']: x for x in json.load(open(f'{os.path.dirname(os.path.abspath(__file__))}/files.json'))}[key]
binary, extra = BUILDS[build] if build in BUILDS else (build, {})
fr, z = FRAMINGS[framing]
ppm = out + '.ppm'
r = subprocess.run([binary, f'{z:g}', ppm, f['path']], env={**os.environ, **fr, **SWEEP_ENV, **extra}, capture_output=True, text=True, timeout=300)
if r.returncode != 0 or not os.path.exists(ppm):
    sys.exit(f'{build} {key} {framing}: rc {r.returncode}\n{r.stderr[-600:]}')
Image.open(ppm).save(out); os.remove(ppm)
print(out, [l for l in r.stderr.splitlines() if 'layers' in l or 'cfgs' in l][:3])
