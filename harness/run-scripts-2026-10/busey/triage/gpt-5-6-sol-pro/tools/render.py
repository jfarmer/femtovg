#!/usr/bin/env python3
"""render.py SVG OUT.png [ENV=VAL ...] : z2 frame from the mst2 binary, run as accuracy.py runs it, plus overrides
(ENV=- removes a variable)."""
import os, subprocess, sys
from PIL import Image
svg, out = sys.argv[1], sys.argv[2]
HD = os.environ.get('HDFR') == '1'
env = {**os.environ, 'FRAME_W': '460', 'FRAME_H': '260', 'BOX': '200', 'BOX_X': '130', 'BOX_Y': '30',
       'SKIP_UNSUPPORTED_FILTERS': '1', 'VIEWPORT_CLIP': '1', 'LAYER_STATS': '1', 'TRANSIENT_BUDGET_MB': '1024',
       'SINGLE_SHADOW_LAYER': '1'}
for a in sys.argv[3:]:
    k, v = a.split('=', 1)
    if v == '-': env.pop(k, None)
    else: env[k] = v
ppm = out + '.ppm'
if HD: env.update({'FRAME_W': '1920', 'FRAME_H': '1080', 'BOX': '1080', 'BOX_X': '420', 'BOX_Y': '0'})
r = subprocess.run(['/Users/matt/src/femtovg-wt/bin/_logos_full_mst2', '1' if HD else '2', ppm, svg], env=env, capture_output=True, text=True)
if r.returncode: print(r.stderr[-800:]); sys.exit(1)
Image.open(ppm).save(out); os.remove(ppm)
for l in r.stderr.splitlines():
    if 'layers begun' in l or 'passed through' in l or 'skipped' in l: print(' ', l)
