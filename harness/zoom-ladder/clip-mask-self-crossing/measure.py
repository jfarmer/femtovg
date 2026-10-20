#!/usr/bin/env python3
"""Numbers for the issue: a coverage mask folds a pixel's summed winding by the fill rule, so a pixel of a self-crossing
contour that holds windings 0, 1 and 2 comes out over-covered.

  measure.py PNG REFS AREA > numbers.txt

PNG: render.sh's output (multiple-children, multiple-children-uncrossed, repro, repro-nonzero, each <zoom>.png).
REFS: the zoom ladder's browser frames (wk_<key>_<framing>.png). AREA: the 8x area references (id_<key>_<framing>.png).

The exact coverage is counted on a 32 x 32 grid of samples a pixel (64 x 64 for the pixels where 0 and 2 meet). The
framing is the ladder's: the file's 200 px box centred in a 460 x 260 frame, so a point (x, y) of the file lands at
(230 + z (x - 100), 130 + z (y - 100)). Green on white: coverage = (255 - R) / 255."""
import json, sys
import numpy as np
from PIL import Image

PNG, REFS, AREA = sys.argv[1:4]
KEY = 'wpt22__20-clippath-unions-and-masks__resvg-clippath-multiple-children'
TAG = {1: 'z1', 1.25: 'z125', 1.5: 'z15', 1.75: 'z175', 2: 'z2', 3: 'z3', 4: 'z4', 0.75: 'z075', 0.5: 'z05',
       0.33: 'z033', 0.25: 'z025'}
ZOOMS = [0.25, 0.33, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2, 3, 4]
# M100 15 l50 160 -130 -100 h160 l-130 100 z
STAR = np.array([(100, 15), (150, 175), (20, 75), (180, 75), (50, 175)], float)
W, H = 460, 260


def load(p):
    try:
        return np.asarray(Image.open(p).convert('RGB')).astype(np.int32)
    except FileNotFoundError:
        return None


def device(z, pts):
    return np.stack([230 + z * (pts[..., 0] - 100), 130 + z * (pts[..., 1] - 100)], -1)


def inner_vertices():
    out = []
    e = [(STAR[i], STAR[(i + 1) % 5]) for i in range(5)]
    for i in range(5):
        for j in range(i + 1, 5):
            (p1, p2), (p3, p4) = e[i], e[j]
            d, f = p2 - p1, p4 - p3
            den = d[0] * f[1] - d[1] * f[0]
            if abs(den) < 1e-12:
                continue
            t = ((p3 - p1)[0] * f[1] - (p3 - p1)[1] * f[0]) / den
            u = ((p3 - p1)[0] * d[1] - (p3 - p1)[1] * d[0]) / den
            if 1e-9 < t < 1 - 1e-9 and 1e-9 < u < 1 - 1e-9:
                out.append(p1 + t * d)
    return np.array(out)


INNER = inner_vertices()


def winding(z, X, Y):
    v = device(z, STAR)
    w = np.zeros(X.shape, np.int32)
    for i in range(5):
        a, b = v[i], v[(i + 1) % 5]
        up = (a[1] <= Y) & (b[1] > Y)
        dn = (b[1] <= Y) & (a[1] > Y)
        xc = a[0] + (Y - a[1]) * (b[0] - a[0]) / (b[1] - a[1] + 1e-30)
        w += np.where(up & (xc > X), 1, 0) - np.where(dn & (xc > X), 1, 0)
    return np.abs(w)


def shares(z, x0, y0, x1, y1, ss):
    """Per pixel of [x0, x1) x [y0, y1): the share of it at winding 0, 1 and 2, and inside the r = 10 circle."""
    o = (np.arange(ss) + 0.5) / ss
    X = (np.arange(x0, x1)[:, None] + o[None, :]).reshape(-1)
    Y = (np.arange(y0, y1)[:, None] + o[None, :]).reshape(-1)
    XX, YY = np.meshgrid(X, Y)
    w = winding(z, XX, YY)
    disc = (XX - 230) ** 2 + (YY - 130) ** 2 < (10 * z) ** 2
    mean = lambda m: m.reshape(y1 - y0, ss, x1 - x0, ss).mean((1, 3))
    return [mean(w == k) for k in range(3)] + [mean(disc)]


def bbox(z):
    v = device(z, STAR)
    x0, y0 = np.maximum(np.floor(v.min(0)).astype(int) - 1, 0)
    x1, y1 = np.minimum(np.ceil(v.max(0)).astype(int) + 1, [W, H])
    return x0, y0, x1, y1


def fold(s, rule):
    if rule == 'nonzero':
        return np.minimum(s, 1)
    f = np.mod(s, 2)
    return np.where(f > 1, 2 - f, f)


