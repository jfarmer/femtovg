"""dashfix.py: opus with the two dashed seam polylines (L229/L230) pre-dashed by hand: one subpath per dash, the dash that
crosses the vertex kept as one subpath through it (what a dasher that keeps joins would emit). No dasharray left."""
import numpy as np
SRC = '/Users/matt/src/femtovg-wt/da/corpus/buseybench/claude-opus-5-5.svg'
D = '/Users/matt/src/femtovg-wt/runs/busey/triage/new-five-r2-verify'
def predash(pts, on=5, off=4, keep_join=True):
    pts = np.array(pts, float); segs = list(zip(pts[:-1], pts[1:])); lens = [np.linalg.norm(b - a) for a, b in segs]; cum = np.concatenate([[0], np.cumsum(lens)])
    def at(s):
        i = min(np.searchsorted(cum, s, side='right') - 1, len(segs) - 1); a, b = segs[i]; return a + (b - a) / lens[i] * (s - cum[i]), i
    sub = []; s = 0.0
    while s < cum[-1]:
        a, b = s, min(s + on, cum[-1]); pa, ia = at(a); pb, ib = at(b - 1e-9 if b == cum[-1] else b)
        if ia == ib: sub.append(f'M {pa[0]:.4f} {pa[1]:.4f} L {pb[0]:.4f} {pb[1]:.4f}')
        elif keep_join: sub.append(f'M {pa[0]:.4f} {pa[1]:.4f} L {pts[ia + 1][0]:g} {pts[ia + 1][1]:g} L {pb[0]:.4f} {pb[1]:.4f}')
        else: sub.append(f'M {pa[0]:.4f} {pa[1]:.4f} L {pts[ia + 1][0]:g} {pts[ia + 1][1]:g} M {pts[ia + 1][0]:g} {pts[ia + 1][1]:g} L {pb[0]:.4f} {pb[1]:.4f}')
        s += on + off
    return ' '.join(sub)
ls = open(SRC).read().split('\n')
for keep, name in ((True, 'o_v_dashjoin'), (False, 'o_v_dashsplit')):
    out = list(ls)
    for ln, pts in ((229, [(404, 918), (358, 924), (452, 1020)]), (230, [(620, 918), (666, 924), (572, 1020)])):
        assert 'stroke-dasharray="5 4"' in out[ln - 1]
        out[ln - 1] = f'  <path d="{predash(pts, keep_join=keep)}" fill="none" stroke="#c9a86a" stroke-width="1.5" opacity="0.8"/>'
    open(f'{D}/svg/{name}.svg', 'w').write('\n'.join(out))
print('ok')
