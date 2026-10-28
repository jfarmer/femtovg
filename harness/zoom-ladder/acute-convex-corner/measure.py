#!/usr/bin/env python3
"""Every number of the issue, from the frames in this directory: measure.py > numbers.txt

frames/: the ladder file fill-path-subpixel-sliver-control.svg (460x260 frame, 200 px box at (130,30), zoom about
(230,130)) per zoom: master_* (femtovg 06243b80, the ladder's frame; each zoom's ladder steps and its fresh frame are
bit-identical), prototype_* and variantN_z3 (variants.patch at SV_V=4 / N), chr_* (Chromium 131), ff_* (Firefox 159),
wk_* (WebKit, macOS 27.2), area8_* (Chromium at 8x, averaged here: the area reference).
probes/: s_*.svg in synth.py's framing (synth.py writes all but s_shortedge.svg, whose quad is listed at the end), drawn at zoom 3; s_*_area.png the exact area by area.py;
s_flat_dy0.25_wk.png WebKit at zoom 3. A count is pixels more than 8/255 off (any channel), max in brackets."""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ZOOMS = {1: 'z1', 1.25: 'z125', 1.5: 'z15', 1.75: 'z175', 2: 'z2', 3: 'z3', 4: 'z4', 0.75: 'z075', 0.5: 'z05',
         0.33: 'z033', 0.25: 'z025'}


def load(name):
    a = np.asarray(Image.open(f'{HERE}/{name}').convert('RGB'), dtype=np.float64)
    if a.shape[0] == 8 * 260:
        a = a.reshape(260, 8, 460, 8, 3).mean(axis=(1, 3))
    return np.round(a).astype(np.int16)


def off(a, b, t=8):
    d = np.abs(a - b).max(axis=2)
    return f'{int((d > t).sum())} ({int(d.max())})'


print('Ladder file, every zoom, against each browser (ff only where Firefox frames exist):')
for z, f in ZOOMS.items():
    m, p = load(f'frames/master_{f}.png'), load(f'frames/prototype_{f}.png')
    row = f'  zoom {z:<5g}'
    for b in ('chr', 'ff', 'wk'):
        if os.path.exists(f'{HERE}/frames/{b}_{f}.png'):
            r = load(f'frames/{b}_{f}.png')
            row += f'  {b}: master {off(m, r):>10} prototype {off(p, r):>10}'
    print(row)

for z, f in ((3, 'z3'), (4, 'z4')):
    area = load(f'frames/area8_{f}.png')
    m, p = load(f'frames/master_{f}.png'), load(f'frames/prototype_{f}.png')
    c, x, w = load(f'frames/chr_{f}.png'), load(f'frames/ff_{f}.png'), load(f'frames/wk_{f}.png')
    print(f'\nzoom {z}, against the 8x area reference: master {off(m, area)}, prototype {off(p, area)}, '
          f'Chromium {off(c, area)}, Firefox {off(x, area)}, WebKit {off(w, area)}')
    print(f'  beyond 32/255: Chromium vs area {off(c, area, 32)}, Chromium vs WebKit {off(c, w, 32)}, '
          f'master vs WebKit {off(m, w, 32)}; Chromium vs Firefox {off(c, x)}; Chromium vs WebKit {off(c, w)}')

print('\nzoom 3, the variants against WebKit / the area (1 any-of on every fill, 2 uncapped inset only, 3 convex '
      'BEVEL takes bevel_join only, 4 = 3 + uncapped = the prototype):')
w, area = load('frames/wk_z3.png'), load('frames/area8_z3.png')
for name in ('master_z3', 'variant1_z3', 'variant2_z3', 'variant3_z3', 'prototype_z3'):
    a = load(f'frames/{name}.png')
    print(f'  {name:13} {off(a, w):>10} / {off(a, area)}')

print('\nMaster zoom 3, coverage along the rows (255 - red channel; green #008000 on white), and the exact area:')
cov = 255 - load('frames/master_z3.png')[..., 0]
import importlib.util
spec = importlib.util.spec_from_file_location('area', f'{HERE}/area.py')
area_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(area_mod)
exact = np.round(area_mod.coverage(area_mod.tri_at(3)) * 255).astype(int)
for y in (130, 131):
    r = cov[y]
    first, full = int(np.nonzero(r)[0][0]), int(np.nonzero(r == 255)[0][0])
    print(f'  row {y}: master 0 for x < {first} ({r[first]} at x = {first}), {r[full - 1]} at x = {full - 1}, '
          f'255 from x = {full}, where the area is {exact[y, full]}; area {exact[y, 0]} at x = 0, '
          f'full from x = {int(np.nonzero(exact[y] >= 255)[0][0])}')

