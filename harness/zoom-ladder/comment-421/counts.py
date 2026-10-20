#!/usr/bin/env python3
"""counts.py: the #421 comment's numbers for corpus/firefox lists-empty-state-light, per ladder zoom.

For master 06243b80 (the ladder's frames, identical to fresh renders at every step) and the #421 prototype
(harness/round-cap-tessellation/prototype.patch, rendered fresh at each zoom from the firefox-artwork triage's
experiment_with_421_prototype.patch, the same prototype plus switches left off):
  wk      px more than 8/255 off WebKit (macOS 27.2) in the whole 460 x 260 frame
  corner  of those, the ones lighter than WebKit within 2.2 user units of a checkbox vertex (the round joins)
  inner   of the corner px, the ones inside the square's centreline (the join's inner side; the rest are outer)
  other   the rest (from zoom 0.75 up all darker than WebKit, mostly at the pill outlines' ends)
  best    px off the nearest browser (Chromium 131 / Firefox / WebKit), the ladder's own test (fails above 24)
and how far WebKit and Chromium themselves are from the area reference (Chromium at 8x, box-averaged)."""
import os, re, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.expanduser('~/src/femtovg-wt/da/harness/corpus_run'))
from zoom_ladder import LADDER, FRAMING_OF

KEY = 'corpus__firefox__lists-empty-state-light'
Z = os.path.expanduser('~/src/femtovg-wt/runs/zoom')
T = f'{Z}/triage/firefox-artwork'
svg = open(os.path.expanduser('~/src/femtovg-wt/da/corpus/firefox/lists-empty-state-light.svg')).read()
boxes = []
for m in re.finditer(r'<path d="([^"]+)"([^>]*)>', svg):
    d, attrs = m.groups()
    if d.count('L') == 4 and 'C' not in d and 'linejoin="round"' in attrs:
        n = list(map(float, re.findall(r'-?\d+\.?\d*', d)))
        boxes.append([(n[i], n[i + 1]) for i in range(0, 8, 2)])
S1 = 200 / 110  # harness framing: the 110-unit viewBox in a 200 px box at (130, 30), zoom about (230, 130)


def load(p):
    return np.asarray(Image.open(p).convert('RGB'), dtype=np.int32) if os.path.exists(p) else None


def n8(a, b):
    return int((np.abs(a - b).max(axis=2) > 8).sum())


def inside(poly, u, v):
    c = False
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        if (y1 > v) != (y2 > v) and u < x1 + (v - y1) * (x2 - x1) / (y2 - y1):
            c = not c
    return c


print(f'{len(boxes)} checkboxes')
print('zoom  | master: wk corner inner other best | prototype: wk corner inner other best | WebKit, Chromium vs area')
for z in [0.25, 0.33, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2, 3, 4]:
    fr = FRAMING_OF[z]
    refs = {b: load(f'{Z}/fresh/refs/{b}_{KEY}_{fr}.png') for b in ('chr', 'ff', 'wk')}
    area = load(f'{T}/area/id8_{KEY}_{fr}.png')
    row = f'{z:<5} |'
    for frame in (load(f'{Z}/png/zl_zm_svg/{KEY}/{LADDER.index(z):02}.png'), load(f'{T}/var/le_p421_{fr}.ppm')):
        wk = refs['wk']
        m = np.abs(frame - wk).max(axis=2)
        lighter = (frame - wk).mean(axis=2) > 0
        corner = inner = 0
        for y, x in zip(*np.nonzero(m > 8)):
            u = ((230 + (x + 0.5 - 230) / z) - 130) / S1
            v = ((130 + (y + 0.5 - 130) / z) - 30) / S1
            dist, box = min(((np.hypot(u - px, v - py), b) for b in boxes for px, py in b), key=lambda t: t[0])
            if lighter[y, x] and dist < 2.2:
                corner += 1
                inner += inside(box, u, v)
        best = min((n8(frame, r), b) for b, r in refs.items() if r is not None)
        row += f' {int((m > 8).sum()):4} {corner:4} {inner:4} {int((m > 8).sum()) - corner:4} {best[0]:4} {best[1]:3} |'
    row += f' {n8(refs["wk"], area):4} {n8(refs["chr"], area):4}'
    print(row)
