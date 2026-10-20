#!/usr/bin/env python3
"""A model of femtovg's mask rasterizer (src/clip/coverage.rs at 06243b80: Row::span and Coverage::resolve, in
float32), checked against master's frames of the repro, and three ways of folding below a pixel, measured against the
exact area at the same pixels. A model, not a patch: it says what each way leaves and how much work it adds.

  model.py PNG > model.txt     (PNG: render.sh's output; repro and repro-nonzero, each <zoom>.png)

Ways: 'pixel' folds each pixel's summed winding once (master); 'rows 4' accumulates 4 sub-rows of each pixel row
exactly along x, folds each sub-row and averages them; '4x4' rasterizes at four times the size both ways, folds each
of the 16 sub-cells and averages them (FreeType's FT_OUTLINE_OVERLAP); '4x4, shared cells' takes the 4x4 value only in
the cells that two edges pass through in that row, horizontal edges included (a cell needs two to hold windings 0 and
2), and master's elsewhere: the cells between are filled from a whole winding, which folds exactly. The work is
counted as cells taken at 16 samples; most are where two consecutive edges of a contour meet, which a real trigger
could leave out.
"""
import sys
import numpy as np
from PIL import Image

PNG = sys.argv[1]
f32 = np.float32
W, H = 460, 260
STAR = np.array([(100, 15), (150, 175), (20, 75), (180, 75), (50, 175)], float)
ZOOMS = [0.25, 0.33, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2, 3, 4]


def span(area, touched, xa, xb, a, width):
    """Row::span: adds an edge's piece from xa at the row's top to xb at its bottom, a its signed height."""
    lo, hi = (xa, xb) if xa <= xb else (xb, xa)
    if lo >= width:
        return
    if hi <= 0:
        return add(area, touched, 0, a, width)
    if lo < 0:
        outside = f32(lo / (lo - hi))
        add(area, touched, 0, f32(a * outside), width)
        xa, xb = (f32(0), xb) if xa < xb else (xa, f32(0))
        return span(area, touched, xa, xb, f32(a * (1 - outside)), width)
    if hi > width:
        inside = f32((width - lo) / (hi - lo))
        xa, xb = (xa, f32(width)) if xa < xb else (f32(width), xb)
        return span(area, touched, xa, xb, f32(a * inside), width)
    first, end = f32(np.floor(lo)), f32(np.ceil(hi))
    cell, last = int(first), int(end)
    if last <= cell + 1:
        middle = f32(f32(0.5) * (lo + hi) - first)
        add(area, touched, cell, f32(a * (1 - middle)), width)
        add(area, touched, cell + 1, f32(a * middle), width)
        return
    per_cell = f32(1 / (hi - lo))
    enters, leaves = f32(1 - (lo - first)), f32(hi - (end - 1))
    head, tail = f32(f32(0.5) * per_cell * enters * enters), f32(f32(0.5) * per_cell * leaves * leaves)
    add(area, touched, cell, f32(a * head), width)
    if last == cell + 2:
        add(area, touched, cell + 1, f32(a * (1 - head - tail)), width)
    else:
        second = f32(per_cell * (enters + f32(0.5)))
        add(area, touched, cell + 1, f32(a * (second - head)), width)
        for between in range(cell + 2, last - 1):
            add(area, touched, between, f32(a * per_cell), width)
        before_last = f32(second + f32(last - cell - 3) * per_cell)
        add(area, touched, last - 1, f32(a * (1 - before_last - tail)), width)
    add(area, touched, last, f32(a * tail), width)


def add(area, touched, cell, a, width):
    if cell < width and a != 0:
        area[cell] += a
        touched[cell] += 1


def fold(winding, rule):
    w = np.abs(winding)
    if rule == 'nonzero':
        return np.minimum(w, 1)
    f = np.mod(w, 2)
    return np.where(f > 1, 2 - f, f)


