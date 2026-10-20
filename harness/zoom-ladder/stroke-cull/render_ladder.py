#!/usr/bin/env python3
"""Draw one SVG through the zoom ladder in one harness process (as zoom_ladder.py does) and save NN.png per step.

  render_ladder.py BINARY SVG OUTDIR
"""
import os, subprocess, sys
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
CORPUS_RUN = os.path.join(HERE, '..', '..', 'corpus_run')  # harness/corpus_run on demo-assets
sys.path.insert(0, CORPUS_RUN if os.path.isdir(CORPUS_RUN) else os.path.expanduser('~/src/femtovg-wt/da/harness/corpus_run'))
from common import FRAMINGS, SWEEP_ENV
from zoom_ladder import LADDER

binary, svg, outdir = sys.argv[1:4]
os.makedirs(outdir, exist_ok=True)
ppm = os.path.join(outdir, 'ladder.ppm')
env = {**os.environ, **FRAMINGS['z1'][0], **SWEEP_ENV, 'ZOOM_LADDER': ','.join(f'{z:g}' for z in LADDER)}
r = subprocess.run([binary, '1', ppm, svg], env=env, capture_output=True, text=True, timeout=600)
if r.returncode:
    sys.exit(r.stderr[-2000:])
for line in r.stderr.splitlines():
    if 'cfgs' in line:
        print(line)
for i in range(len(LADDER)):
    p = f'{ppm}.{i:02}.ppm'
    Image.open(p).save(os.path.join(outdir, f'{i:02}.png'))
    os.remove(p)
if os.path.exists(ppm):
    os.remove(ppm)
print(outdir, len(LADDER), 'steps')
