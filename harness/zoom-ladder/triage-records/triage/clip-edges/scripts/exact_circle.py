# Exact coverage of a green rect clipped to a circle, composited on white, at the harness framing.
import sys, numpy as np, os
sys.path.insert(0, os.path.dirname(__file__))
from cmp import fem, ref, diff, FR
def coverage_circle(cx, cy, r, W=460, H=260, ss=32, bbox=None):
    cov = np.zeros((H, W))
    x0 = int(max(0, np.floor(cx - r - 1))); x1 = int(min(W, np.ceil(cx + r + 1)))
    y0 = int(max(0, np.floor(cy - r - 1))); y1 = int(min(H, np.ceil(cy + r + 1)))
    o = (np.arange(ss) + 0.5) / ss
    for y in range(y0, y1):
        ys = y + o
        xs = np.arange(x0, x1)[:, None] + o[None, :]  # (nx, ss)
        dy2 = (ys - cy) ** 2  # (ss,)
        inside = ((xs[:, :, None] - cx) ** 2 + dy2[None, None, :]) <= r * r
        cov[y, x0:x1] = inside.mean(axis=(1, 2))
    return cov
def framing(cx, cy, r, z, fit=1.0):
    X = 230 + z * (130 + fit * cx - 230); Y = 130 + z * (30 + fit * cy - 130)
    return X, Y, z * fit * r
def compose(cov, color=(0, 128, 0)):
    out = np.zeros(cov.shape + (3,))
    for i, c in enumerate(color):
        out[..., i] = 255 * (1 - cov) + c * cov
    return out
if __name__ == '__main__':
    key = sys.argv[1]; cx, cy, r = map(float, sys.argv[2:5])
    zs = [1, 1.25, 1.5, 1.75, 2, 3, 4, 0.75, 0.5, 0.33, 0.25]
    print('zoom  ' + ' '.join(f'{b:>14}' for b in ['fem', 'chr', 'ff', 'wk']) + '   (n>8 vs exact / mean |err| over edge px in 1/255)')
    for z in zs:
        X, Y, R = framing(cx, cy, r, z)
        ex = compose(coverage_circle(X, Y, R))
        edge = (np.abs(ex[..., 0] - 255) > 0.5) & (np.abs(ex[..., 0] - 0) > 0.5)
        row = []
        for b in ['fem', 'chr', 'ff', 'wk']:
            img = fem(key, z) if b == 'fem' else ref(b, key, z)
            if img is None: row.append('-'.rjust(14)); continue
            d = np.abs(img[..., :3] - ex).max(-1)
            row.append(f'{int((d > 8).sum()):5d} / {d[edge].mean():5.2f}'.rjust(14))
        print(f'{z:<5} ' + ' '.join(row))
