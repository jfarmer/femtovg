import json, numpy as np, math
from PIL import Image
from geom import *
D = '/Users/matt/src/femtovg-wt/runs/busey/triage/new-five-r2-verify'
def orient(P):
    P = np.asarray(P, float); a = 0.5 * np.sum(P[:, 0] * np.roll(P[:, 1], -1) - np.roll(P[:, 0], -1) * P[:, 1]); return P if a > 0 else P[::-1]
def stroke_polys(pts, w, limit=10.0, cap='butt'):
    """butt-capped polyline stroke with miter joins as a union of polygons (device space)."""
    pts = np.asarray(pts, float); h = w / 2; polys = []
    for a, b in zip(pts[:-1], pts[1:]):
        d = (b - a) / np.linalg.norm(b - a); n = np.array([-d[1], d[0]]) * h
        polys.append(orient([a + n, b + n, b - n, a - n]))
    for i in range(1, len(pts) - 1):
        V = pts[i]; d1 = (V - pts[i - 1]); d1 /= np.linalg.norm(d1); d2 = pts[i + 1] - V; d2 /= np.linalg.norm(d2)
        n1 = np.array([-d1[1], d1[0]]); n2 = np.array([-d2[1], d2[0]])
        sg = -1 if (d1[0] * d2[1] - d1[1] * d2[0]) > 0 else 1
        o1, o2 = V + sg * n1 * h, V + sg * n2 * h; bis = sg * (n1 + n2); bis /= np.linalg.norm(bis); ch = (sg * n1) @ bis
        if 1 / ch <= limit: polys.append(orient([V, o1, V + bis * h / ch, o2]))
        else: polys.append(orient([V, o1, o2]))
    return polys
if __name__ == '__main__':
    recs = json.load(open(f'{D}/svg/geo.json'))['v_miter']
    f = np.asarray(Image.open(f'{D}/png/mst4_t__v_miter_hd.png').convert('L'), float) / 255
    print(' A(deg) w(px) | px>20/255 near join (r<w*ratio+2) | min err  max err | join-window ink/area')
    for r in recs:
        polys = stroke_polys(r['pts'], r['w']); V = np.array(r['pts'][1]); ratio = 1 / math.sin(math.radians(r['A'] / 2))
        R = r['w'] / 2 * ratio + 2.5; x0, y0 = np.floor(V - R).astype(int); x1, y1 = np.ceil(V + R).astype(int)
        cov = coverage(x0, y0, x1, y1, lambda X, Y: inside_polys(X, Y, polys), ss=24)
        e = f[y0:y1, x0:x1] - cov
        Yc, Xc = np.mgrid[y0:y1, x0:x1] + 0.5; m = np.hypot(Xc - V[0], Yc - V[1]) < R
        print(f'{r["A"]:6d} {r["w"]:5.1f} | {int((np.abs(e[m]) > 20 / 255).sum()):4d} | {e[m].min():+.3f} {e[m].max():+.3f} | {f[y0:y1, x0:x1][m].sum() / cov[m].sum():.3f}')
