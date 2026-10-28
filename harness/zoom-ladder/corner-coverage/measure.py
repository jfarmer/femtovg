#!/usr/bin/env python3
"""Every number in the issue, from the zoom-ladder run's frames (master 06243b80, WGPU, harness _logos_full_zm) and the
browser references of that run.

  measure.py > measure.txt

Builds and frames:
  master      the ladder's frames, png/zl_zm_svg/<key>/<step>.png (bit-identical to a fresh process at each zoom)
  allmasks    master + all-masks-experiment.patch run with ZL_ALL_MASKS=1: every fill through #408's exact-area
              mask, geometry unchanged (triage/dasharray/exp/mask_*.png; corners.svg rendered with the same binary)
  clipcircle  unmodified master on clip-circle.svg: each rect drawn as a circle clipped to it, so the clip box's
              coverage (cover.x * cover.y) replaces the fill fringe (triage/dasharray-v/out/a_cc_*.ppm)
A pixel counts when its largest channel difference is beyond 8/255, the ladder's test; a step fails past 24 px."""
import os
import numpy as np
from PIL import Image

H = os.path.expanduser('~/src/femtovg-wt/runs/zoom')
KEY = 'wpt22__21-degenerate-paths-dashes-and-joins__resvg-dasharray-0-n-square-caps-ref'
LADDER = [1, 1.25, 1.5, 1.75, 2, 3, 4, 3, 2, 1.75, 1.5, 1.25, 1, 0.75, 0.5, 0.33, 0.25, 0.33, 0.5, 0.75, 1]
FR = {1: 'z1', 1.25: 'z125', 1.5: 'z15', 1.75: 'z175', 2: 'z2', 3: 'z3', 4: 'z4', 0.75: 'z075', 0.5: 'z05',
      0.33: 'z033', 0.25: 'z025'}
RECTS = [(30, 30), (70, 30), (110, 30), (150, 30), (150, 70), (150, 110), (150, 150), (110, 150), (70, 150),
         (30, 150), (30, 110), (30, 70)]


def load(p):
    return np.asarray(Image.open(p).convert('RGB'), dtype=np.int16) if os.path.exists(p) else None


def master(z):
    return load(f'{H}/png/zl_zm_svg/{KEY}/{LADDER.index(z):02}.png')


def allmasks(z):
    return load(f'{H}/triage/dasharray/exp/mask_resvg-dasharray-0-n-square-caps-ref_{z:g}.png')


def clipcircle(z):
    return load(f'{H}/triage/dasharray-v/out/a_cc_{z:g}.ppm')


def ref(b, z):
    return load(f'{H}/fresh/refs/{b}_{KEY}_{FR[z]}.png')


def dev(v, z):  # user unit -> device pixel, the ladder's framing (460x260, 200 px box, zoom about the centre)
    return 230 + (v - 100) * z


def devy(v, z):
    return 130 + (v - 100) * z


def classify(a, o, z):
    """Pixels beyond 8/255 by place: a rect's corner pixel, the frame's corner pixels, anything else."""
    d = np.abs(a - o).max(2) > 8
    cx = [dev(v, z) for v in (30, 50, 70, 90, 110, 130, 150, 170)]
    cy = [devy(v, z) for v in (30, 50, 70, 90, 110, 130, 150, 170)]
    fx = [dev(v, z) for v in (0.5, 1.5, 198.5, 199.5)]
    fy = [devy(v, z) for v in (0.5, 1.5, 198.5, 199.5)]
    n = {'rect': 0, 'frame': 0, 'other': 0}
    for y, x in zip(*np.nonzero(d)):
        if min(abs(x + .5 - v) for v in cx) < 1.01 and min(abs(y + .5 - v) for v in cy) < 1.01:
            n['rect'] += 1
        elif min(abs(x + .5 - v) for v in fx) < 1.01 and min(abs(y + .5 - v) for v in fy) < 1.01:
            n['frame'] += 1
        else:
            n['other'] += 1
    return int(d.sum()), n


print('1. The ladder file, px beyond 8/255 (rect corners + frame corners + other)')
print(f'   failing steps on master: {[i for i, z in enumerate(LADDER) if z in (1.25, 1.75, 0.75, 0.33, 0.25)]}'
      f' ({sum(z in (1.25, 1.75, 0.75, 0.33, 0.25) for z in LADDER)} of {len(LADDER)})')
for z in (1, 1.25, 1.5, 1.75, 2, 3, 4, 0.75, 0.5, 0.33, 0.25):
    xs = sorted({round(dev(v, z) % 1, 3) for v in (30, 50, 70, 90, 110, 130, 150, 170)})
    line = f'   zoom {z:<4g} rect edges at pixel fractions {xs}:'
    for b in ('chr', 'ff', 'wk'):
        o = ref(b, z)
        if o is None:
            line += f'  {b} -'
            continue
        parts = []
        for name, f in (('master', master), ('allmasks', allmasks), ('clipcircle', clipcircle)):
            a = f(z)
            if a is None:
                continue
            n, c = classify(a, o, z)
            parts.append(f'{name} {n} ({c["rect"]}+{c["frame"]}+{c["other"]})')
        line += f'\n      vs {b}: ' + ', '.join(parts)
    print(line)