def coverage_maps(z, rule, circle):
    """exact: the area's coverage. folded: the coverage the mask's fold gives, from the same shares. both 0-255."""
    x0, y0, x1, y1 = bbox(z)
    a0, a1, a2, disc = shares(z, x0, y0, x1, y1, 32)
    exact_star = a1 + (a2 if rule == 'nonzero' else 0)
    folded_star = fold(a1 + 2 * a2, rule)
    exact, folded, meet = np.zeros((H, W)), np.zeros((H, W)), np.zeros((H, W), bool)
    # The disc lies inside the pentagon, where the star is a hole under even-odd: the two add without overlap.
    exact[y0:y1, x0:x1] = np.minimum(exact_star + (disc if circle else 0), 1) * 255
    folded[y0:y1, x0:x1] = np.minimum(folded_star + (disc if circle else 0), 1) * 255
    meet[y0:y1, x0:x1] = (a0 > 0) & (a2 > 0)
    return exact, folded, meet, (x0, y0, x1, y1)


def cov(im):
    return 255 - im[..., 0]


def beyond(a, b, mask=None, t=8):
    d = np.abs(a - b).max(-1) > t
    return int((d if mask is None else d & mask).sum())


def meet_pixels(z, rule):
    """The pixels where winding 0 and 2 meet, at 64 x 64 samples: (x, y, a0, a1, a2, exact, folded)."""
    out = []
    for q in device(z, INNER):
        for py in range(int(q[1]) - 2, int(q[1]) + 3):
            for px in range(int(q[0]) - 2, int(q[0]) + 3):
                if not (0 <= px < W and 0 <= py < H):
                    continue
                a0, a1, a2, _ = (float(s[0, 0]) for s in shares(z, px, py, px + 1, py + 1, 64))
                if a0 > 0 and a2 > 0:
                    e = a1 + (a2 if rule == 'nonzero' else 0)
                    out.append((px, py, a0, a1, a2, 255 * e, 255 * float(fold(a1 + 2 * a2, rule))))
    return out


result = {}
yy, xx = np.mgrid[0:H, 0:W]
for probe, rule, circle in [('multiple-children', 'evenodd', True), ('repro', 'evenodd', False),
                            ('repro-nonzero', 'nonzero', False)]:
    print(f'\n== {probe}: the pentagram under {rule}' + (' and the r = 10 circle' if circle else ''))
    print('zoom | femtovg off the area by > 8/255 inside the star (max) | femtovg off the fold by > 2/255 | '
          'pixels where 0 and 2 meet: count, femtovg - exact max, fold - exact max | worst pixel')
    for z in ZOOMS:
        im = load(f'{PNG}/{probe}/{z:g}.png')
        f = cov(im).astype(float)
        exact, folded, meet, (x0, y0, x1, y1) = coverage_maps(z, rule, circle)
        # Inside the star's box, 2 px clear of the 1 px frame and of the box's sides (the five tips).
        roi = (xx >= x0 + 2) & (xx < x1 - 2) & (yy >= y0 + 2) & (yy < y1 - 2)
        roi &= (xx > 230 + z * (1 - 100) + 2) & (xx < 230 + z * (199 - 100) - 2)
        roi &= (yy > 130 + z * (1 - 100) + 2) & (yy < 130 + z * (199 - 100) - 2)
        off = np.abs(f - exact) * roi
        offfold = np.abs(f - folded) * roi
        px = meet_pixels(z, rule)
        over = [(f[y, x] - e, x, y, e, fo, f[y, x]) for x, y, _, _, _, e, fo in px]
        worst = max(over) if over else None
        line = (f'{z:g} | {int((off > 8).sum())} ({off.max():.0f}) | {int((offfold > 2).sum())} | {len(px)}, '
                f'{max(o[0] for o in over):.0f}, {max(o[4] - o[3] for o in over):.0f}')
        if worst:
            line += f' | ({worst[1]},{worst[2]}): femtovg {worst[5]:.0f}, exact {worst[3]:.0f}, fold {worst[4]:.0f}'
        print(line)
        result.setdefault(probe, {})[f'{z:g}'] = {
            'off_area_px': int((off > 8).sum()), 'off_area_max': float(off.max()),
            'off_fold_px': int((offfold > 2).sum()), 'meet_pixels': len(px),
            'meet_over_max': float(max(o[0] for o in over)), 'fold_over_max': float(max(o[4] - o[3] for o in over)),
            'worst': [int(worst[1]), int(worst[2]), float(worst[5]), float(worst[3]), float(worst[4])]}

# The corpus file against WebKit, whole frame, as the ladder scores it (more than 8/255 in any channel; pass: 24 px
# or fewer), split by where the pixels lie: within 2.5 px of an inner vertex, within 3 px of a corner of the 1 px
# frame, elsewhere. Then WebKit itself and the uncrossed redraw against the area, inside the star.
print('\n== multiple-children against WebKit, px > 8/255 (vertex + frame corner + other) | uncrossed redraw | '
      'WebKit off the exact star (inside the star, max) | Chromium off it | master and uncrossed vs the 8x area '
      'reference, whole frame | the pixels where 0 and 2 meet')
