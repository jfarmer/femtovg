# For every framing the patch moves: off and on against the area reference (Chromium at 8x DPR, box-downsampled).
import json, os, sys, numpy as np
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render
from PIL import Image
D = os.path.dirname(os.path.abspath(__file__)); R = '/Users/matt/src/femtovg-wt/runs/zoom'
paths = {f['key']: f['path'] for f in json.load(open(f'{R}/fresh/files.json'))}
Z = {'z1': 1, 'z125': 1.25, 'z15': 1.5, 'z175': 1.75, 'z2': 2, 'z3': 3, 'z4': 4, 'z075': 0.75, 'z05': 0.5, 'z033': 0.33, 'z025': 0.25}
B = f'{D}/bin/_logos_full_thin'
rows = [json.loads(l) for l in open(f'{D}/corpus_ab.jsonl')]
moved = [r for r in rows if not r.get('same', True)]
os.makedirs(f'{D}/area', exist_ok=True)
def L(p): return np.asarray(Image.open(p).convert('RGB'), dtype=np.int16)
def n(a, b): return int((np.abs(a - b).max(axis=2) > 8).sum())
def job(r):
    k, f = r['key'], r['framing']; z = Z[f]
    ap = f'{D}/area/area_{k}_{f}.png'
    html = f'{D}/area/{abs(hash((k, f)))}.html'
    if not os.path.exists(ap):
        render.page(paths[k], z, html); render.chrome(html, ap, 8); os.remove(html)
    off = f'{D}/area/off_{k}_{f}.png'; on = f'{D}/area/on_{k}_{f}.png'
    render.femtovg(B, paths[k], z, off); render.femtovg(B, paths[k], z, on, {'FEMTOVG_THIN_STROKE_EXACT': '1'})
    A = L(ap); o = L(off); p = L(on)
    out = {'key': k, 'framing': f, 'off_area': n(o, A), 'on_area': n(p, A)}
    for b in ['chr', 'ff', 'wk']:
        q = f'{R}/fresh/refs/{b}_{k}_{f}.png'
        if os.path.exists(q): out[f'{b}_area'] = n(L(q), A)
    os.remove(off); os.remove(on)
    return out
with ThreadPoolExecutor(4) as ex: res = list(ex.map(job, moved))
json.dump(res, open(f'{D}/area_ab.json', 'w'), indent=0)
c = {'closer': 0, 'further': 0, 'same': 0}
for x in res: c['closer' if x['on_area'] < x['off_area'] else 'further' if x['on_area'] > x['off_area'] else 'same'] += 1
print(c, 'sum off', sum(x['off_area'] for x in res), 'sum on', sum(x['on_area'] for x in res),
      'chr', sum(x.get('chr_area', 0) for x in res), 'wk', sum(x.get('wk_area', 0) for x in res))
for x in res:
    if x['on_area'] >= x['off_area']: print('  not closer:', x)
