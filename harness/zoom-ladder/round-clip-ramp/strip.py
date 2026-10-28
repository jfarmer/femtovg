#!/usr/bin/env python3
"""The zoom-ladder strip, zoom-ladder/round-clip-ramp/strip.gif and .webp: clip-path-variation-28 at each of the 21
steps of zoom_ladder.py's ladder, in a 40 x 40 window that follows the circle's upper-right diagonal (the whole circle
while it is small), 4x. Panels: before (femtovg master 06243b80) | after (the prototype) | WebKit | before vs WebKit |
after vs WebKit | before vs the exact area | after vs the exact area. Difference panels as zoom_strip.py draws them:
red where more than 8/255 off, the difference amplified 4x in grey elsewhere; their labels count the whole frame.

  strip.py [OUT.gif]"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from measure import exact, R, K

LADDER = [1, 1.25, 1.5, 1.75, 2, 3, 4, 3, 2, 1.75, 1.5, 1.25, 1, 0.75, 0.5, 0.33, 0.25, 0.33, 0.5, 0.75, 1]
TAG = {1: 'z1', 1.25: 'z125', 1.5: 'z15', 1.75: 'z175', 2: 'z2', 3: 'z3', 4: 'z4', 0.75: 'z075', 0.5: 'z05',
       0.33: 'z033', 0.25: 'z025'}
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'strip.gif')
font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 14)
WIN, SCALE = 40, 4


def load(p):
    return np.asarray(Image.open(p).convert('RGB'), dtype=np.float64)


def window(z):
    cx, cy, r = 230 + 10 * z, 130 - 5 * z, 25 * z
    t = min(max((r - 15) / 15, 0), 1)
    x, y = cx + 0.7071 * r * t, cy - 0.7071 * r * t
    return int(round(x - WIN / 2)), int(round(y - WIN / 2))


def cut(a, z):
    x, y = window(z)
    return Image.fromarray(np.clip(np.rint(a[y:y + WIN, x:x + WIN]), 0, 255).astype(np.uint8)).resize(
        (WIN * SCALE, WIN * SCALE), Image.NEAREST)


def diff(a, b):
    d = np.abs(a - b).max(axis=2)
    img = np.stack([np.clip(d * 4, 0, 255)] * 3, -1)
    img[d > 8] = [230, 30, 30]
    return img, int((d > 8).sum())


cache = {}
frames = []
for step, z in enumerate(LADDER):
    if z not in cache:
        b = load(f'{R}/triage/clip-edges-v/png/mst/{K}/{z:g}.png')
        a = load(f'{R}/triage/clip-edges-v/png/area/{K}/{z:g}.png')
        wk = load(f'{R}/fresh/refs/wk_{K}_{TAG[z]}.png')
        ex = exact(z)[0]
        cache[z] = (b, a, wk, ex)
    b, a, wk, ex = cache[z]
    tiles = [('before:', 'master 06243b80', b), ('after:', 'prototype', a), ('WebKit', '(macOS 27.2)', wk)]
    for name, im, ref, rname in (('before', b, wk, 'WebKit'), ('after', a, wk, 'WebKit'),
                                 ('before', b, ex, 'exact area'), ('after', a, ex, 'exact area')):
        img, n = diff(im, ref)
        tiles.append((f'{name} vs {rname}', f'{n} px > 8/255', img))
    w = h = WIN * SCALE
    pad, top = 8, 62
    canvas = Image.new('RGB', (len(tiles) * (w + pad) + pad, h + top + pad), (40, 40, 40))
    draw = ImageDraw.Draw(canvas)
    head = (f'clip-path-variation-28   zoom {z:g}   (step {step + 1} of {len(LADDER)}: ' + ' > '.join(f'{v:g}' for v in LADDER)
            + ')')
    draw.text((pad, 4), head, fill=(255, 255, 255), font=font)
    for i, (t, t2, im) in enumerate(tiles):
        x = pad + i * (w + pad)
        draw.text((x, 24), t, fill=(220, 220, 220), font=font)
        draw.text((x, 41), t2, fill=(220, 220, 220), font=font)
        canvas.paste(cut(im, z), (x, top))
    frames.append(canvas)
frames[0].save(out, save_all=True, append_images=frames[1:], duration=700, loop=0, optimize=True)
frames[0].save(os.path.splitext(out)[0] + '.webp', save_all=True, append_images=frames[1:], duration=700, loop=0,
               lossless=True, method=4)
print(out, len(frames), 'frames', frames[0].size)
