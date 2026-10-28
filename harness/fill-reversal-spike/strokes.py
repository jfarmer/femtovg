#!/usr/bin/env python3
"""The same outlines stroked (ear-stroke.svg, cusp-stroke.svg, stroke-width 4) on master: pixels where femtovg has
more than 40/255 of ink and Chromium less than 8/255, and their extent.

  strokes.py RUN     (RUN/png/red/master_<name>_<framing>.png from render.py, RUN/refs/chr_frs__<name>_<framing>.png)"""
import sys
import numpy as np
from PIL import Image

RUN = sys.argv[1]


def ink(p):
    return 255.0 - np.asarray(Image.open(p).convert('L'), dtype=float)


for name in ('ear-stroke', 'cusp-stroke'):
    for fr in ('z2', 'hd'):
        a, c = ink(f'{RUN}/png/red/master_{name}_{fr}.png'), ink(f'{RUN}/refs/chr_frs__{name}_{fr}.png')
        ys, xs = np.nonzero((a > 40) & (c < 8))
        box = (xs.min(), ys.min(), xs.max(), ys.max()) if len(xs) else None
        print(f'{name} {fr}: {len(xs)} px, x {box[0]}-{box[2]}, y {box[1]}-{box[3]}' if box else f'{name} {fr}: none')
