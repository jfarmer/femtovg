import sys, json; sys.path.insert(0, '.')
from boxes import *
V = ['v01_no_lower_lip', 'v03_no_nose_cres', 'v04_no_iris_dashes', 'v05_iris_presplit', 'v06_caps_butt', 'v07_no_teeth_strokes', 'v08_crow_fill_none', 'v09_no_filters', 'v10_no_catchlights', 'v02_no_upper_lip']
out = {}
for fr in ('z2', 'hd'):
    R0 = refs('v00_orig', fr); o0 = ours('v00_orig', fr); a0, ag0, _ = red(o0, R0)
    fm = ours('v00_orig', fr, 'fm_'); afm, _, _ = red(fm, R0)
    gone = {}
    for v in V:
        a, _, _ = red(ours(v, fr), refs(v, fr)); gone[v] = a0 & ~a
        new = a & ~a0
        print(fr, f'{v:22s} removes {int(gone[v].sum()):4d} adds {int(new.sum()):3d}')
    gone['fm'] = a0 & ~afm
    ys, xs = np.nonzero(a0)
    rows = []
    for y, x in zip(ys, xs):
        rows.append(dict(x=int(x), y=int(y), agreed=bool(ag0[y, x]), gone=[k for k in gone if gone[k][y, x]]))
    out[fr] = rows
json.dump(out, open('assign.json', 'w'))
