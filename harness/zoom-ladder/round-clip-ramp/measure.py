#!/usr/bin/env python3
"""clip-path-variation-28 (a 25-unit circle clip at 110,95 over a green rect) at the ladder's eleven zooms, each
renderer against the exact disc: pixels more than 8/255 off it and the largest difference, of 255, and where the
off pixels lie (share within 30-60 degrees of the axes, i.e. on the diagonals).

The exact disc is each pixel's share inside the circle, integrated exactly along y and with 512 samples along x.
Frames: femtovg master 06243b80 (_logos_full_master_v, bit-identical to the ladder's frames) and the prototype
(_logos_full_area_v, 48b9284 on 06243b80), WebKit (macOS 27.2), Chromium 131 in software (the ladder's reference),
Chromium 131 on the GPU at one device pixel per CSS pixel, and Firefox where the ladder has its frame.

Then, per zoom: how far master is from the ramp clamp(0.5 - (|p - c| - r)) (largest, of 255); whether the circle
written as 16 arcs (v28_16.svg, frames of _logos_full_master_v) renders the same as usvg's four cubics; and of the
pixels where master and WebKit are more than 8/255 apart, how many have errors from the exact disc of opposite sign;
how master's off pixels split between 30-60 degrees from the axes and the bins next to them (15-30, 60-75); and how far
the 8x area reference (Chromium 131 on the GPU at 8x, averaged) is from the exact disc.

  RUNS_ZOOM=~/src/femtovg-wt/runs/zoom measure.py"""
import os, sys
import numpy as np
from PIL import Image

R = os.environ.get('RUNS_ZOOM', os.path.expanduser('~/src/femtovg-wt/runs/zoom'))
K = 'corpus__wpt-clip-path-reftests__clip-path-variation-28'
TAG = {1: 'z1', 1.25: 'z125', 1.5: 'z15', 1.75: 'z175', 2: 'z2', 3: 'z3', 4: 'z4', 0.75: 'z075', 0.5: 'z05',
       0.33: 'z033', 0.25: 'z025'}


def load(p):
    return np.asarray(Image.open(p).convert('RGB'), dtype=np.float64) if os.path.exists(p) else None


def disc(W, H, cx, cy, r, n=512):
    cov = np.zeros((H, W))
    for px in range(max(0, int(cx - r) - 1), min(W, int(cx + r) + 2)):
        xs = px + (np.arange(n) + 0.5) / n
        h = np.sqrt(np.clip(r * r - (xs - cx) ** 2, 0, None))
        for py in range(max(0, int(cy - r) - 1), min(H, int(cy + r) + 2)):
            cov[py, px] = np.clip(np.minimum(py + 1, cy + h) - np.maximum(py, cy - h), 0, None).mean()
    return cov


def exact(z):
    # The ladder pivots on the frame's centre (230,130), where the 200-unit box's centre (100,100) sits.
    cx, cy, r = 230 + z * 10, 130 - z * 5, 25 * z
    a = disc(460, 260, cx, cy, r)
    return np.stack([255 * (1 - a), 255 - 127 * a, 255 * (1 - a)], -1), (cx, cy)


def frames(z):
    T = f'{R}/triage/clip-edges'
    return {'master': load(f'{R}/triage/clip-edges-v/png/mst/{K}/{z}.png'),
            'prototype': load(f'{R}/triage/clip-edges-v/png/area/{K}/{z}.png'),
            'WebKit': load(f'{R}/fresh/refs/wk_{K}_{TAG[z]}.png'),
            'Chromium sw': load(f'{R}/fresh/refs/chr_{K}_{TAG[z]}.png'),
            'Chromium GPU': load(f'{T}/chg/chg_clip-path-variation-28_{TAG[z]}.png'),
            'Firefox': load(f'{R}/fresh/refs/ff_{K}_{TAG[z]}.png')}


if __name__ == '__main__':
    yy, xx = np.mgrid[0:260, 0:460] + 0.5
    names = list(frames(1))
    print('zoom  ' + ''.join(f'{n:>22s}' for n in names) + '   (px > 8/255 (max) [on the diagonals])')
    for z in sorted(TAG):
        ex, (cx, cy) = exact(z)
        ang = np.degrees(np.arctan2(yy - cy, xx - cx)) % 90
        diag = (ang > 30) & (ang < 60)
        cells = []
        for n, im in frames(z).items():
            if im is None:
                cells.append(f'{"-":>22s}')
                continue
            d = np.abs(im - ex).max(-1)
            off = d > 8
            cells.append(f'{f"{int(off.sum())} ({d.max():.0f}) [{int((off & diag).sum())}]":>22s}')
        print(f'{z:<6g}' + ''.join(cells))
    print()
    for z in sorted(TAG):
        ex, (cx, cy) = exact(z)
        f = frames(z)
        m, wk = f['master'], f['WebKit']
        ramp = np.clip(0.5 - (np.hypot(xx - cx, yy - cy) - 25 * z), 0, 1)
        near = np.abs(np.hypot(xx - cx, yy - cy) - 25 * z) < 2
        r16 = load(f'{R}/triage/clip-edges-v/png/r16/v28_16/{z:g}.png')
        apart = np.abs(m - wk).max(-1) > 8
        opp = apart & ((m[..., 0] - ex[..., 0]) * (wk[..., 0] - ex[..., 0]) < 0)
        ang = np.degrees(np.arctan2(yy - cy, xx - cx)) % 90
        off = np.abs(m - ex).max(-1) > 8
        idr = load(f'{R}/triage/clip-edges/area/id_{K}_{TAG[z]}.png')
        print(f'{z:<6g} master vs the ramp {np.abs(m[..., 0] - 255 * (1 - ramp))[near].max():.2f}/255; 16 arcs '
              f'{"bit-identical" if r16 is not None and np.array_equal(r16, m) else "DIFFERENT"}; master vs WebKit '
              f'{int(apart.sum())} px apart, {int(opp.sum())} with errors of opposite sign; master off: '
              f'{int((off & (ang > 30) & (ang < 60)).sum())} at 30-60, {int((off & (((ang > 15) & (ang <= 30)) | ((ang >= 60) & (ang < 75)))).sum())} '
              f'at 15-30/60-75; area reference vs exact {np.abs(idr - ex).max():.1f}/255')
