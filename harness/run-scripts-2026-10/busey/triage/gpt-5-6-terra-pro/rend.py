# rend.py SVG OUT.png [KEY=VAL ...] [-SINGLE]: render z2 with mst2 and the sweep env
import os, subprocess, sys
from PIL import Image
env = {**os.environ, 'FRAME_W': '460', 'FRAME_H': '260', 'BOX': '200', 'BOX_X': '130', 'BOX_Y': '30',
       'SKIP_UNSUPPORTED_FILTERS': '1', 'VIEWPORT_CLIP': '1', 'LAYER_STATS': '1', 'TRANSIENT_BUDGET_MB': '1024',
       'SINGLE_SHADOW_LAYER': '1'}
z = '2'
for a in sys.argv[3:]:
    if a == '-SINGLE': env.pop('SINGLE_SHADOW_LAYER')
    elif a.startswith('z='): z = a[2:]
    else:
        k, v = a.split('=', 1); env[k] = v
ppm = sys.argv[2] + '.ppm'
r = subprocess.run(['/Users/matt/src/femtovg-wt/bin/_logos_full_mst2', z, ppm, sys.argv[1]], env=env, capture_output=True, text=True)
sys.stderr.write(r.stderr[-3000:] if 'LAYER_LOG' in env else '\n'.join(l for l in r.stderr.splitlines() if 'layers' in l or 'cfgs' in l) + '\n')
Image.open(ppm).save(sys.argv[2]); os.remove(ppm)
