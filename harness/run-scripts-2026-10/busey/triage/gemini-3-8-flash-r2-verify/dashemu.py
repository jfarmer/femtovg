"""Emulate femtovg's dasher on the iris circles: usvg's four cubic arcs, flattened in path units (tess_tol 0.125,
dist_tol 0.01) as flattened_contours does, dashed chord by chord. Writes the pieces either as femtovg emits them
(one M-L subpath per piece) or joined (one polyline per dash), into portrait variants."""
import math, json
K = 0.5522847498
def circle_cubics(cx, cy, r):
    pts = [(cx + r, cy), (cx, cy + r), (cx - r, cy), (cx, cy - r), (cx + r, cy)]
    out = []
    for i in range(4):
        (x0, y0), (x3, y3) = pts[i], pts[i + 1]
        # tangent directions for clockwise (y-down) travel
        t0 = (-(y0 - cy) / r, (x0 - cx) / r); t3 = (-(y3 - cy) / r, (x3 - cx) / r)
        out.append(((x0, y0), (x0 + K * r * t0[0], y0 + K * r * t0[1]), (x3 - K * r * t3[0], y3 - K * r * t3[1]), (x3, y3)))
    return out
def flat(p0, p1, p2, p3, pts, level=0, tol=0.125, dist=0.01):
    if level > 10: return
    p01 = ((p0[0]+p1[0])/2, (p0[1]+p1[1])/2); p12 = ((p1[0]+p2[0])/2, (p1[1]+p2[1])/2); p23 = ((p2[0]+p3[0])/2, (p2[1]+p3[1])/2)
    p012 = ((p01[0]+p12[0])/2, (p01[1]+p12[1])/2); p123 = ((p12[0]+p23[0])/2, (p12[1]+p23[1])/2); p0123 = ((p012[0]+p123[0])/2, (p012[1]+p123[1])/2)
    dx = p3[0]-p0[0]; dy = p3[1]-p0[1]
    d1 = abs((p1[0]-p3[0])*dy - (p1[1]-p3[1])*dx); d2 = abs((p2[0]-p3[0])*dy - (p2[1]-p3[1])*dx)
    if (d1+d2)**2 < tol*(dx*dx+dy*dy):
        if math.hypot(p3[0]-pts[-1][0], p3[1]-pts[-1][1]) > dist: pts.append(p3)
        return
    flat(p0, p01, p012, p0123, pts, level+1, tol, dist); flat(p0123, p123, p23, p3, pts, level+1, tol, dist)
def dashes(cx, cy, r, on, off):
    pts = [(cx + r, cy)]
    for c in circle_cubics(cx, cy, r): flat(*c, pts)
    if math.hypot(pts[-1][0]-pts[0][0], pts[-1][1]-pts[0][1]) < 0.01: pts.pop()
    pts.append(pts[0])  # closed
    pieces = []; dash = []; drawing = True; remaining = on; pat = [on, off]; idx = 0
    for a, b in zip(pts[:-1], pts[1:]):
        L = math.hypot(b[0]-a[0], b[1]-a[1]); ux, uy = (b[0]-a[0])/L, (b[1]-a[1])/L; tr = 0
        while tr < L:
            if remaining <= 1e-7:
                idx = (idx + 1) % 2; drawing = idx == 0; remaining = pat[idx]
                if drawing: dash = []
                continue
            step = min(remaining, L - tr)
            if drawing and step > 0.01:
                s = (a[0]+ux*tr, a[1]+uy*tr); e = (a[0]+ux*(tr+step), a[1]+uy*(tr+step))
                pieces.append((s, e))
                if dash and math.hypot(dash[-1][0]-s[0], dash[-1][1]-s[1]) < 1e-6: dash.append(e)
                else:
                    dash = [s, e]
                    pieces_j.append(dash)
            tr += step; remaining -= step
    return pts, pieces
pieces_j = []
def svgpath(lst, stroke):
    return f'      <path d="{lst}" fill="none" stroke="{stroke}" stroke-width="1.5" opacity="0.8"/>'
if __name__ == '__main__':
    import sys; sys.path.insert(0, '.')
    exec(open('mkvar.py').read().split("names = []")[0])
    rep_split = {}; rep_join = {}
    for ln, (cx, cy, r) in {277: (423, 452, 15), 312: (600, 448, 14.5)}.items():
        pieces_j.clear()
        pts, pieces = dashes(cx, cy, r, 2, 3)
        print(ln, 'chords', len(pts) - 1, 'pieces', len(pieces), 'dashes', len(pieces_j), 'split dashes', sum(1 for d in pieces_j if len(d) > 2))
        rep_split[ln] = svgpath(' '.join(f'M {s[0]:.5f},{s[1]:.5f} L {e[0]:.5f},{e[1]:.5f}' for s, e in pieces), '#9ee5ff')
        rep_join[ln] = svgpath(' '.join('M ' + ' L '.join(f'{x:.5f},{y:.5f}' for x, y in d) for d in pieces_j), '#9ee5ff')
    n1 = var('v15_iris_emul_split', repl=rep_split); n2 = var('v16_iris_emul_joined', repl=rep_join)
    fs = json.load(open('files.json'))
    for n in (n1, n2): fs.append({'path': f'{HERE}/svg/{n}.svg', 'key': f't__{n}', 'group': 'd'})
    json.dump(fs, open('files.json', 'w'))
