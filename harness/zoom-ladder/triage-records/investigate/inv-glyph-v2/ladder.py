import json, os, subprocess, sys, tempfile, shutil
import numpy as np
from PIL import Image
LADDER = [1, 1.25, 1.5, 1.75, 2, 3, 4, 3, 2, 1.75, 1.5, 1.25, 1, 0.75, 0.5, 0.33, 0.25, 0.33, 0.5, 0.75, 1]
BASE = dict(FRAME_W='460', FRAME_H='260', BOX='200', BOX_X='130', BOX_Y='30', SKIP_UNSUPPORTED_FILTERS='1',
            VIEWPORT_CLIP='1', TRANSIENT_BUDGET_MB='1024', FEMTOVG_TEXT='glyphs')
files = {r['key']: r['path'] for r in json.load(open(os.path.expanduser('~/src/femtovg-wt/runs/zoom/files.json')))}
binp, key = sys.argv[1], sys.argv[2]
extra = dict(a.split('=',1) for a in sys.argv[3:])
env = dict(os.environ, **BASE, **extra)
load = lambda p: np.asarray(Image.open(p).convert('RGB')).astype(int)
d = tempfile.mkdtemp(dir=os.path.expanduser('~/src/femtovg-wt/runs/zoom/investigate/inv-glyph-v2'))
try:
    fresh = {}
    for z in sorted(set(LADDER)):
        subprocess.run([binp, str(z), f'{d}/f{z}.ppm', files[key]], env=env, capture_output=True, check=True)
        fresh[z] = load(f'{d}/f{z}.ppm')
    subprocess.run([binp, '1', f'{d}/l.ppm', files[key]], env=dict(env, ZOOM_LADDER=','.join(map(str, LADDER))), capture_output=True, check=True)
    out=[]
    for i, z in enumerate(LADDER):
        dd = np.abs(load(f'{d}/l.ppm.{i:02d}.ppm') - fresh[z]).max(axis=2)
        out.append(f"{z}:{int((dd>8).sum())}/{int(dd.max())}")
    print(key[-50:], extra, ' '.join(out))
finally:
    shutil.rmtree(d)
