#!/usr/bin/env python3
"""Replays femtovg's concave fill on WGPU in software, from the vertices and commands the library itself emits, to
tell which pass puts down the extra ink at a sliver's tip.

  CAP=path/to/cap fringe_model.py RUN

CAP is cap/ here built against a femtovg checkout with void-dump.patch applied: it fills one path with the z2
transform on the Void renderer, which then prints every vertex (x y u v) and every command. The patch also lets
FV_NO_INNERBEVEL=1 skip setting PointFlags::INNERBEVEL in calculate_joins, which leaves a sharp point's fringe
mitered (expand_fill bevels a point's strip only when it has both BEVEL and INNERBEVEL). RUN holds the frames
render.py wrote (png/red/master_<name>_z2.png) and the area references (refs/id_ct__<name>_z2.png).

The passes, as src/renderer/wgpu.rs concave_fill draws them: the fill fan into the stencil (+1 front, -1 back);
then each contour's fringe strip, back faces culled, where the stencil is 0, blended and not written to the
stencil, with alpha min(1, 1 - |2u - 1|) * min(1, v) (shader.wgsl strokeMask); then the cover quad where the
stencil is not 0. One sample per pixel, at its centre."""
import os, re, subprocess, sys
import numpy as np
from PIL import Image

CAP = os.environ.get('CAP', 'cap/target/release/cap')
RUN = sys.argv[1] if len(sys.argv) > 1 else '.'
W, H = 460, 260
yy, xx = np.mgrid[0:H, 0:W]
PX, PY = xx + 0.5, yy + 0.5


def capture(d, zoom=2, env=None):
    out = subprocess.run([CAP, str(zoom), d], capture_output=True, text=True, check=True,
                         env={**os.environ, **(env or {})}).stdout
    lines = out.splitlines()
    n = int(lines[0].split()[1])
    V = np.array([[float(t) for t in l.split()] for l in lines[1:1 + n]])
    fill = [l for l in lines[1 + n:] if l.startswith('CMD') and 'ConcaveFill' in l]
    assert len(fill) == 1, 'expected one concave fill'
    c = fill[0]
    dr = re.findall(r'fill_verts: (?:Some\(\((\d+), (\d+)\)\)|None), stroke_verts: (?:Some\(\((\d+), (\d+)\)\)|None)', c)
    tv = re.search(r'triangles_verts: Some\(\((\d+), (\d+)\)\)', c)
    return V, [tuple(int(x) if x else None for x in t) for t in dr], tuple(map(int, tv.groups()))


def raster(a, b, c):
    """Pixel centres inside triangle abc: the box, the mask, the signed area and the barycentrics."""
    area = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    if area == 0:
        return None
    x0 = int(max(0, np.floor(min(a[0], b[0], c[0])))); x1 = int(min(W, np.ceil(max(a[0], b[0], c[0])) + 1))
    y0 = int(max(0, np.floor(min(a[1], b[1], c[1])))); y1 = int(min(H, np.ceil(max(a[1], b[1], c[1])) + 1))
    if x0 >= x1 or y0 >= y1:
        return None
    px, py = PX[y0:y1, x0:x1], PY[y0:y1, x0:x1]
    w0 = ((b[0] - px) * (c[1] - py) - (b[1] - py) * (c[0] - px)) / area
    w1 = ((c[0] - px) * (a[1] - py) - (c[1] - py) * (a[0] - px)) / area
    w2 = 1 - w0 - w1
    return (y0, y1, x0, x1), (w0 >= 0) & (w1 >= 0) & (w2 >= 0), area, (w0, w1, w2)


def stencil(V, dr):
    st = np.zeros((H, W), int)
    for f0, fn, _, _ in dr:
        for i in range(f0 + 1, f0 + fn - 1):
            r = raster(V[f0], V[i], V[i + 1])
            if r:
                (y0, y1, x0, x1), m, area, _ = r
                st[y0:y1, x0:x1] += np.where(m, 1 if area > 0 else -1, 0)
    return st


def strip_layers(V, dr, st):
    """Each front-facing fringe triangle: its box, its alpha where the stencil lets it through, and its u = 1
    (outside) vertices, which lie half a pixel outside the edge the triangle antialiases."""
    out = []
    for _, _, s0, sn in dr:
        for k in range(sn - 2):
            a, b, c = V[s0 + k], V[s0 + k + 1], V[s0 + k + 2]
            r = raster(a, b, c)
            if r is None:
                continue
            (y0, y1, x0, x1), m, area, (w0, w1, w2) = r
            if area * (1 if k % 2 == 0 else -1) > 0:  # a strip flips every other triangle; back faces are culled
                continue
            u = w0 * a[2] + w1 * b[2] + w2 * c[2]
            v = w0 * a[3] + w1 * b[3] + w2 * c[3]
            al = np.clip(np.minimum(1, 1 - np.abs(2 * u - 1)) * np.minimum(1, v), 0, 1)
            out.append(((y0, y1, x0, x1), np.where(m & (st[y0:y1, x0:x1] == 0), al, 0), u,
                        [p for p in (a, b, c) if p[2] == 1.0]))
    return out


