import json, os, subprocess, sys, tempfile, shutil
import numpy as np
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
BIN = os.path.abspath(os.environ.get('HBIN', 'bin/_logos_full_ig'))
LADDER = [1, 1.25, 1.5, 1.75, 2, 3, 4, 3, 2, 1.75, 1.5, 1.25, 1, 0.75, 0.5, 0.33, 0.25, 0.33, 0.5, 0.75, 1]
BASE = dict(FRAME_W='460', FRAME_H='260', BOX='200', BOX_X='130', BOX_Y='30', SKIP_UNSUPPORTED_FILTERS='1',
            VIEWPORT_CLIP='1', TRANSIENT_BUDGET_MB='1024', FEMTOVG_TEXT='glyphs')
CFGS = {'master': {}, 'grid': {'GLYPH_DEVICE_GRID': '1'}, 'gridsubpx': {'GLYPH_DEVICE_GRID': '1', 'GLYPH_SUBPIXEL_MASK': '1'}}
files = {r['key']: r['path'] for r in json.load(open(os.path.expanduser('~/src/femtovg-wt/runs/zoom/files.json')))}
keys = [l.strip() for l in open(sys.argv[1]) if l.strip()]
cfgs = sys.argv[2].split(',')
def load(p): return np.asarray(Image.open(p).convert('RGB')).astype(int)
def run(key, cfg):
    env = dict(os.environ, **BASE, **CFGS[cfg])
    d = tempfile.mkdtemp(dir=os.path.expanduser('~/src/femtovg-wt/runs/zoom/investigate/inv-glyph/tmp'))
    try:
        svg = files[key]
        fresh = {}
        for z in sorted(set(LADDER)):
            p = f'{d}/f{z}.ppm'
            subprocess.run([BIN, str(z), p, svg], env=env, capture_output=True, check=True)
            fresh[z] = load(p)
        e2 = dict(env, ZOOM_LADDER=','.join(map(str, LADDER)))
        subprocess.run([BIN, '1', f'{d}/l.ppm', svg], env=e2, capture_output=True, check=True)
        steps = []
        for i, z in enumerate(LADDER):
            dd = np.abs(load(f'{d}/l.ppm.{i:02d}.ppm') - fresh[z]).max(axis=2)
            steps.append(dict(zoom=z, any=int((dd > 0).sum()), n8=int((dd > 8).sum()), max=int(dd.max())))
        return dict(key=key, cfg=cfg, steps=steps)
    finally:
        shutil.rmtree(d)
os.makedirs('tmp', exist_ok=True)
jobs = [(k, c) for k in keys for c in cfgs]
with ThreadPoolExecutor(4) as ex, open(sys.argv[3], 'a') as out:
    for r in ex.map(lambda kc: run(*kc), jobs):
        out.write(json.dumps(r) + '\n'); out.flush()
        print(r['cfg'], r['key'], 'n8 total', sum(s['n8'] for s in r['steps']), 'max', max(s['max'] for s in r['steps']), flush=True)
