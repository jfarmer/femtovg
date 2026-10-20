import sys, json, numpy as np
from PIL import Image
sys.path.insert(0, '/Users/matt/src/femtovg-wt/runs/busey/triage/new-five-r2/scripts')
from locate import S as FS
D = '/Users/matt/src/femtovg-wt/runs/busey/triage/new-five-r2-verify'; R = '/Users/matt/src/femtovg-wt/runs/busey'
L = lambda p: np.asarray(Image.open(p).convert('RGB'), dtype=np.int16)
cls = json.load(open('/Users/matt/src/femtovg-wt/runs/busey/triage/new-five-r2/classes.json'))
var, refsrc = sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else 'orig'
k = 'corpus__buseybench__claude-opus-5-5'
for fr in ('z2', 'hd'):
    o = L(f'{D}/png/mst4_{k}_{fr}.png'); v = L(f'{D}/png/mst4_t__{var}_{fr}.png')
    if refsrc == 'orig': rs = [L(f'{R}/refs/{b}_{k}_{fr}.png') for b in ('chr', 'ff', 'wk')]; idr = L(f'{R}/refs/id_{k}_{fr}.png')
    else: rs = [L(f'{D}/refs/{b}_t__{var}_{fr}.png') for b in ('chr', 'ff', 'wk')]; idr = L(f'{D}/refs/id_t__{var}_{fr}.png')
    a3 = lambda im: np.logical_and.reduce([np.abs(im - r).max(2) > 20 for r in rs])
    A, V = a3(o), a3(v)
    byc = {}
    for (x, y, c, ln) in cls[f'claude-opus-5-5_{fr}']['pixels']:
        byc.setdefault(c, []).append((x, y))
    det = ' '.join(f'{c}: {sum(V[y, x] for x, y in p)}/{len(p)}' for c, p in byc.items())
    print(f'{var} vs {refsrc} refs {fr}: all3 orig {A.sum()} -> variant {V.sum()} (gone {(A & ~V).sum()}, new {(V & ~A).sum()}); still red by class: {det}; pixels changed by variant {(np.abs(o - v).max(2) > 0).sum()}')