print('\n2. Corner pixels, red channel (green on white: coverage = 1 - R/255)')
for z in (1, 1.25, 0.75, 0.33, 0.25):
    m, e = master(z), allmasks(z)
    R = {b: ref(b, z) for b in ('chr', 'ff', 'wk')}
    X0, Y0 = int(np.floor(dev(0.5, z))), int(np.floor(devy(0.5, z)))
    X1, Y1 = int(np.floor(dev(1.5, z) - 1e-9)), int(np.floor(devy(1.5, z) - 1e-9))
    RX, RY = int(np.floor(dev(30, z))), int(np.floor(devy(30, z)))

    def row(X, Y):
        s = f'master {m[Y, X, 0]} allmasks {e[Y, X, 0]}'
        return s + ''.join(f' {b} {o[Y, X, 0]}' for b, o in R.items() if o is not None)
    print(f'   zoom {z:g}: rect (30,30) top-left at ({dev(30, z):.3f}, {devy(30, z):.3f}) px ({RX},{RY}): {row(RX, RY)}')
    print(f'      frame outer corner px ({X0},{Y0}): {row(X0, Y0)}')
    if (X1, Y1) != (X0, Y0):
        print(f'      frame inner corner px ({X1},{Y1}): {row(X1, Y1)}')

print('\n3. The rects against two models, largest error over every rect pixel, /255')
print('   min: femtovg takes min(ax, ay) of the per-axis ramps; area: ax * ay, the exact coverage')
Xc, Yc = np.arange(460) + .5, np.arange(260) + .5
for z in (1.25, 1.75, 0.75, 0.33, 0.25):
    mn, ar = np.zeros((260, 460)), np.zeros((260, 460))
    for x, y in RECTS:
        ax = np.clip(np.minimum(Xc - dev(x, z) + .5, dev(x + 20, z) - Xc + .5), 0, 1)
        ay = np.clip(np.minimum(Yc - devy(y, z) + .5, devy(y + 20, z) - Yc + .5), 0, 1)
        mn = np.maximum(mn, np.minimum(ax[None, :], ay[:, None]))
        ar = np.maximum(ar, ax[None, :] * ay[:, None])
    on = (ar > 0) | (mn > 0)
    cov = lambda a: 1 - a[..., 0] / 255
    out = f'   zoom {z:<4g}'
    for name, a in (('master', master(z)), ('allmasks', allmasks(z)), ('chr', ref('chr', z)), ('wk', ref('wk', z))):
        c = cov(a)
        out += f'  {name}: min {np.abs(c - mn)[on].max() * 255:.1f} area {np.abs(c - ar)[on].max() * 255:.1f}'
    print(out + f'  (pixels where min and area differ beyond 8/255: {int((np.abs(mn - ar) * 255 > 8).sum())})')

print('\n4. corners.svg at 1x: coverage of each rect\'s top-left pixel, corner on fraction f of it in x and y')
D = os.path.dirname(os.path.abspath(__file__))
W = os.path.expanduser('~/src/femtovg-wt/runs/zoom/drafts/N10-corner-coverage/work')
P = f'{H}/triage/dasharray/repro'
c8 = load(f'{P}/chr8_corners.png').astype(float).reshape(260, 8, 460, 8, 3).mean((1, 3))
imgs = [('master', load(f'{W}/corners_master_z1.png')), ('allmasks', load(f'{W}/corners_allmasks_z1.png')),
        ('Chromium 131', load(f'{P}/chr_corners.png')), ('8x area reference', c8)]
fs = [0, 0.1, 0.25, 0.5, 0.75, 0.9]
print('   f:                 ' + ''.join(f'{f:>7g}' for f in fs))
for name, a in imgs:
    print(f'   {name:<19}' + ''.join(f'{1 - a[40, 140 + 30 * i, 0] / 255:7.3f}' for i in range(6)))
print('   model 1-f (min):   ' + ''.join(f'{1 - f:7.3f}' for f in fs))
print('   model (1-f)^2:     ' + ''.join(f'{(1 - f) ** 2:7.3f}' for f in fs))

print('\n5. The error f(1-f) of a convex corner on fraction f of a pixel in both axes')
f = np.linspace(0, 1, 100001)
e = f * (1 - f) * 255
print(f'   largest {e.max():.2f}/255 at f = {f[e.argmax()]:.2f}; beyond 8/255 for f in '
      f'[{f[e > 8].min():.4f}, {f[e > 8].max():.4f}]')

print('\n6. frame-as-fill.svg (the frame as an even-odd fill, rects unchanged) with ZL_ALL_MASKS=1, px beyond 8/255')
for z in (1, 1.25, 0.75):
    a = load(f'{H}/triage/dasharray/exp/ff_mask_{z:g}.png')
    print(f'   zoom {z:<4g}' + ''.join(f'  vs {b} {int((np.abs(a - ref(b, z)).max(2) > 8).sum())}' for b in ('chr', 'ff', 'wk')))

print('\n7. clip-circle.svg on master against the all-masks frames: largest difference /255 at each zoom')
for z in (1, 1.25, 1.5, 1.75, 2, 0.75, 0.33, 0.25):
    print(f'   zoom {z:<4g} {int(np.abs(clipcircle(z) - allmasks(z)).max())}')
