import sys, numpy as np, math
from PIL import Image
from geom import *
D = '/Users/matt/src/femtovg-wt/runs/busey/triage/new-five-r2-verify'
pts = np.array([(404, 918), (358, 924), (452, 1020)], float); W = 1.5; pat = [5, 4]; off = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
fr = sys.argv[1] if len(sys.argv) > 1 else 'hd'
def orient(P):
    P = np.asarray(P); a = 0.5 * np.sum(P[:, 0] * np.roll(P[:, 1], -1) - np.roll(P[:, 0], -1) * P[:, 1]); return P if a > 0 else P[::-1]
segs = [(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]; lens = [np.linalg.norm(b - a) for a, b in segs]; cum = np.concatenate([[0], np.cumsum(lens)])
def at(s):
    i = min(np.searchsorted(cum, s, side='right') - 1, len(segs) - 1); a, b = segs[i]; return a + (b - a) / lens[i] * (s - cum[i]), i
def rect(p, q):
    d = (q - p) / np.linalg.norm(q - p); n = np.array([-d[1], d[0]]) * W / 2; return orient([p + n, q + n, q - n, p - n])
polys = []
period = sum(pat); s = -(off % period)
while s < cum[-1]:
    a, b = max(s, 0), min(s + pat[0], cum[-1])
    if b > a:
        pa, ia = at(a); pb, ib = at(b - 1e-9)
        if ia == ib: polys.append(rect(pa, pb))
        else:
            V = pts[1]; polys.append(rect(pa, V)); polys.append(rect(V, pb))
            d1 = (V - pa) / np.linalg.norm(V - pa); d2 = (pb - V) / np.linalg.norm(pb - V)
            n1 = np.array([-d1[1], d1[0]]); n2 = np.array([-d2[1], d2[0]])
            sgn = -1 if (d1[0] * d2[1] - d1[1] * d2[0]) > 0 else 1   # outer side
            o1 = V + sgn * n1 * W / 2; o2 = V + sgn * n2 * W / 2
            bis = (sgn * n1 + sgn * n2); bis /= np.linalg.norm(bis); cos_half = (sgn * n1) @ bis
            tip = V + bis * (W / 2) / cos_half
            print('miter ratio', 1 / cos_half, 'tip', tip)
            polys.append(orient([V, o1, tip, o2]))
    s += period
ox, oy, sc = FS[fr]
dpolys = [np.column_stack([ox + P[:, 0] * sc, oy + P[:, 1] * sc]) for P in polys]
allp = np.vstack(dpolys); x0, y0 = np.floor(allp.min(0)).astype(int) - 2; x1, y1 = np.ceil(allp.max(0)).astype(int) + 2
cov = coverage(x0, y0, x1, y1, lambda X, Y: inside_polys(X, Y, dpolys), ss=24)
for b in ['mst4']:
    key = 'v_dash' if off == 0 else 'v_dash_gap'
    f = np.asarray(Image.open(f'{D}/png/{b}_t__{key}_{fr}.png').convert('L'), float)[y0:y1, x0:x1] / 255
    e = f - cov; V = pts[1]; vx, vy = ox + V[0] * sc, oy + V[1] * sc
    Yc, Xc = np.mgrid[y0:y1, x0:x1] + 0.5; near = np.hypot(Xc - vx, Yc - vy) < 2.5
    print(fr, key, 'px>20/255 off analytic:', (np.abs(e) > 20 / 255).sum(), ' near vertex:', (near & (np.abs(e) > 20 / 255)).sum(), ' ink near vertex femtovg/area: %.3f' % (f[near].sum() / cov[near].sum()))
    for yy, xx in zip(*np.nonzero(np.abs(e) > 20 / 255)):
        print(f'   ({xx + x0},{yy + y0}) f={f[yy, xx]:.2f} area={cov[yy, xx]:.2f} dist_to_vertex={math.hypot(xx + x0 + .5 - vx, yy + y0 + .5 - vy):.2f}')
np.save(f'{D}/c/dash_cov_{fr}_{off}.npy', np.array([x0, y0, x1, y1]))