def edges_of(points):
    out = []
    for (x0, y0), (x1, y1) in zip(np.roll(points, 1, 0), points):
        if y0 == y1:
            continue
        down, (xa, ya), (xb, yb) = (1, (x0, y0), (x1, y1)) if y0 < y1 else (-1, (x1, y1), (x0, y0))
        out.append((f32(xa), f32(ya), f32(yb), f32((xb - xa) / (yb - ya)), f32(down)))
    return out


def strip(edges, top, bottom, width, scale, rule):
    """One strip [top, bottom) of a row: what each cell folds to, and how many edge pieces touched each cell."""
    area, touched = np.zeros(width + 1, f32), np.zeros(width + 1, np.int32)
    for x, y, yb, slope, down in edges:
        y0, y1 = max(y, f32(top)), min(f32(bottom), yb)
        if y1 <= y0:
            continue
        span(area, touched, f32(x + (y0 - y) * slope), f32(x + (y1 - y) * slope), f32((y1 - y0) * down * scale), width)
    return fold(np.cumsum(area[:width], dtype=f32), rule), touched[:width]


def rasterize(points, rule, way, width=W, height=H):
    """Coverage 0-1 per pixel, and the cells that took a strip's work (pixels x strips) over master's."""
    edges = edges_of(points)
    out = np.zeros((height, width))
    strips = 0
    for row in range(height):
        whole, touched = strip(edges, row, row + 1, width, 1, rule)
        n = way[1] if way[0] == 'rows' else 1
        if n == 1:
            out[row] = whole
            continue
        strips += n - 1
        acc = np.zeros(width)
        for s in range(n):
            acc += strip(edges, row + s / n, row + (s + 1) / n, width, n, rule)[0]
        out[row] = acc / n
    return out, strips


def shared_cells(points, width=W, height=H):
    """Per pixel: whether two or more edges, horizontal ones included, pass through it."""
    count = np.zeros((height, width), np.int32)
    for (x0, y0), (x1, y1) in zip(np.roll(points, 1, 0), points):
        if y0 == y1:
            r = int(np.floor(y0))
            if 0 <= r < height:
                a, b = sorted((x0, x1))
                count[r, max(int(np.floor(a)), 0):min(max(int(np.ceil(b)), 0), width)] += 1
            continue
        (xa, ya), (xb, yb) = sorted(((x0, y0), (x1, y1)), key=lambda p: p[1])
        for r in range(max(int(np.floor(ya)), 0), min(int(np.ceil(yb)), height)):
            t0, t1 = max(ya, r), min(yb, r + 1)
            xs = [xa + (t - ya) * (xb - xa) / (yb - ya) for t in (t0, t1)]
            count[r, max(int(np.floor(min(xs))), 0):min(max(int(np.ceil(max(xs))), 0), width)] += 1
    return count >= 2


def exact(z, rule, ss=32):
    v = device(z)
    x0, y0 = np.maximum(np.floor(v.min(0)).astype(int) - 1, 0)
    x1, y1 = np.minimum(np.ceil(v.max(0)).astype(int) + 1, [W, H])
    o = (np.arange(ss) + 0.5) / ss
    X = (np.arange(x0, x1)[:, None] + o[None, :]).reshape(-1)
    Y = (np.arange(y0, y1)[:, None] + o[None, :]).reshape(-1)
    XX, YY = np.meshgrid(X, Y)
    w = np.zeros(XX.shape, np.int32)
    for i in range(5):
        a, b = v[i], v[(i + 1) % 5]
        up, dn = (a[1] <= YY) & (b[1] > YY), (b[1] <= YY) & (a[1] > YY)
        xc = a[0] + (YY - a[1]) * (b[0] - a[0]) / (b[1] - a[1] + 1e-30)
        w += np.where(up & (xc > XX), 1, 0) - np.where(dn & (xc > XX), 1, 0)
    w = np.abs(w)
    inside = (w % 2 == 1) if rule == 'evenodd' else (w > 0)
    e = np.zeros((H, W))
    e[y0:y1, x0:x1] = inside.reshape(y1 - y0, ss, x1 - x0, ss).mean((1, 3))
    return e


