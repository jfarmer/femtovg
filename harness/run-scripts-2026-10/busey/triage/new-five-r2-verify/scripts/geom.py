import numpy as np, math
FS = {'z2': (30.0, -70.0, 0.390625), 'hd': (420.0, 0.0, 1080 / 1024)}
def dev(fr, u, v):
    ox, oy, s = FS[fr]; return ox + u * s, oy + v * s
def svgc(fr, x, y):
    ox, oy, s = FS[fr]; return (x - ox) / s, (y - oy) / s
def samples(x0, y0, x1, y1, ss):
    xs = x0 + (np.arange((x1 - x0) * ss) + 0.5) / ss
    ys = y0 + (np.arange((y1 - y0) * ss) + 0.5) / ss
    return np.meshgrid(xs, ys)
def inside_polys(X, Y, polys, rule='nonzero'):
    """polys: list of (N,2) device-space closed rings. Winding-number test, vectorized."""
    w = np.zeros(X.shape, np.int32)
    for P in polys:
        P = np.asarray(P, float); Q = np.roll(P, -1, 0)
        for (ax, ay), (bx, by) in zip(P, Q):
            if ay == by: continue
            up = (ay <= Y) & (by > Y); dn = (by <= Y) & (ay > Y)
            t = (Y - ay) / (by - ay); xi = ax + t * (bx - ax)
            left = X < xi
            w += (up & left).astype(np.int32); w -= (dn & left).astype(np.int32)
    return (w != 0) if rule == 'nonzero' else (w % 2 != 0)
def coverage(x0, y0, x1, y1, fn, ss=32):
    X, Y = samples(x0, y0, x1, y1, ss)
    m = fn(X, Y).astype(np.float64)
    h, w = y1 - y0, x1 - x0
    return m.reshape(h, ss, w, ss).mean((1, 3))
def cubic(p0, p1, p2, p3, n=64):
    t = np.linspace(0, 1, n + 1)[:, None]; s = 1 - t
    return s**3 * p0 + 3 * s * s * t * p1 + 3 * s * t * t * p2 + t**3 * p3
def seg_dist(X, Y, a, b):
    a = np.asarray(a, float); b = np.asarray(b, float); d = b - a; L2 = d @ d
    t = np.clip(((X - a[0]) * d[0] + (Y - a[1]) * d[1]) / L2, 0, 1)
    return np.hypot(X - (a[0] + t * d[0]), Y - (a[1] + t * d[1]))
def pil_cov(polys_dev, W, H, ss=8):
    from PIL import Image, ImageDraw
    im = Image.new('L', (W * ss, H * ss), 0); dr = ImageDraw.Draw(im)
    for P in polys_dev:
        dr.polygon([(float(x * ss - 0.5), float(y * ss - 0.5)) for x, y in P], fill=255)
    a = np.asarray(im, float) / 255
    return a.reshape(H, ss, W, ss).mean((1, 3))
