#!/usr/bin/env python3
"""zoom_strip.py's strip with an after column: master | gate fix | WebKit | master vs WebKit | gate fix vs WebKit,
one frame per ladder step. A difference panel is red where the frame is more than 8/255 off WebKit, the difference
amplified 4x in grey below that; its count is over the whole 460x260 frame.

  strip5.py OUT.gif MASTER_DIR GATE_DIR REFS_DIR KEY steps=14,15,16 crop=x,y,w,h scale=N ms=N label=TEXT

MASTER_DIR holds the zm build's ladder frames (NN.png), GATE_DIR the proof build's with FV_GATE_FIX=1."""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

LADDER = [1, 1.25, 1.5, 1.75, 2, 3, 4, 3, 2, 1.75, 1.5, 1.25, 1, 0.75, 0.5, 0.33, 0.25, 0.33, 0.5, 0.75, 1]
FRAMING_OF = {1: 'z1', 1.25: 'z125', 1.5: 'z15', 1.75: 'z175', 2: 'z2', 3: 'z3', 4: 'z4', 0.75: 'z075', 0.5: 'z05',
              0.33: 'z033', 0.25: 'z025'}
out, master, gate, refs, key = sys.argv[1:6]
opts = dict(a.split('=', 1) for a in sys.argv[6:])
steps = [int(s) for s in opts['steps'].split(',')]
x0, y0, w0, h0 = (int(v) for v in opts['crop'].split(','))
scale = int(opts.get('scale', 1))
font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 14)


def load(path):
    return np.asarray(Image.open(path).convert('RGB'), dtype=np.int16)


def cut(a):
    im = Image.fromarray(np.clip(a[y0:y0 + h0, x0:x0 + w0], 0, 255).astype(np.uint8))
    return im.resize((w0 * scale, h0 * scale), Image.NEAREST)


def diff(a, b):
    d = np.abs(a - b).max(axis=2)
    img = np.stack([np.clip(d * 4, 0, 255)] * 3, -1)
    img[d > 8] = [230, 30, 30]
    return img, int((d > 8).sum())


frames = []
for step in steps:
    zoom = LADDER[step]
    m, g = load(f'{master}/{step:02}.png'), load(f'{gate}/{step:02}.png')
    wk = load(f'{refs}/wk_{key}_{FRAMING_OF[zoom]}.png')
    (dm, nm), (dg, ng) = diff(m, wk), diff(g, wk)
    tiles = [('femtovg master 06243b80', m), ('gate fix (prototype)', g), ('WebKit (macOS 27.2)', wk),
             (f'> 8/255 master vs WebKit: {nm} px', dm), (f'> 8/255 gate fix vs WebKit: {ng} px', dg)]
    ims = [(t, cut(a)) for t, a in tiles]
    w, h = ims[0][1].size
    pad, top = 8, 40
    canvas = Image.new('RGB', (len(ims) * (w + pad) + pad, h + top + pad), (40, 40, 40))
    draw = ImageDraw.Draw(canvas)
    head = f'zoom {zoom:g}  (step {step + 1} of {len(LADDER)}: ' + ' > '.join(f'{z:g}' for z in LADDER) + ')'
    draw.text((pad, 4), opts.get('label', key) + '   ' + head, fill=(255, 255, 255), font=font)
    for i, (t, im) in enumerate(ims):
        x = pad + i * (w + pad)
        draw.text((x, 22), t, fill=(220, 220, 220), font=font)
        canvas.paste(im, (x, top))
    frames.append(canvas)
ms = int(opts.get('ms', 1000))
# One palette for every GIF frame, with the difference panels' red in it: a palette made per frame lets a few red
# pixels (4 at 0.5) fall to a dark red.
stack = Image.new('RGB', (frames[0].width, frames[0].height * len(frames)))
for i, f in enumerate(frames):
    stack.paste(f, (0, i * f.height))
palette = Image.new('P', (1, 1))
palette.putpalette(stack.quantize(255, dither=Image.Dither.NONE).getpalette()[:255 * 3] + [230, 30, 30])
gif = [f.quantize(palette=palette, dither=Image.Dither.NONE) for f in frames]
gif[0].save(out, save_all=True, append_images=gif[1:], duration=ms, loop=0, optimize=True)
frames[0].save(os.path.splitext(out)[0] + '.webp', save_all=True, append_images=frames[1:], duration=ms, loop=0,
               lossless=True, method=4)
print(out, len(frames), 'frames', frames[0].size)
