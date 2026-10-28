# Regression check of a patched harness binary against the master ladder frames:
# every file in zoomcmp_zm_svg.jsonl at the 11 ladder zooms, frames that move scored
# against each browser (pixels beyond 8/255, the ladder's own diff).
import json, os, subprocess, sys, numpy as np
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
HOME = os.path.expanduser('~')
RUN = f'{HOME}/src/femtovg-wt/runs/zoom'
OUT = f'{RUN}/triage/subpixel-sliver/reg'
BIN = f'{RUN}/triage/subpixel-sliver/bin/_logos_fix'
FIX = sys.argv[1] if len(sys.argv) > 1 else '2'
ZOOMS = [1, 1.25, 1.5, 1.75, 2, 3, 4, 0.75, 0.5, 0.33, 0.25]
STEP = {1: 0, 1.25: 1, 1.5: 2, 1.75: 3, 2: 4, 3: 5, 4: 6, 0.75: 13, 0.5: 14, 0.33: 15, 0.25: 16}
FR = {1: 'z1', 1.25: 'z125', 1.5: 'z15', 1.75: 'z175', 2: 'z2', 3: 'z3', 4: 'z4', 0.75: 'z075', 0.5: 'z05', 0.33: 'z033', 0.25: 'z025'}
ENV = {'FRAME_W': '460', 'FRAME_H': '260', 'BOX': '200', 'BOX_X': '130', 'BOX_Y': '30', 'SKIP_UNSUPPORTED_FILTERS': '1',
       'VIEWPORT_CLIP': '1', 'LAYER_STATS': '1', 'TRANSIENT_BUDGET_MB': '1024', 'FV_FIX': FIX}
paths = {f['key']: f['path'] for f in json.load(open(f'{RUN}/files.json'))}
keys = [json.loads(l)['key'] for l in open(f'{RUN}/zoomcmp_zm_svg.jsonl')]
def load(p): return np.asarray(Image.open(p).convert('RGB'), dtype=np.int16)
def n8(a, b): return int((np.abs(a - b).max(axis=2) > 8).sum())
def one(key):
    tmp = f'{OUT}/tmp/{abs(hash(key))}.ppm'
    r = subprocess.run([BIN, '1', tmp, paths[key]], env={**os.environ, **ENV, 'ZOOM_LADDER': ','.join(f'{z:g}' for z in ZOOMS)},
                       capture_output=True, text=True, timeout=600)
    rows = []
    for i, z in enumerate(ZOOMS):
        p = f'{tmp}.{i:02d}.ppm'
        mp = f'{RUN}/png/zl_zm_svg/{key}/{STEP[z]:02d}.png'
        if not os.path.exists(p) or not os.path.exists(mp):
            rows.append({'zoom': z, 'missing': True}); continue
        a, m = load(p), load(mp)
        os.remove(p)
        moved = int((np.abs(a - m).max(axis=2) > 0).sum())
        row = {'zoom': z, 'moved': moved}
        if moved:
            row['max'] = int(np.abs(a - m).max())
            for b in ['chr', 'ff', 'wk']:
                rp = f'{RUN}/fresh/refs/{b}_{key}_{FR[z]}.png'
                if os.path.exists(rp):
                    ref = load(rp)
                    row[b] = [n8(m, ref), n8(a, ref)]
            if moved > 0 and key.endswith('sliver-control') or key.endswith('sliver-control-ref'):
                Image.fromarray(a.astype(np.uint8)).save(f'{OUT}/{key}_{FR[z]}.png')
        rows.append(row)
    return {'key': key, 'rc': r.returncode, 'steps': rows}
with ThreadPoolExecutor(6) as ex, open(f'{OUT}/fix{FIX}.jsonl', 'w') as out:
    for i, res in enumerate(ex.map(one, keys)):
        out.write(json.dumps(res) + '\n'); out.flush()
        if i % 100 == 0: print(i, len(keys), flush=True)
