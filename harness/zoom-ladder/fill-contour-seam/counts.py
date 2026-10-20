#!/usr/bin/env python3
"""Every number in the issue, from the frames in frames/ (460x260, 200 px box at (130,30), as the zoom ladder frames).

master: femtovg master 06243b80 on WGPU (the ladder build zm; the proof build without toggles is bit-identical).
masked: the same build with FV_FORCE_THIN=1 (proof_toggles.patch): every fill through #408's coverage mask.
merged: master on shoe_merged.svg, each path's squares merged into one outline, so no edge is shared.
gate: FV_GATE_FIX=1 (proof_toggles.patch): #408's thin-fill gate takes a fill of several contours as concave.
halffringe: SKV_HALF=1 (half_fringe_toggles.patch): every fill's fringe stops 0.5 px inside its edge, as a convex
  fill's does, so only the seam's band is left of the overlap between fringes.
chr / ff / wk: Chromium 131, Firefox 159, WebKit (macOS 27.2), through make_ref.py pages.
shoe_z033_master is the ladder's own frame (steps 16 and 18 are identical); the other femtovg frames come from the
proof builds in the ladder's framing (FRAME_W=460 FRAME_H=260 BOX=200 BOX_X=130 BOX_Y=30 SKIP_UNSUPPORTED_FILTERS=1
VIEWPORT_CLIP=1, _logos_full ZOOM OUT.ppm SVG), the browsers' from make_ref.py pages; seam.svg the same way.
Counts are pixels more than 8/255 off (the zoom ladder's threshold), on any channel, frames composited on white.

  python3 counts.py > counts.txt"""
import os
import numpy as np
from PIL import Image

F = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frames')


def load(name):
    a = np.asarray(Image.open(f'{F}/{name}.png').convert('RGBA')).astype(float)
    return (a[..., :3] * a[..., 3:4] + 255 * (255 - a[..., 3:4])) / 255


def off(a, b, t=8):
    return int((np.abs(a - b).max(-1) > t).sum())


import re
# squares keyed in half-square units: every square's y is an odd multiple of 20.48
_paths = [{(round(float(x) / 20.48), round(float(y) / 20.48)) for x, y in re.findall(r'M([\d.]+) ([\d.]+)', d)}
          for d, _ in re.findall(r'<path d="([^"]+)"\s*fill="([^"]+)"', open(os.path.join(os.path.dirname(F), 'shoe.svg')).read())]
_shared = sum((x + 2, y) in s for s in _paths for x, y in s) + sum((x, y + 2) in s for s in _paths for x, y in s)
print(f'== the shoe (corpus/svgenius/hard/page_70_..._40194_icon_17.svg): {len(_paths)} paths of 40.96-unit squares,'
      f' {min(map(len, _paths))} to {max(map(len, _paths))} a path, {sum(map(len, _paths))} in all;'
      f' {_shared} square edges shared within a path')
ladder = [1, 1.25, 1.5, 1.75, 2, 3, 4, 0.75, 0.5, 0.33, 0.25]
print('shared edges at x = 230 + (8k - 100) z, y = 130 + (8j - 40) z; furthest from a whole pixel, per ladder zoom:')
for z in ladder:
    e = [230 + (8 * k - 100) * z for k in range(26)] + [130 + (8 * j - 40) * z for j in range(26)]
    print(f'  {z:g}: {max(abs(v - round(v)) for v in e):.2f} px')
print('off the ladder, the edge lines on whole pixels:')
for z in (0.6, 0.9, 1.1, 1.3):
    on = lambda c, o: [k for k in range(26) if abs(c + (8 * k - o) * z - round(c + (8 * k - o) * z)) < 1e-6]
    print(f'  {z:g}: squares {8 * z:g} px; x lines k = {on(230, 100)}, y lines j = {on(130, 40)} of 0-25')
for zz, label in [('033', '0.33 (ladder steps 16 and 18)'), ('06', '0.6'), ('09', '0.9'), ('11', '1.1'), ('13', '1.3')]:
    ims = {n: load(f'shoe_z{zz}_{n}') for n in ('master', 'masked', 'merged', 'gate', 'halffringe', 'chr', 'ff', 'wk')
           if os.path.exists(f'{F}/shoe_z{zz}_{n}.png')}
    refs = [r for r in ('wk', 'chr', 'ff') if r in ims]
    print(f'shoe at {label}')
    for b in ('master', 'masked', 'merged', 'gate', 'halffringe'):
        if b in ims:
            print(f'  {b:10s}', '  '.join(f'vs {r} {off(ims[b], ims[r]):4d}' for r in refs),
                  f'  (beyond 20/255 vs wk {off(ims[b], ims["wk"], 20)}, max {np.abs(ims[b] - ims["wk"]).max():.0f}/255)')
    print('  browsers:', '  '.join(f'{a}-{b} {off(ims[a], ims[b])}' for i, a in enumerate(refs) for b in refs[i + 1:]))

