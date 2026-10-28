# ab.py: per file, base vs area build: fails vs best browser (>24 px beyond 8/255), px beyond 8 of the area ref, max err
import json, os, numpy as np
from PIL import Image
from cmp import ref, load, fem
H = os.path.expanduser('~'); T = f'{H}/src/femtovg-wt/runs/zoom/triage/clip-edges'
c = json.load(open(f'{H}/src/femtovg-wt/runs/zoom/triage/clusters_compact.json'))['clip-edges']
FR = {1: 'z1', 1.25: 'z125', 1.5: 'z15', 1.75: 'z175', 2: 'z2', 3: 'z3', 4: 'z4', 0.75: 'z075', 0.5: 'z05', 0.33: 'z033', 0.25: 'z025'}
n8 = lambda a, b: int((np.abs(a[..., :3] - b[..., :3]).max(-1) > 8).sum())
tot = {}
for f in c:
    k = f['key']; line = []; fails = {'base': [], 'area': [], 'area_ref_as_fem': []}
    sums = {'base': 0, 'area': 0}
    for z, fr in FR.items():
        a = load(f'{T}/area/id_{k}_{fr}.png')
        refs = [r for r in (ref(b, k, z) for b in ('chr', 'ff', 'wk')) if r is not None]
        for tag in ('base', 'area'):
            img = load(f'{T}/png/{tag}/{k}_{fr}.png')
            best = min(n8(img, r) for r in refs)
            if best > 24: fails[tag].append(z)
            sums[tag] += n8(img, a)
        if min(n8(a, r) for r in refs) > 24: fails['area_ref_as_fem'].append(z)
    # sanity: base == ladder fresh frames
    same = all(np.array_equal(load(f'{T}/png/base/{k}_{fr}.png')[..., :3], fem(k, z)[..., :3]) for z, fr in FR.items())
    print(f"{k.split('__')[-1][:38]:38} base==ladder:{same!s:5} px>8 of area: {sums['base']:5d} -> {sums['area']:5d} | zooms failing vs best browser: base {fails['base']}  area {fails['area']}  exact(area ref) itself {fails['area_ref_as_fem']}")