def compose(layers, st, cover_alpha=1.0, blend='over', inner=True):
    """Coverage the three passes leave. blend='max' merges overlapping strip triangles by their largest alpha (each
    pixel blended once); inner=False drops each ramp's part more than half a pixel inside its edge (u < 0.5)."""
    fr = np.zeros((H, W))
    for (y0, y1, x0, x1), al, u, _ in layers:
        if not inner:
            al = np.where(u < 0.5, 0, al)
        sub = fr[y0:y1, x0:x1]
        fr[y0:y1, x0:x1] = np.maximum(sub, al) if blend == 'max' else 1 - (1 - sub) * (1 - al)
    return np.where(st != 0, cover_alpha, fr)


def load_cov(p):
    return (255.0 - np.asarray(Image.open(p).convert('RGB'), dtype=np.float64).mean(axis=2)) / 255.0


def window(cx, cy, r=14):
    x, y = int(np.floor(cx)), int(np.floor(cy))
    return (slice(y - r, y + r), slice(x - r, x + r))


def z2(u, v):
    return np.array([0.390625 * u + 30, 0.390625 * v - 70])


def inside(poly, pts):
    """Even-odd point in polygon."""
    x, y = pts[:, 0], pts[:, 1]
    res = np.zeros(len(pts), bool)
    for (x1, y1), (x2, y2) in zip(poly, np.roll(poly, -1, 0)):
        c = ((y1 > y) != (y2 > y)) & (x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-30) + x1)
        res ^= c
    return res


def flatten(d, n=64):
    """The outline as a dense polygon in frame pixels, each segment in n pieces."""
    t = d.replace(',', ' ').split()
    pts, i, cur = [], 0, None
    while i < len(t):
        if t[i] == 'M':
            cur = np.array([float(t[i + 1]), float(t[i + 2])]); pts.append(cur); i += 3
        elif t[i] == 'L':
            to = np.array([float(t[i + 1]), float(t[i + 2])])
            pts += [cur + s * (to - cur) for s in np.linspace(0, 1, n + 1)[1:]]
            cur = to; i += 3
        elif t[i] == 'C':
            p1, p2, p3 = (np.array([float(t[i + j]), float(t[i + j + 1])]) for j in (1, 3, 5))
            for s in np.linspace(0, 1, n + 1)[1:]:
                pts.append((1 - s) ** 3 * cur + 3 * (1 - s) ** 2 * s * p1 + 3 * (1 - s) * s * s * p2 + s ** 3 * p3)
            cur = p3; i += 7
        else:
            i += 1
    return np.array([z2(*p) for p in pts])


# Each reduction, its tips' bisectors (the sum of the two edges' unit directions at the left tip, in svg units).
SHAPES = {
    'wedge': ((232, 116), (232, 86)),
    'wedge-split': ((232, 116), (232, 86)),
    'lip': ((64, 155), (64, 115)),
}
TIPS = [z2(280, 725), z2(744, 725)]

