#!/usr/bin/env python3
"""Five-column sheet for the #151 comment: before | after | reference | before vs reference | after vs reference.
Difference panels as harness/corpus_run/sheet.py: white within 8/255, orange 9-20, red beyond; counts are whole-frame.

  sheet151.py OUT.png WORKDIR"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

out, W = sys.argv[1], sys.argv[2]
H = os.path.expanduser('~')
REFS = f'{H}/src/femtovg-wt/runs/zoom/fresh/refs'
LAD = f'{H}/src/femtovg-wt/runs/zoom/png/zl_zm_svg'
AREA = f'{H}/src/femtovg-wt/runs/zoom/triage/firefox-artwork-v/area'
REPRO = f'{H}/src/femtovg-wt/runs/zoom/triage/mask-thin-stroke-3x/repro'
MK = 'corpus__wpt__tests__mask-on-thin-stroked-path-userspaceonuse'
font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 14)
PROOF = 'AA pass writes stencil'
rows = [
    ("#151's paint with stencil strokes on (rgb 65,212,215 at 100/255, 12 px, square caps, bevel joins), pen path with "
     "points 2.5-4 px apart, zoom 1, x3; reference: Chromium 131 at 8x, averaged",
     f'{W}/pen_none.ppm', f'{W}/pen_fold.ppm', f'{AREA}/m151_bevel_s8.png',
     'master 06243b80', 'fold test (prototype)', 'area reference', 'area', (126, 64, 72, 132), 3),
    ('coincident butt ends, two subpaths: mask-on-thin-stroked-path-userspaceonuse at zoom 1.25, left end, x6; '
     'after = AA pass writes the stencil (proof, not a fix)',
     f'{LAD}/{MK}/01.png', f'{W}/mask_once_1.25.ppm', f'{REFS}/chr_{MK}_z125.png',
     'master 06243b80', PROOF, 'Chromium 131', 'Chromium', (150, 50, 40, 35), 6),
    ('abutting subpaths: M50 50 L100.5 50 M100.5 50 L150 50, width 20, zoom 1, x8; '
     'the seam goes from 75 % to 50 % coverage (Chromium 100 %)',
     f'{W}/abut_none.ppm', f'{W}/abut_once.ppm', f'{REPRO}/chr_fringe-abutting.png',
     'master 06243b80', PROOF, 'Chromium 131', 'Chromium', (215, 65, 30, 30), 8),
]


def ld(p):
    return np.asarray(Image.open(p).convert('RGB')).astype(int)


def diff(a, r):
    d = np.abs(a - r).max(-1)
    o = np.full(a.shape, 255, np.uint8)
    o[(d > 8) & (d <= 20)] = [255, 160, 0]
    o[d > 20] = [220, 30, 30]
    return o, int((d > 8).sum())


tiles = []
for cap, b, a, r, lb, la, lr, rn, box, z in rows:
    B, A, C = ld(b), ld(a), ld(r)
    db, nb = diff(B, C)
    da, na = diff(A, C)
    ims = [B.astype(np.uint8), A.astype(np.uint8), C.astype(np.uint8), db, da]
    labs = [lb, la, lr, f'master vs {rn}: {nb} px > 8/255', f'{la.split(" (")[0].split(" ")[0]} vs {rn}: {na} px']
    if la == PROOF:
        labs[4] = f'proof vs {rn}: {na} px'
    out_ims = []
    for im in ims:
        x, y, w, h = box
        p = Image.fromarray(im[y:y + h, x:x + w])
        out_ims.append(p.resize((p.width * z, p.height * z), Image.NEAREST))
    tiles.append((cap, out_ims, labs))
pad, top, lab = 8, 22, 20
width = max(sum(p.width for p in o) + pad * (len(o) + 1) for _, o, _ in tiles)
width = max(width, max(int(font.getlength(c)) + 2 * pad for c, _, _ in tiles))
height = sum(top + lab + max(p.height for p in o) + pad for _, o, _ in tiles) + pad
S = Image.new('RGB', (width, height), (40, 40, 40))
d = ImageDraw.Draw(S)
y = pad
for cap, o, labs in tiles:
    d.text((pad, y), cap, fill=(255, 255, 255), font=font)
    y += top
    x = pad
    for p, l in zip(o, labs):
        d.text((x, y), l, fill=(220, 220, 220), font=font)
        S.paste(p, (x, y + lab))
        x += p.width + pad
    y += lab + max(p.height for p in o) + pad
S.save(out)
print(out, S.size)