print('\nProbes at zoom 3 against the exact area (and WebKit where shot): master / prototype / variant 1 / variant 2')
for k in ('flat_dy0.25', 'acute2', 'acute5', 'shortedge'):
    area = load(f'probes/s_{k}_area.png')
    row = f'  {k:12}'
    for v in ('master', 'prototype', 'variant1', 'variant2'):
        p = f'probes/s_{k}_{v}.png'
        if os.path.exists(f'{HERE}/{p}'):
            row += f'  {v} {off(load(p), area):>10}'
    print(row)
    if os.path.exists(f'{HERE}/probes/s_{k}_wk.png'):
        w = load(f'probes/s_{k}_wk.png')
        row = f'  {k:12} vs WebKit (WebKit vs area {off(w, area)}):'
        for v in ('master', 'prototype', 'variant1', 'variant2'):
            a = load(f'probes/s_{k}_{v}.png')
            d = np.abs(a - w).max(axis=2) > 8
            xs = np.nonzero(d)[1]
            row += f'  {v} {off(a, w)}'
            if v == 'variant2':
                row += f', rows {sorted(set(np.nonzero(d)[0].tolist()))}, {int(((xs < 40) | (xs > 420)).sum())} past the tips'
        print(row)

print('\nDerived (calculate_joins / expand_fill arithmetic at 06243b80, fringe 1 px, woff 0.5):')
print(f'  miter limit 2.4 bevels corners under {2 * np.degrees(np.arcsin(1 / 2.4)):.2f} deg; the 600 cap shortens '
      f'miters under {2 * np.degrees(np.arcsin(1 / np.sqrt(600))):.3f} deg')
A, B, C = np.array([-10, 130.]), np.array([470, 130.]), np.array([230, 133.])  # the sliver at zoom 3, device px
half = np.arctan2(3, 240) / 2  # half the corner angle at A and B
print(f'  corner angle {2 * np.degrees(half):.3f} deg; |dm| = sin(theta/2) = {np.sin(half):.6f}; capped |dmpos| = '
      f'{600 * np.sin(half):.4f}, uncapped {1 / np.sin(half):.2f}; inset at woff: {0.5 * 600 * np.sin(half):.4f} px '
      f'from the corner, {0.5 * 600 * np.sin(half) * np.sin(half):.4f} px inside each edge (fringe at the corner '
      f'{2 * 0.5 * 600 * np.sin(half) * np.sin(half):.4f} px); uncapped inset {0.5 / np.sin(half):.2f} px')
u = (A - B) / np.linalg.norm(A - B) + (C - B) / np.linalg.norm(C - B)
u /= np.linalg.norm(u)  # inward bisector at B
dmpos_b = u * 600 * np.sin(half)
print(f'  at B: dmpos = ({dmpos_b[0]:.4f}, {dmpos_b[1]:.5f}), fan vertex {B + 0.5 * dmpos_b}, outer fringe vertex '
      f'{B - 0.5 * dmpos_b} (the instrumented builds printed dm (+-3.7497, 0.02346), fan (468.125, 130.0117), '
      f'outer (471.875, 129.988))')
dmpos_a = np.array([-dmpos_b[0], dmpos_b[1]])
half_c = np.pi / 2 - 2 * half  # half the apex angle: the apex is 180 deg less both corners
c_in, c_out = C + np.array([0, -0.5 / np.sin(half_c)]), C + np.array([0, 0.5 / np.sin(half_c)])
a_in, a_out = A + 0.5 * dmpos_a, A - 0.5 * dmpos_a


def cross_at(p, q, y=130.5):
    return p[0] + (y - p[1]) * (q[0] - p[0]) / (q[1] - p[1])


print(f'  row 130 (centres y = 130.5): the fan edge crosses at x = {cross_at(a_in, c_in):.1f}, the fringe outer line at '
      f'x = {cross_at(a_out, c_out):.1f}')
perim = sum(np.linalg.norm(p - q) for p, q in ((A, B), (B, C), (C, A)))
print(f'  mean width (2 area / perimeter) at zoom 3: {2 * (480 * 3 / 2) / perim:.3f} px; at zoom z: z/2')
P = np.array([[40.3, 130.2], [420.3, 130.2], [420.3, 140.2], [41.3, 130.7]])  # s_shortedge at zoom 3
print(f'  s_shortedge: corner {np.degrees(np.arctan2(0.5, 1.0)):.1f} deg beside an edge {np.linalg.norm(P[3] - P[0]):.3f} px long')
