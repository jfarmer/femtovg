"""rend.py TAG KEY|SVGPATH frs=z2,hd [ENV=VAL ...] [-SINGLE]: render with _logos_full_mst4 (harness defaults: rule 4a merge)
into png/TAG_KEY_FR.png. KEY 'name' -> corpus__buseybench__name with the corpus svg; an svg path -> key t__<stem>."""
import os, sys, subprocess, json
from PIL import Image
S='/Users/matt/src/femtovg-wt/runs/busey/triage/new-five-r2-verify'
BIN='/Users/matt/src/femtovg-wt/bin/_logos_full_mst4'
DEFAULT = {'FRAME_W': '460', 'FRAME_H': '260', 'BOX': '200', 'BOX_X': '130', 'BOX_Y': '30'}
HD = {'FRAME_W': '1920', 'FRAME_H': '1080', 'BOX': '1080', 'BOX_X': '420', 'BOX_Y': '0'}
FR = {'z1': (DEFAULT, 1.0), 'z2': (DEFAULT, 2.0), 'z4': (DEFAULT, 4.0), 'hd': (HD, 1.0)}
SWEEP = {'SKIP_UNSUPPORTED_FILTERS': '1', 'VIEWPORT_CLIP': '1', 'LAYER_STATS': '1', 'TRANSIENT_BUDGET_MB': '1024'}
tag, what = sys.argv[1], sys.argv[2]
frs = ['z2', 'hd']; extra = {}
for a in sys.argv[3:]:
    k, v = a.split('=', 1)
    if k == 'frs': frs = v.split(',')
    else: extra[k] = v
if what.endswith('.svg'):
    svg = what; key = 't__' + os.path.basename(what)[:-4]
else:
    svg = f'/Users/matt/src/femtovg-wt/da/corpus/buseybench/{what}.svg'; key = 'corpus__buseybench__' + what
os.makedirs(f'{S}/png', exist_ok=True)
for fr in frs:
    env, z = FR[fr]
    ppm = f'{S}/png/{tag}_{key}_{fr}.ppm'
    r = subprocess.run([BIN, f'{z:g}', ppm, svg], env={**os.environ, **env, **SWEEP, **extra}, capture_output=True, text=True, timeout=600)
    open(f'{S}/png/{tag}_{key}_{fr}.log', 'w').write(r.stderr)
    Image.open(ppm).save(ppm[:-4] + '.png'); os.remove(ppm)
    print(tag, key, fr, 'rc', r.returncode)