print('where the pixels off WebKit lie, for master and merged (no shared edge): within 2 px of a square\'s corner,'
      ' else within 0.5 px of an edge line')
for zz, z in [('09', 0.9), ('11', 1.1)]:
    xe = np.array([230 + (8 * k - 100) * z for k in range(26)])
    ye = np.array([130 + (8 * j - 40) * z for j in range(26)])
    w = load(f'shoe_z{zz}_wk')
    for b in ('master', 'merged'):
        pts = list(zip(*np.nonzero(np.abs(load(f'shoe_z{zz}_{b}') - w).max(-1) > 8)))
        dist = [(np.abs(xe - x - 0.5).min(), np.abs(ye - y - 0.5).min()) for y, x in pts]
        corner = sum(1 for dx, dy in dist if max(dx, dy) <= 2)
        edge = sum(1 for dx, dy in dist if max(dx, dy) > 2 and min(dx, dy) <= 0.5)
        print(f'  {z:g} {b:7s} {len(pts):4d} px: {corner} near a corner, {edge} along an edge, {len(pts) - corner - edge} other')
print('how many paths each off pixel touches (shoe.svg = the corpus file): one = inside a path or on its outer edge, two or more ='
      ' where separate paths meet, as in #411')
import re
_t = open(os.path.join(os.path.dirname(F), 'shoe.svg')).read()
_sq = [(i, float(x), float(y)) for i, (d, _) in enumerate(re.findall(r'<path d="([^"]+)"\s*fill="([^"]+)"', _t))
       for x, y in re.findall(r'M([\d.]+) ([\d.]+)', d)]


def touched(px, py, z):
    sc, hits = 200 / 1024, set()
    s = 40.96 * sc * z
    for i, x, y in _sq:
        x0, y0 = 230 + (130 + x * sc - 230) * z, 130 + (30 + y * sc - 130) * z
        if min(px + 1, x0 + s) - max(px, x0) > 1e-6 and min(py + 1, y0 + s) - max(py, y0) > 1e-6:
            hits.add(i)
    return len(hits)


for zz, z in [('033', 0.33), ('06', 0.6), ('09', 0.9), ('11', 1.1), ('13', 1.3)]:
    w = load(f'shoe_z{zz}_wk')
    for b in ('master', 'chr'):
        pts = list(zip(*np.nonzero(np.abs(load(f'shoe_z{zz}_{b}') - w).max(-1) > 8)))
        k = [touched(x, y, z) for y, x in pts]
        print(f'  {z:g} {b:7s} vs wk {len(pts):4d} px: {sum(v == 1 for v in k)} touch one path, {sum(v >= 2 for v in k)} two or more')
print()
print('== seam.svg at 1x: four 10 px squares a row; frame x = 130 + svg x, y = 30 + svg y')
ims = {n: load(f'seam_{n}') for n in ('master', 'masked', 'chr', 'ff', 'wk')}
rows = [('one path, shared edges through pixel centres (d = 0)', 55, 0.0),
        ('one path, a quarter pixel off them (d = 0.25)', 70, 0.25),
        ('one path, on pixel edges (d = 0.5)', 85, 0.5),
        ('four paths, edges through pixel centres', 100, None)]
for name, y, d in rows:
    model = f'  model 255 (1 - (0.75 + d^2)) = {255 * (1 - (0.75 + d * d)):.1f}' if d is not None else ''
    print(f'{name}:{model}')
    for n, a in ims.items():
        print(f'  {n:7s} columns 160, 170, 180 in row {y}:', [int(round(a[y, x, 0])) for x in (160, 170, 180)])
print('whole frame:', '  '.join(f'{b} vs {r} {off(ims[b], ims[r])}' for b in ('master', 'masked') for r in ('chr', 'ff', 'wk')))
print('browsers:', f"chr-ff {off(ims['chr'], ims['ff'])}  chr-wk {off(ims['chr'], ims['wk'])}  ff-wk {off(ims['ff'], ims['wk'])}")
dm = np.abs(ims['master'] - ims['wk']).max(-1) > 8
cols = np.zeros_like(dm)
cols[:, [160, 170, 180]] = True
for name, y0, y1 in [('row 1', 50, 61), ('row 2', 65, 76), ('row 3', 80, 91), ('row 4', 95, 106)]:
    band = np.zeros_like(dm)
    band[y0 + 1:y1 - 1] = True
    edge = np.zeros_like(dm)
    edge[[y0, y1 - 1]] = True
    print(f'  master vs wk, {name}: {int((dm & band & cols).sum())} px in the seam columns inside the row,'
          f' {int((dm & edge).sum())} on its top and bottom edge pixels (squares\' corners, which the fringe covers by'
          f' min(cx, cy) where the area is cx cy, #13), {int((dm & band & ~cols).sum())} elsewhere')
