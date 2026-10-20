#!/usr/bin/env python3
"""Animated strips of a zoom gesture, as #312's: one frame per step of zoom_ladder.py's ladder.

  zoom_strip.py OUT.gif key=KEY build=BUILD [mode=svg] [refs=DIR] [panels=femtovg,chr,ff,diff_chr]
                [crop=x,y,w,h] [scale=N] [steps=0,1,2] [ms=700] [label=TEXT]

Panels, left to right, each labelled: femtovg (the ladder's frame), fresh (a fresh process's frame of that zoom),
chr / ff / wk (the browser's frame of that zoom), diff_<chr|ff|wk|fresh> (where the ladder frame is more than 8/255
off that frame: red, with the difference amplified 4x in grey below it). crop= cuts every panel to one rectangle of
the frame and scale= enlarges it (nearest). Writes OUT.gif and OUT.webp (lossless)."""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from common import OUT
from zoom_ladder import LADDER, FRAMING_OF

opts = dict(a.split('=', 1) for a in sys.argv[2:])
out = sys.argv[1]
key, build, mode = opts['key'], opts['build'], opts.get('mode', 'svg')
refs = opts.get('refs', f'{OUT}/fresh/refs')
panels = opts.get('panels', 'femtovg,chr,ff,diff_chr').split(',')
crop = [int(v) for v in opts['crop'].split(',')] if 'crop' in opts else None
scale = int(opts.get('scale', 1))
steps = [int(s) for s in opts['steps'].split(',')] if 'steps' in opts else list(range(len(LADDER)))
src = f'{OUT}/png/zl_{build}_{mode}/{key}'
NAMES = {'femtovg': 'femtovg master', 'fresh': 'fresh canvas at this zoom', 'chr': 'Chromium 131', 'ff': 'Firefox',
         'wk': 'WebKit (macOS)'}
try:
    font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 14)
except OSError:
    font = ImageFont.load_default()


def load(path):
    return np.asarray(Image.open(path).convert('RGB'), dtype=np.int16) if os.path.exists(path) else None


def frame_of(name, step):
    zoom = LADDER[step]
    if name == 'femtovg':
        return load(f'{src}/{step:02}.png')
    if name == 'fresh':
        return load(f'{src}/00.png') if zoom == 1 else load(f'{src}/fresh_{FRAMING_OF[zoom]}.png')
    return load(f'{refs}/{name}_{key}_{FRAMING_OF[zoom]}.png')


def cut(a):
    if crop:
        x, y, w, h = crop
        a = a[y:y + h, x:x + w]
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    return im.resize((im.width * scale, im.height * scale), Image.NEAREST) if scale > 1 else im


frames = []
for step in steps:
    tiles = []
    base = frame_of('femtovg', step)
    for name in panels:
        if name.startswith('diff_'):
            other = frame_of(name[5:], step)
            if other is None or base is None:
                tiles.append((f'vs {NAMES[name[5:]]}: no frame', None))
                continue
            h, w = min(base.shape[0], other.shape[0]), min(base.shape[1], other.shape[1])
            d = np.abs(base[:h, :w] - other[:h, :w]).max(axis=2)
            img = np.stack([np.clip(d * 4, 0, 255)] * 3, -1)
            img[d > 8] = [230, 30, 30]
            tiles.append((f'> 8/255 vs {NAMES[name[5:]].split(" ")[0]}: {int((d > 8).sum())} px', img))
        else:
            tiles.append((NAMES[name], frame_of(name, step)))
    ims = [(t, cut(a) if a is not None else None) for t, a in tiles]
    w = max(im.width for _, im in ims if im is not None)
    h = max(im.height for _, im in ims if im is not None)
    pad, top = 8, 40
    canvas = Image.new('RGB', (len(ims) * (w + pad) + pad, h + top + pad), (40, 40, 40))
    draw = ImageDraw.Draw(canvas)
    head = f'zoom {LADDER[step]:g}  (step {step + 1} of {len(LADDER)}: ' + ' > '.join(f'{z:g}' for z in LADDER) + ')'
    draw.text((pad, 4), opts.get('label', key) + '   ' + head, fill=(255, 255, 255), font=font)
    for i, (t, im) in enumerate(ims):
        x = pad + i * (w + pad)
        draw.text((x, 22), t, fill=(220, 220, 220), font=font)
        if im is not None:
            canvas.paste(im, (x, top))
    frames.append(canvas)
ms = int(opts.get('ms', 700))
frames[0].save(out, save_all=True, append_images=frames[1:], duration=ms, loop=0, optimize=True)
frames[0].save(os.path.splitext(out)[0] + '.webp', save_all=True, append_images=frames[1:], duration=ms, loop=0,
               lossless=True, method=4)
print(out, len(frames), 'frames', frames[0].size)
