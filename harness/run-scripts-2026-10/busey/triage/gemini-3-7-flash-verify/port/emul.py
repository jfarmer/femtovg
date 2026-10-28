# Emulates femtovg Path::dashed_with_tolerance (mst2 src/path.rs) in f32 for the iris circles,
# then writes the dashes (a) as femtovg's own output, one subpath per piece, and (b) one polyline per dash.
import os, re
import numpy as np
F = np.float32
S = os.path.dirname(os.path.abspath(__file__))
TESS, DIST = F(0.125), F(0.01)

def circle(cx, cy, r):
    k = {21: F(11.598), 16: F(8.83655)}[r]  # usvg's control-point offsets (PATH_DUMP)
    cx, cy, r = F(cx), F(cy), F(r)
    p = lambda x, y: (F(x), F(y))
    start = p(cx + r, cy)
    cubics = [
        (p(cx + r, cy + k), p(cx + k, cy + r), p(cx, cy + r)),
        (p(cx - k, cy + r), p(cx - r, cy + k), p(cx - r, cy)),
        (p(cx - r, cy - k), p(cx - k, cy - r), p(cx, cy - r)),
        (p(cx + k, cy - r), p(cx + r, cy - k), p(cx + r, cy)),
    ]
    return start, cubics

def push(pts, q):
    if pts:
        dx, dy = F(q[0] - pts[-1][0]), F(q[1] - pts[-1][1])
        if F(dx * dx + dy * dy) < F(DIST * DIST):
            return
    pts.append(q)

def mid(a, b):
    return (F(F(a[0] + b[0]) * F(0.5)), F(F(a[1] + b[1]) * F(0.5)))

def flat(pts, p0, p1, p2, p3, level):
    if level > 10:
        push(pts, p3); return
    p01, p12, p23 = mid(p0, p1), mid(p1, p2), mid(p2, p3)
    p012, p123 = mid(p01, p12), mid(p12, p23)
    p0123 = mid(p012, p123)
    dx, dy = F(p3[0] - p0[0]), F(p3[1] - p0[1])
    d1 = abs(F(F(F(p1[0] - p3[0]) * dy) - F(F(p1[1] - p3[1]) * dx)))
    d2 = abs(F(F(F(p2[0] - p3[0]) * dy) - F(F(p2[1] - p3[1]) * dx)))
    if F(F(d1 + d2) * F(d1 + d2)) < F(TESS * F(F(dx * dx) + F(dy * dy))):
        push(pts, p3); return
    flat(pts, p0, p01, p012, p0123, level + 1)
    flat(pts, p0123, p123, p23, p3, level + 1)

def contour(cx, cy, r):
    start, cubics = circle(cx, cy, r)
    pts = [start]; cur = start
    for c1, c2, e in cubics:
        flat(pts, cur, c1, c2, e, 0); cur = e
    return pts  # closed

def dash(pts, pattern):
    # returns a list of dashes, each a list of pieces (a, b) in femtovg's order
    idx, rem, drawing = 0, F(pattern[0]), True
    dashes, cur = [], None
    segs = list(zip(pts, pts[1:])) + [(pts[-1], pts[0])]
    for s, e in segs:
        ddx, ddy = F(e[0] - s[0]), F(e[1] - s[1])
        length = F(np.sqrt(F(F(ddx * ddx) + F(ddy * ddy))))
        if length <= DIST:
            continue
        inv = F(F(1.0) / length)
        dirx, diry = F(ddx * inv), F(ddy * inv)
        t = F(0.0)
        while t < length:
            if rem <= F(np.finfo(np.float32).eps):
                idx = (idx + 1) % len(pattern); rem = F(pattern[idx]); drawing = idx % 2 == 0
                cur = None
                continue
            step = min(rem, F(length - t))
            if drawing and step > DIST:
                a = (F(s[0] + F(dirx * t)), F(s[1] + F(diry * t)))
                b = (F(s[0] + F(dirx * F(t + step))), F(s[1] + F(diry * F(t + step))))
                if cur is None:
                    cur = []; dashes.append(cur)
                cur.append((a, b))
            t = F(t + step); rem = F(rem - step)
    return dashes

def fmt(v):
    return repr(float(v))

src = open('/Users/matt/src/femtovg-wt/da/corpus/buseybench/gemini-3-7-flash.svg').read()
pat = re.compile(r'<circle cx="(\d+)" cy="(\d+)" r="(\d+)" stroke="(#[0-9a-f]+)" stroke-width="1.5" stroke-dasharray="(\d),(\d)" fill="none"/>')
stats = []
def rep(mode):
    def f(m):
        cx, cy, r, col, on, off = m.groups()
        pts = contour(int(cx), int(cy), int(r))
        ds = dash(pts, [F(int(on)), F(int(off))])
        if mode == 'split':
            d = ' '.join(f'M{fmt(a[0])} {fmt(a[1])} L{fmt(b[0])} {fmt(b[1])}' for dd in ds for a, b in dd)
        else:
            d = ' '.join(f'M{fmt(dd[0][0][0])} {fmt(dd[0][0][1])} ' + ' '.join(f'L{fmt(b[0])} {fmt(b[1])}' for a, b in dd) for dd in ds)
        if mode == 'split':
            pieces = [p for dd in ds for p in dd]
            lens = [float(np.hypot(b[0] - a[0], b[1] - a[1])) for a, b in pieces]
            stats.append((r, on, off, len(pts), len(ds), sum(len(dd) > 1 for dd in ds), len(pieces),
                          sum(l * 0.390625 < 1.0 for l in lens)))
        return f'<path d="{d}" stroke="{col}" stroke-width="1.5" fill="none"/>'
    return f
open(f'{S}/svg/p04_emul_split.svg', 'w').write(pat.sub(rep('split'), src))
open(f'{S}/svg/p05_emul_joined.svg', 'w').write(pat.sub(rep('joined'), src))
print('r on off | contour pts | dashes | dashes split | pieces | pieces < 1 px at z2')
for s in stats:
    print(s)
