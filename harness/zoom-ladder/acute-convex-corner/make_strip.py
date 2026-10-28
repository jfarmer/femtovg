#!/usr/bin/env python3
"""The issue's zoom-ladder strip, as zoom_strip.py's (one frame per step of zoom_ladder.py's ladder, #312) with the
panels stacked, since the sliver is 160 times as long as it is tall, and the prototype's frame added: femtovg master
06243b80 (the ladder's frame) | prototype (variants.patch at SV_V=4, its frame of that zoom) | Chromium 131 | WebKit |
master vs WebKit | prototype vs WebKit. A difference panel is red where the frame is more than 8/255 off WebKit, the
difference amplified 4x in grey elsewhere; its count is over the whole frame.

  make_strip.py OUT.gif   (writes OUT.gif and OUT.webp, lossless)"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1]
LADDER = [1, 1.25, 1.5, 1.75, 2, 3, 4, 3, 2, 1.75, 1.5, 1.25, 1, 0.75, 0.5, 0.33, 0.25, 0.33, 0.5, 0.75, 1]
FRAMING_OF = {1: 'z1', 1.25: 'z125', 1.5: 'z15', 1.75: 'z175', 2: 'z2', 3: 'z3', 4: 'z4', 0.75: 'z075', 0.5: 'z05',
              0.33: 'z033', 0.25: 'z025'}
X, Y, W, H, SCALE = 0, 128, 230, 8, 4  # the sliver's left half; it is symmetric about x = 230
font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 14)
small = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 13)


def load(name):
    return np.asarray(Image.open(f'{HERE}/frames/{name}').convert('RGB'), dtype=np.int16)


def cut(a):
    im = Image.fromarray(np.clip(a[Y:Y + H, X:X + W], 0, 255).astype(np.uint8))
    return im.resize((W * SCALE, H * SCALE), Image.NEAREST)


def diff(a, ref):
    d = np.abs(a - ref).max(axis=2)
    img = np.stack([np.clip(d * 4, 0, 255)] * 3, -1)
    img[d > 8] = [230, 30, 30]
    return img, int((d > 8).sum())


frames = []
pad, label_h, top = 8, 18, 46
pw, ph = W * SCALE, H * SCALE
for step, zoom in enumerate(LADDER):
    f = FRAMING_OF[zoom]
    master, proto, chr_, wk = (load(f'{k}_{f}.png') for k in ('master', 'prototype', 'chr', 'wk'))
    dm, nm = diff(master, wk)
    dp, np_ = diff(proto, wk)
    panels = [('femtovg master 06243b80', master), ('prototype (variants.patch, SV_V=4)', proto),
              ('Chromium 131 (Firefox 159 is identical at 3x and 4x)', chr_), ('WebKit (macOS 27.2)', wk),
              (f'> 8/255, master vs WebKit: {nm} px', dm), (f'> 8/255, prototype vs WebKit: {np_} px', dp)]
    canvas = Image.new('RGB', (pw + 2 * pad, top + len(panels) * (label_h + ph + 6) + pad), (40, 40, 40))
    draw = ImageDraw.Draw(canvas)
    draw.text((pad, 4), f'fill-path-subpixel-sliver-control.svg, left half (x 0-229, y 128-135, 4x)   zoom {zoom:g}  '
              f'(step {step + 1} of {len(LADDER)})', fill=(255, 255, 255), font=font)
    x = pad
    draw.text((x, 24), 'ladder:', fill=(170, 170, 170), font=small)
    x += small.getlength('ladder: ')
    for i, z in enumerate(LADDER):
        t = f'{z:g}' + (' > ' if i < len(LADDER) - 1 else '')
        draw.text((x, 24), t, fill=(255, 210, 60) if i == step else (170, 170, 170), font=small)
        x += small.getlength(t)
    y = top
    for label, a in panels:
        draw.text((pad, y), label, fill=(220, 220, 220), font=small)
        canvas.paste(cut(a), (pad, y + label_h))
        y += label_h + ph + 6
    frames.append(canvas)
ms = 700
frames[0].save(OUT, save_all=True, append_images=frames[1:], duration=ms, loop=0, optimize=True)
frames[0].save(os.path.splitext(OUT)[0] + '.webp', save_all=True, append_images=frames[1:], duration=ms, loop=0,
               lossless=True, method=4)
print(OUT, len(frames), 'frames', frames[0].size)