for z in ZOOMS:
    m, nc = load(f'{PNG}/multiple-children/{z:g}.png'), load(f'{PNG}/multiple-children-uncrossed/{z:g}.png')
    wk, idr = load(f'{REFS}/wk_{KEY}_{TAG[z]}.png'), load(f'{AREA}/id_{KEY}_{TAG[z]}.png')
    near = np.zeros((H, W), bool)
    for q in device(z, INNER):
        near |= np.hypot(xx + 0.5 - q[0], yy + 0.5 - q[1]) < 2.5
    corner = np.zeros((H, W), bool)
    for cx in (1, 199):
        for cy in (1, 199):
            q = device(z, np.array([cx, cy], float))
            corner |= (np.abs(xx + 0.5 - q[0]) < 3) & (np.abs(yy + 0.5 - q[1]) < 3)
    exact, _, _, (x0, y0, x1, y1) = coverage_maps(z, 'evenodd', True)
    roi = (xx >= x0 + 2) & (xx < x1 - 2) & (yy >= y0 + 2) & (yy < y1 - 2)
    roi &= (xx > 230 + z * (1 - 100) + 2) & (xx < 230 + z * (199 - 100) - 2)
    roi &= (yy > 130 + z * (1 - 100) + 2) & (yy < 130 + z * (199 - 100) - 2)
    wkoff = np.abs(cov(wk) - exact) * roi
    choff = np.abs(cov(load(f'{REFS}/chr_{KEY}_{TAG[z]}.png')) - exact) * roi
    total, v, c = beyond(m, wk), beyond(m, wk, near), beyond(m, wk, corner & ~near)
    # At the pixels where 0 and 2 meet: how far master, the uncrossed redraw and WebKit lie from the exact area.
    meet = meet_pixels(z, 'evenodd')
    at = {n: max(abs(cov(im)[y, x] - e) for x, y, _, _, _, e, _ in meet) for n, im in (('m', m), ('nc', nc), ('wk', wk))}
    print(f'{z:g} | {total} ({v} + {c} + {total - v - c}) | {beyond(nc, wk)} (vertex {beyond(nc, wk, near)}) | '
          f'{int((wkoff > 8).sum())} ({wkoff.max():.0f}) | {int((choff > 8).sum())} ({choff.max():.0f}) | '
          f'{beyond(m, idr)} -> {beyond(nc, idr)} | at the {len(meet)} meeting pixels, off the exact area by at most: '
          f'master {at["m"]:.0f}, uncrossed {at["nc"]:.0f}, WebKit {at["wk"]:.0f}')
    result.setdefault('vs_webkit', {})[f'{z:g}'] = {
        'master': total, 'master_vertex': v, 'master_frame_corner': c, 'uncrossed': beyond(nc, wk),
        'uncrossed_vertex': beyond(nc, wk, near), 'webkit_off_exact': int((wkoff > 8).sum()),
        'webkit_off_exact_max': float(wkoff.max()), 'chromium_off_exact': int((choff > 8).sum()),
        'chromium_off_exact_max': float(choff.max()), 'master_vs_area': beyond(m, idr), 'uncrossed_vs_area': beyond(nc, idr),
        'meeting_pixels_off_exact_max': {k: float(v) for k, v in at.items()}}
json.dump(result, open(sys.argv[4] if len(sys.argv) > 4 else 'numbers.json', 'w'), indent=1)

# What the uncrossed redraw leaves beyond 8/255 of WebKit at the two failing zooms, by where it lies, with how far
# each lies from the 8x area reference there.
print('\n== the uncrossed redraw against WebKit at the failing zooms: px > 8/255 by place | uncrossed and WebKit off '
      'the 8x area reference there (range /255)')
for z in (1.25, 1.75):
    nc, wk = load(f'{PNG}/multiple-children-uncrossed/{z:g}.png'), load(f'{REFS}/wk_{KEY}_{TAG[z]}.png')
    idr = load(f'{AREA}/id_{KEY}_{TAG[z]}.png')
    corner = np.zeros((H, W), bool)
    for cx in (1, 199):
        for cy in (1, 199):
            q = device(z, np.array([cx, cy], float))
            corner |= (np.abs(xx + 0.5 - q[0]) < 3) & (np.abs(yy + 0.5 - q[1]) < 3)
    disc = np.abs(np.hypot(xx + 0.5 - 230, yy + 0.5 - 130) - 10 * z) < 2
    left = np.abs(nc - wk).max(-1) > 8
    for name, where in (('frame corners', corner), ('the r = 10 circle', disc & ~corner),
                        ('elsewhere', ~corner & ~disc)):
        p = left & where
        if p.any():
            a, b = np.abs(nc - idr).max(-1)[p], np.abs(wk - idr).max(-1)[p]
            print(f'{z:g} {name}: {int(p.sum())} px, uncrossed {a.min()}-{a.max()}, WebKit {b.min()}-{b.max()}')
        else:
            print(f'{z:g} {name}: 0 px')