def device(z):
    v = np.stack([230 + z * (STAR[:, 0] - 100), 130 + z * (STAR[:, 1] - 100)], 1)
    return np.round(v * 256) / 256  # coverage.rs takes points on a 1/256 px grid (SUBPIXELS)


def to_u8(c):
    return np.floor(c * 255 + 0.5)


WAYS = [('pixel',), ('rows', 4), ('4x4',), ('4x4 cells',)]
NAME = {('pixel',): 'pixel (master)', ('rows', 4): 'rows 4', ('4x4',): '4x4', ('4x4 cells',): '4x4, shared cells'}
print('zoom rule | model vs master frame: px off, max | per way: px > 8/255 off the exact area (max), work added | '
      'cells in the star\'s box')
for rule, probe in [('evenodd', 'repro'), ('nonzero', 'repro-nonzero')]:
    for z in ZOOMS:
        frame = 255 - np.asarray(Image.open(f'{PNG}/{probe}/{z:g}.png').convert('RGB')).astype(int)[..., 0]
        ex = to_u8(exact(z, rule))
        v = device(z)
        y0, y1 = max(int(v[:, 1].min()) - 1, 0), min(int(np.ceil(v[:, 1].max())) + 1, H)
        rows = y1 - y0
        x0, x1 = max(int(v[:, 0].min()) - 1, 0), min(int(np.ceil(v[:, 0].max())) + 1, W)
        cells = []
        master, _ = rasterize(v, rule, ('pixel',))
        big, _ = rasterize(v * 4, rule, ('pixel',), W * 4, H * 4)
        quad = big.reshape(H, 4, W, 4).mean((1, 3))
        two = shared_cells(v)
        for way in WAYS:
            if way == ('pixel',):
                c, work = master, '+0'
            elif way == ('4x4',):
                c, work = quad, 'x16'
            elif way == ('4x4 cells',):
                c = np.where(two, quad, master)
                work = f'{int(two.sum())} cells x16'
            else:
                c, strips = rasterize(v, rule, way)
                work = f'+{100 * strips / rows:.0f} % strips'
            m = to_u8(c)
            if way == ('pixel',):
                d = np.abs(m - frame)
                check = f'{int((d > 0).sum())}, {int(d.max())}'
            off = np.abs(m - ex)
            cells.append(f'{NAME[way]} {int((off > 8).sum())} ({int(off.max())}) {work}')
        print(f'{z:g} {rule} | {check} | ' + ' | '.join(cells) + f' | {(x1 - x0) * rows}')

# The issue's femtovg-API repro: the star under canvas.scale(1.25, 1.25), no translation. The ladder places it at
# (105, 5) + 1.25 (x, y), a whole-pixel shift, so its pixel (253, 98) is the API's (148, 93).
v = np.round(STAR * 1.25 * 256) / 256
c, _ = rasterize(v, 'evenodd', ('pixel',), 260, 260)
ss = 64
o = (np.arange(ss) + 0.5) / ss
XX, YY = np.meshgrid(148 + o, 93 + o)
w = np.zeros(XX.shape, np.int32)
for i in range(5):
    a, b = v[i], v[(i + 1) % 5]
    up, dn = (a[1] <= YY) & (b[1] > YY), (b[1] <= YY) & (a[1] > YY)
    xc = a[0] + (YY - a[1]) * (b[0] - a[0]) / (b[1] - a[1] + 1e-30)
    w += np.where(up & (xc > XX), 1, 0) - np.where(dn & (xc > XX), 1, 0)
print(f'API repro, pixel (148, 93): model {to_u8(c[93, 148]):.0f}, exact {255 * (np.abs(w) % 2 == 1).mean():.0f}')