for name, (e1, e2) in SHAPES.items():
    d = re.search(r'<path d="([^"]*)"', open(f'{os.path.dirname(os.path.abspath(__file__))}/{name}.svg').read()).group(1)
    V, dr, tv = capture(d.replace(',', ' '))
    st = stencil(V, dr)
    layers = strip_layers(V, dr, st)
    cov = compose(layers, st)
    fv = load_cov(f'{RUN}/png/red/master_{name}_z2.png')
    area = load_cov(f'{RUN}/refs/id_ct__{name}_z2.png')
    wins = [window(*t) for t in TIPS]
    tipsum = lambda a: sum(a[w].sum() for w in wins)
    ex = cov - area
    fan = V[dr[0][0]:dr[0][0] + dr[0][1], :2]
    print(f'== {name}: model vs the 06243b80 frame, largest difference {255 * np.abs(cov - fv).max():.2f}/255')
    print(f'   fill fan: nearest vertex to the left tip {np.hypot(*(fan - TIPS[0]).T).min():.1f} px back from it')
    print(f'   tip windows: ink {tipsum(cov):.1f} against the area {tipsum(area):.1f}: excess {tipsum(ex):+.1f} = '
          f'cover (stencil != 0) {tipsum(np.where(st != 0, ex, 0)):+.1f} + fringe (stencil 0) {tipsum(np.where(st == 0, ex, 0)):+.1f}')
    over = np.abs(cov - area) > 20 / 255
    print(f'   pixels > 20/255 off the area in the tip windows: {tipsum(over)}, of which stencil 0: {tipsum(over & (st == 0))}')
    for label, kw in (('strip triangles merged by max (each pixel blended once)', dict(blend='max')),
                      ('ramps stopped half a pixel inside their edge (u >= 0.5 only)', dict(inner=False)),
                      ('both', dict(blend='max', inner=False))):
        c2 = compose(layers, st, **kw)
        print(f'   counterfactual, {label}: ink {tipsum(c2):.1f}, > 20/255 off the area {tipsum(np.abs(c2 - area) > 20 / 255)}')
    # One edge's fringe alone: the strip triangles whose outside vertices lie on one side of the tip's bisector.
    bis = np.array(e1) / np.hypot(*e1) + np.array(e2) / np.hypot(*e2)
    best = None
    for ti, (tip, sgn) in enumerate(zip(TIPS, (1, -1))):
        b = np.array([sgn * bis[0], bis[1]])
        side = [np.zeros((H, W)), np.zeros((H, W))]
        for (y0, y1, x0, x1), al, u, outs in layers:
            c = np.mean(outs, axis=0)[:2] - tip
            if np.hypot(*c) > 40:
                continue
            s = 0 if (b[0] * c[1] - b[1] * c[0]) > 0 else 1
            side[s][y0:y1, x0:x1] = 1 - (1 - side[s][y0:y1, x0:x1]) * (1 - al)
        w = wins[ti]
        for s in (0, 1):
            cand = np.where((area[w] <= 0.02) & (st[w] == 0), side[s][w], 0)
            iy, ix = np.unravel_index(np.argmax(cand), cand.shape)
            if best is None or cand[iy, ix] > best[0]:
                best = (cand[iy, ix], w[1].start + ix, w[0].start + iy, s, side[1 - s][w][iy, ix], cov[w][iy, ix],
                        fv[w][iy, ix], tip, b)
    a1, x, y, s, a2, c, f, tip, b = best
    # Which edge is nearer the pixel: the outline's points within 40 px of the tip, split by the same bisector.
    poly = flatten(d, 512)
    rel = poly - tip
    close = np.hypot(*rel.T) < 40
    sides = np.where(b[0] * rel[:, 1] - b[1] * rel[:, 0] > 0, 0, 1)
    dist = [np.hypot(*(poly[close & (sides == k)] - (x + 0.5, y + 0.5)).T).min() for k in (0, 1)]
    print(f'   one edge alone: pixel ({x},{y}), area {area[y, x]:.2f}, gets {a1:.2f} from one edge\'s strip, {a2:.2f} from '
          f'the other\'s, {c:.2f} in all (frame {f:.2f}); its centre is {dist[s]:.2f} px from the edge that strip '
          f'antialiases and {dist[1 - s]:.2f} px from the other')
    # Where the strips' inner vertices (u = 0, 1.5 px inside their edge) land near the tips. Distinct vertices: a
    # bevel_join pushes each twice and the strip's closing loop repeats its first pair. A tip's own inner-bevel
    # vertices (1.5 px off each edge at the point) lie outside at any sharp inner-beveled tip, so they are apart.
    poly = flatten(d)

    def tip_vertices(V, dr):
        S = V[dr[0][2]:dr[0][2] + dr[0][3]]
        inner = np.unique(np.round(S[S[:, 2] == 0.0][:, :2], 3), axis=0)
        dist = np.min([np.hypot(*(inner - t).T) for t in TIPS], axis=0)
        near, own, out = dist < 15, dist < 2, ~inside(poly, inner)
        added = near & ~own
        # How far past each point its strip's outer (u = 1) vertices reach, along the point's outward bisector.
        outer = S[S[:, 2] == 1.0][:, :2]
        bis = np.array(e1) / np.hypot(*e1) + np.array(e2) / np.hypot(*e2)
        bis /= np.hypot(*bis)
        past = max(((outer - tip) @ -np.array([sgn * bis[0], bis[1]])).max() for tip, sgn in zip(TIPS, (1, -1)))
        return (f'{own.sum()} at the tips themselves ({(own & out).sum()} outside the shape), {added.sum()} added by the '
                f'pieces or flattening ({(added & out).sum()} outside); tip strip reaches {past:.2f} px past the point')

    print(f'   distinct strip inner vertices within 15 px of a tip: {tip_vertices(V, dr)}')
    # The same fill with no point inner-beveled: every point's fringe mitered, as the plain wedge's tips already are.
    Vm, drm, _ = capture(d.replace(',', ' '), env={'FV_NO_INNERBEVEL': '1'})
    stm = stencil(Vm, drm)
    cm = compose(strip_layers(Vm, drm, stm), stm)
    print(f'   counterfactual, points mitered (FV_NO_INNERBEVEL=1): excess {(tipsum(cm) - tipsum(area)) / 2:+.2f} px a tip, '
          f'> 20/255 off the area {tipsum(np.abs(cm - area) > 20 / 255)}; {tip_vertices(Vm, drm)}')
    print(f'   as built: excess {(tipsum(cov) - tipsum(area)) / 2:+.2f} px a tip')
