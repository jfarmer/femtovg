import json, os, sys, numpy as np
from PIL import Image
from cmp import fem, ref, load
H = os.path.expanduser('~')
c = json.load(open(f'{H}/src/femtovg-wt/runs/zoom/triage/clusters_compact.json'))['clip-edges']
FR = {1: 'z1', 1.25: 'z125', 1.5: 'z15', 1.75: 'z175', 2: 'z2', 3: 'z3', 4: 'z4', 0.75: 'z075', 0.5: 'z05', 0.33: 'z033', 0.25: 'z025'}
A = f'{H}/src/femtovg-wt/runs/zoom/triage/clip-edges/area'
def n8(a, b): return int((np.abs(a[..., :3] - b[..., :3]).max(-1) > 8).sum())
res = {}
for f in c:
    k = f['key']; badz = {b[0] for b in f['bad']}
    print(k.split('__')[-1], ' z1 best', f['z1'])
    print('   zoom  fem  chr   ff   wk | fem-vs-best  chr-vs-ff   (pixels beyond 8/255 of the area ref)')
    res[k] = {}
    for z, fr in FR.items():
        a = load(f'{A}/id_{k}_{fr}.png')
        F = fem(k, z); row = {'fem': n8(F, a)}
        for b in ('chr', 'ff', 'wk'):
            r = ref(b, k, z); row[b] = n8(r, a) if r is not None else None
        bs = [n8(F, ref(b, k, z)) for b in ('chr', 'ff', 'wk') if ref(b, k, z) is not None]
        cf = n8(ref('chr', k, z), ref('ff', k, z)) if ref('ff', k, z) is not None else None
        row['best'] = min(bs); row['cf'] = cf
        res[k][fr] = row
        fmt = lambda v: '   -' if v is None else f'{v:4d}'
        print(f'  {"*" if z in badz else " "}{z:<5}{fmt(row["fem"])} {fmt(row["chr"])} {fmt(row["ff"])} {fmt(row["wk"])} | {fmt(row["best"])}      {fmt(cf)}')
json.dump(res, open(f'{A}/../vs_area.json', 'w'), indent=1)
