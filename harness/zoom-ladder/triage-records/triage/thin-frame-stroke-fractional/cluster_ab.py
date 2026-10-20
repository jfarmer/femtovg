# Render every cluster file at every ladder zoom with the patched binary, on and off, and count n8 per browser.
import json, os, subprocess, sys, numpy as np
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
H = os.path.expanduser('~'); R = f'{H}/src/femtovg-wt/runs/zoom'; D = f'{R}/triage/thin-frame-stroke-fractional'
sys.path.insert(0, D); from split import ring
B = f'{D}/bin/_logos_full_thin'
ENV = {**os.environ, 'FRAME_W': '460', 'FRAME_H': '260', 'BOX': '200', 'BOX_X': '130', 'BOX_Y': '30', 'SKIP_UNSUPPORTED_FILTERS': '1', 'VIEWPORT_CLIP': '1', 'TRANSIENT_BUDGET_MB': '1024'}
FR = {1: 'z1', 1.25: 'z125', 1.5: 'z15', 1.75: 'z175', 2: 'z2', 3: 'z3', 4: 'z4', 0.75: 'z075', 0.5: 'z05', 0.33: 'z033', 0.25: 'z025'}
def load(p): return np.asarray(Image.open(p).convert('RGB'), dtype=np.int16)
def render(job):
    key, path, z, mode = job
    out = f'{D}/ab/{mode}/{key}_{FR[z]}.png'
    if os.path.exists(out): return
    os.makedirs(os.path.dirname(out), exist_ok=True)
    ppm = out[:-4] + '.ppm'
    env = {**ENV, **({'FEMTOVG_THIN_STROKE_EXACT': '1'} if mode == 'thin' else {})}
    subprocess.run([B, f'{z:g}', ppm, f'{H}/{path}'], env=env, capture_output=True, timeout=300)
    Image.open(ppm).convert('RGB').save(out); os.remove(ppm)
files = json.load(open(f'{R}/triage/clusters_compact.json'))[sys.argv[1] if len(sys.argv) > 1 else 'thin-frame-stroke-fractional']
jobs = [(e['key'], e['path'], z, m) for e in files for z in FR for m in ['off', 'thin']]
with ThreadPoolExecutor(6) as ex: list(ex.map(render, jobs))
res = {}
for e in files:
    k = e['key']; res[k] = {}
    for z in FR:
        row = {}
        for m in ['off', 'thin']:
            a = load(f'{D}/ab/{m}/{k}_{FR[z]}.png')
            for br in ['chr', 'ff', 'wk']:
                p = f'{R}/fresh/refs/{br}_{k}_{FR[z]}.png'
                if os.path.exists(p): row[f'{m}_{br}'] = int((np.abs(a - load(p)).max(axis=2) > 8).sum())
        res[k][FR[z]] = row
json.dump(res, open(f'{D}/cluster_ab.json', 'w'), indent=1)
for k, zs in res.items():
    print(k)
    for z, row in zs.items():
        off = min([v for kk, v in row.items() if kk.startswith('off_')], default=None)
        thin = min([v for kk, v in row.items() if kk.startswith('thin_')], default=None)
        flag = ' FAIL' if (thin or 0) > 24 else ''
        if (off or 0) > 24 or (thin or 0) > 24:
            print(f'  {z:5} best off={off} thin={thin}{flag}  ' + ' '.join(f'{kk}={v}' for kk, v in row.items()))
