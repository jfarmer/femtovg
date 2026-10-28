import os, subprocess, sys
from PIL import Image
# rend.py SVG OUT.png [K=V|K=-]...  z2, as accuracy.py runs mst2 (SINGLE_SHADOW_LAYER=1 unless removed)
svg, out = sys.argv[1], sys.argv[2]
env = {**os.environ, 'FRAME_W':'460','FRAME_H':'260','BOX':'200','BOX_X':'130','BOX_Y':'30',
       'SKIP_UNSUPPORTED_FILTERS':'1','VIEWPORT_CLIP':'1','LAYER_STATS':'1','TRANSIENT_BUDGET_MB':'1024','SINGLE_SHADOW_LAYER':'1'}
for a in sys.argv[3:]:
    k, v = a.split('=',1)
    if v == '-': env.pop(k, None)
    else: env[k] = v
ppm = out + '.ppm'
r = subprocess.run(['/Users/matt/src/femtovg-wt/bin/_logos_full_mst2','2',ppm,svg], env=env, capture_output=True, text=True)
if r.returncode: print(r.stderr[-800:]); sys.exit(1)
Image.open(ppm).save(out); os.remove(ppm)
if os.environ.get('SHOWLOG'): print(r.stderr)
