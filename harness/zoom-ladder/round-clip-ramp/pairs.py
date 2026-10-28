#!/usr/bin/env python3
"""The zoom ladder's failing (file, zoom) pairs that go through a round clip shape, on femtovg master 06243b80 and
with the prototype: a pair fails when the frame is more than 8/255 off each browser's frame of that zoom in more
than 24 pixels (zoom_ladder.py's pass mark). For each pair still failing with the prototype: is the area reference
itself that far off the nearest browser (then the residual is that browser's own error), or not (then: how many px
the browser is off the area, and in how many of the residual px both are within 8/255 of it, two errors that add up)?

Frames: master and prototype rendered at each zoom by render.sh with _logos_full_master_v (bit-identical to the
ladder's frames on all 165 frames here) and _logos_full_area_v (corner-area-on-06243b80.patch). Browser frames are
the ladder's (fresh/refs); the area reference is Chromium 131 on the GPU at 8x, averaged.

  RUNS_ZOOM=~/src/femtovg-wt/runs/zoom pairs.py"""
import json, os, sys
import numpy as np
from PIL import Image

R = os.environ.get('RUNS_ZOOM', os.path.expanduser('~/src/femtovg-wt/runs/zoom'))
TAG = {1: 'z1', 1.25: 'z125', 1.5: 'z15', 1.75: 'z175', 2: 'z2', 3: 'z3', 4: 'z4', 0.75: 'z075', 0.5: 'z05',
       0.33: 'z033', 0.25: 'z025'}
LADDER = [1, 1.25, 1.5, 1.75, 2, 3, 4, 3, 2, 1.75, 1.5, 1.25, 1, 0.75, 0.5, 0.33, 0.25, 0.33, 0.5, 0.75, 1]
V = f'{R}/triage/clip-edges-v/png'
W = f'{R}/drafts/N6-round-clip-ramp/work'
FEB = 'corpus__blend-probes__feblend-in-clipped-layer'


def load(p):
    return np.asarray(Image.open(p).convert('RGB'), dtype=np.int16) if os.path.exists(p) else None


def beyond(a, b):
    return None if a is None or b is None else int((np.abs(a - b).max(-1) > 8).sum())


def frame(tag, k, z):
    return load(f'{W}/png/{tag}/{k}/{z:g}.png' if k == FEB else f'{V}/{tag}/{k}/{z:g}.png')


def area(k, z):
    if k == FEB:
        for p in (f'{W}/area/id_{k}_{TAG[z]}.png', f'{R}/triage/thin-frame-stroke-fractional/area/area_{k}_{TAG[z]}.png'):
            if os.path.exists(p):
                return load(p)
        return None
    return load(f'{R}/triage/clip-edges/area/id_{k}_{TAG[z]}.png')


C = json.load(open(f'{R}/triage/clusters_compact.json'))
files = [f for f in C['clip-edges'] if not any(s in f['key'] for s in ('thin-ring', 'concentric', 'multiple-children'))]
files += [f for f in C['thin-frame-stroke-fractional'] if f['key'] == FEB]
same = total = 0
before = after = own = summed = 0
for f in files:
    k = f['key']
    for z in TAG:
        m, l = frame('mst', k, z), load(f'{R}/png/zl_zm_svg/{k}/{LADDER.index(z):02d}.png')
        total += 1
        same += m is not None and l is not None and np.array_equal(m, l)
    cells = []
    for z, *_ in f['bad']:
        refs = [load(f'{R}/fresh/refs/{b}_{k}_{TAG[z]}.png') for b in ('chr', 'ff', 'wk')]
        mb = min(v for v in (beyond(frame('mst', k, z), r) for r in refs) if v is not None)
        ab = min(v for v in (beyond(frame('area', k, z), r) for r in refs) if v is not None)
        before += mb > 24
        after += ab > 24
        note = ''
        if ab > 24 and k == FEB:
            # The clip is a circle of 60 units at the box's centre, which sits on the frame's (230,130).
            d = np.abs(frame('area', k, z) - refs[2]).max(-1)
            ys, xs = np.nonzero(d > 8)
            ang = np.degrees(np.arctan2(ys + 0.5 - 130, xs + 0.5 - 230)) % 90
            edge = np.abs(np.hypot(ys + 0.5 - 130, xs + 0.5 - 230) - 60 * z) < 1.5
            axis = edge & ((ang < 15) | (ang > 75))
            moved = int(np.abs(frame('area', k, z) - frame('mst', k, z)).max(-1)[ys[axis], xs[axis]].max())
            note = (f' (not classified: {int(axis.sum())} of the {len(xs)} px off WebKit lie on the clip\'s edge within 15 degrees '
                    f'of an axis, where the ramp is nearly exact; the prototype moves them by at most {moved}/255)')
        elif ab > 24:
            ar = min(v for v in (beyond(area(k, z), r) for r in refs) if v is not None)
            own += ar > 24
            summed += ar <= 24
            if ar > 24:
                note = f' (area {ar}: browser off the area)'
            else:
                # The browser nearest the prototype: its own px off the area, and the residual px where both are
                # within 8/255 of the area, two errors that add up.
                a, p = area(k, z), frame('area', k, z)
                r = min((r for r in refs if r is not None), key=lambda r: beyond(p, r))
                both = (np.abs(p - r).max(-1) > 8) & (np.abs(p - a).max(-1) <= 8) & (np.abs(r - a).max(-1) <= 8)
                note = (f' (area {beyond(r, a)}: the browser is off the area within the pass mark; in {int(both.sum())} px both '
                        f'are within 8/255 of the area and add up)')
        cells.append(f'{z:g}: {mb} -> {ab}{note}')
    big = [(np.abs(frame(t, k, z) - area(k, z)).max(), t) for z in TAG for t in ('mst', 'area') if area(k, z) is not None]
    print(k.split('__')[-1], f"(largest difference from the area reference over the zooms: master "
          f"{max(d for d, t in big if t == 'mst')}, prototype {max(d for d, t in big if t == 'area')})")
    for c in cells:
        print('   ', c)
print(f'master frames bit-identical to the ladder: {same} / {total}')
print(f'failing pairs: master {before}, prototype {after}; of those left, the area itself fails against the nearest '
      f'browser in {own}, the nearest browser is within the pass mark of the area in {summed}')
