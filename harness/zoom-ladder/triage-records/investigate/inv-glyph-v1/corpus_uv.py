# Ladder vs fresh per zoom for the 34 files, master vs a UV-only bias.
import json, os, subprocess, sys, tempfile, shutil
import numpy as np
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
BIN = os.path.abspath('bin/_logos_full_uvb')
LADDER = [1, 1.25, 1.5, 1.75, 2, 3, 4, 3, 2, 1.75, 1.5, 1.25, 1, 0.75, 0.5, 0.33, 0.25, 0.33, 0.5, 0.75, 1]
BASE = dict(FRAME_W='460', FRAME_H='260', BOX='200', BOX_X='130', BOX_Y='30', SKIP_UNSUPPORTED_FILTERS='1',
            VIEWPORT_CLIP='1', TRANSIENT_BUDGET_MB='1024', FEMTOVG_TEXT='glyphs')
CFGS = {'master': {}, 'uvp': {'GLYPH_UV_BIAS': '0.25,0.25'}, 'uvm': {'GLYPH_UV_BIAS': '-0.25,-0.25'}, 'uvp3': {'GLYPH_UV_BIAS': '0.3,0.3'}}
files = {r['key']: r['path'] for r in json.load(open(os.path.expanduser('~/src/femtovg-wt/runs/zoom/files.json')))}
keys = [l.strip() for l in open(sys.argv[1]) if l.strip()]
cfgs = sys.argv[2].split(',')
TMP = os.path.abspath('tmp'); os.makedirs(TMP, exist_ok=True)
def load(p): return np.asarray(Image.open(p).convert('RGB')).astype(int)
def run(key, cfg):
    env = dict(os.environ, **BASE, **CFGS[cfg])
    d = tempfile.mkdtemp(dir=TMP)
    try:
        svg = files[key]; fresh = {}
        for z in sorted(set(LADDER)):
            p = f'{d}/f{z}.ppm'
            subprocess.run([BIN, str(z), p, svg], env=env, capture_output=True, check=True)
            fresh[z] = load(p)
        subprocess.run([BIN, '1', f'{d}/l.ppm', svg], env=dict(env, ZOOM_LADDER=','.join(map(str, LADDER))), capture_output=True, check=True)
        steps = []
        for i, z in enumerate(LADDER):
            dd = np.abs(load(f'{d}/l.ppm.{i:02d}.ppm') - fresh[z]).max(axis=2)
            steps.append(dict(zoom=z, any=int((dd > 0).sum()), n8=int((dd > 8).sum()), max=int(dd.max())))
        return dict(key=key, cfg=cfg, steps=steps)
    finally:
        shutil.rmtree(d)
jobs = [(k, c) for k in keys for c in cfgs]
with ThreadPoolExecutor(4) as ex, open(sys.argv[3], 'w') as out:
    for r in ex.map(lambda kc: run(*kc), jobs):
        out.write(json.dumps(r) + '\n'); out.flush()
