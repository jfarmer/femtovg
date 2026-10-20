"""attrib.py name fr [build=mst4] [pd=] [rd=] [svg=] [key=] [r=1.5] [dil=3]: red clusters with nearby SVG elements"""
import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from locate import elements, near, describe, to_svg, S
from off3 import masks
import off3
a = dict(x.split('=', 1) for x in sys.argv[1:] if '=' in x); p = [x for x in sys.argv[1:] if '=' not in x]
name, fr = p[0], p[1]
off3.fr = fr; off3.b = a.get('build', 'mst4'); off3.pd = a.get('pd', off3.pd); off3.rd = a.get('rd', off3.rd)
key = a.get('key', 'corpus__buseybench__' + name)
svg = a.get('svg', f'/Users/matt/src/femtovg-wt/da/corpus/buseybench/{name}.svg')
o, refs, all3, sp, offid = masks(key)
r = float(a.get('r', 1.5)); dl = int(a.get('dil', 3))
def dil(m, it):
    for _ in range(it): m = m | np.roll(m, 1, 0) | np.roll(m, -1, 0) | np.roll(m, 1, 1) | np.roll(m, -1, 1)
    return m
def label(m):
    lab = np.zeros(m.shape, int); n = 0
    for y, x in zip(*np.nonzero(m)):
        if lab[y, x]: continue
        n += 1; st = [(y, x)]; lab[y, x] = n
        while st:
            cy, cx = st.pop()
            for dy, dx in ((1,0),(-1,0),(0,1),(0,-1)):
                yy, xx = cy+dy, cx+dx
                if 0 <= yy < m.shape[0] and 0 <= xx < m.shape[1] and m[yy, xx] and not lab[yy, xx]:
                    lab[yy, xx] = n; st.append((yy, xx))
    return lab, n
lab, n = label(dil(all3, dl))
els = elements(svg)
rows = []
for i in range(1, n + 1):
    m = (lab == i) & all3
    ys, xs = np.nonzero(m)
    if not len(ys): continue
    cnt = {}
    for y, x in zip(ys, xs):
        u, v = to_svg(fr, x, y)
        for j, d in near(els, u, v, r / S[fr][2]): cnt[j] = cnt.get(j, 0) + 1
    rows.append((len(ys), int((m & ~sp).sum()), int((m & offid).sum()) if offid is not None else -1, xs.min(), ys.min(), xs.max(), ys.max(), cnt))
tot = all3.sum()
print(f'{name} {fr}: all3 {tot}')
for c, ag, oi, x0, y0, x1, y1, cnt in sorted(rows, key=lambda r: -r[0]):
    u0, v0 = to_svg(fr, x0, y0); u1, v1 = to_svg(fr, x1, y1)
    print(f'-- {c} px (agreed {ag}, off-area {oi}) frame x{x0}-{x1} y{y0}-{y1}  svg ({u0:.0f},{v0:.0f})-({u1:.0f},{v1:.0f})')
    for j in sorted(cnt, key=lambda j: -j)[:int(a.get('top', 6))]:
        print(f'     [{cnt[j]}/{c}]', describe(els[j])[:230])
