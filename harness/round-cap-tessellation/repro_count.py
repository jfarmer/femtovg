#!/usr/bin/env python3
"""repro_count.py: repro.svg's whole frame at z1, z2 and hd: pixels more than 20/255 off the area reference, and off
all three browsers, for master (mstc), the count alone (capx3) and the prototype (caps), and each browser off the
area reference."""
import os
import numpy as np
from PIL import Image
OUT = os.environ['CORPUS_RUN_OUT']
L = lambda p: np.asarray(Image.open(p).convert('RGB'), np.int16)
for fr in ('z1', 'z2', 'hd'):
    ref = {t: L(f'{OUT}/refs/{t}_red__repro_{fr}.png') for t in ('chr', 'ff', 'wk', 'id')}
    off = lambda im, t: np.abs(im - ref[t]).max(2) > 20
    cells = []
    for t in ('mstc', 'capx3', 'caps'):
        im = L(f'{OUT}/png/{t}_red__repro_{fr}.png')
        cells.append(f'{t} {int(off(im, "id").sum())}/{int((off(im, "chr") & off(im, "ff") & off(im, "wk")).sum())}')
    cells += [f'{t} {int(off(ref[t], "id").sum())}' for t in ('chr', 'ff', 'wk')]
    print(f'{fr}: off the area / off all three: ' + ', '.join(cells))
