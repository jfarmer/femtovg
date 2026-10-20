#!/usr/bin/env python3
"""Five-column zoom-ladder strip: before | after | reference | before vs reference | after vs reference.

  strip151.py OUT.gif follow=CX,CY size=W,H scale=N [steps=0,1,...] [ms=700] label=TEXT
      before=PATTERN after=PATTERN ref=PATTERN [before_name=..] [after_name=..] [ref_name=..]

PATTERN takes {step} (ladder step, 00-20) and {fr} (framing, e.g. z175). follow= is a frame point at zoom 1; the
window of size W x H stays centred on it as the ladder zooms about the frame centre (230, 130), as mystrip.py does.
Difference panels follow zoom_strip.py: red where a frame is more than 8/255 off the reference, the difference
amplified 4x in grey elsewhere; the count is of pixels in the window. Writes OUT.gif and OUT.webp (lossless)."""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.expanduser('~/src/femtovg-wt/da/harness/corpus_run'))
from zoom_ladder import LADDER, FRAMING_OF

out = sys.argv[1]
o = dict(a.split('=', 1) for a in sys.argv[2:])
fx, fy = map(float, o['follow'].split(','))
w, h = map(int, o['size'].split(','))
s = int(o.get('scale', 6))
steps = [int(t) for t in o['steps'].split(',')] if 'steps' in o else list(range(len(LADDER)))
names = [o.get('before_name', 'before'), o.get('after_name', 'after'), o.get('ref_name', 'reference')]
font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 14)


def load(pattern, step):
    p = pattern.replace('{step}', f'{step:02}').replace('{fr}', FRAMING_OF[LADDER[step]])
    return np.asarray(Image.open(p).convert('RGB'), dtype=np.int16)


def diff(a, r):
    d = np.abs(a - r).max(axis=2)
    img = np.stack([np.clip(d * 4, 0, 255)] * 3, -1)
    img[d > 8] = [230, 30, 30]
    return img, int((d > 8).sum())


frames = []
for st in steps:
    z = LADDER[st]
    x = max(0, min(460 - w, int(round(230 + (fx - 230) * z - w / 2))))
    y = max(0, min(260 - h, int(round(130 + (fy - 130) * z - h / 2))))
    b, a, r = (load(o[k], st)[y:y + h, x:x + w] for k in ('before', 'after', 'ref'))
    db, nb = diff(b, r)
    da, na = diff(a, r)
    rn = names[2].split(' (')[0]
    tiles = [(names[0], b), (names[1], a), (names[2], r),
             (f'{names[0].split(" ")[0]} vs {rn}: {nb} px > 8/255', db), (f'{names[1].split(" ")[0]} vs {rn}: {na} px', da)]
    W, H, pad, top = w * s, h * s, 8, 42
    canvas = Image.new('RGB', (len(tiles) * (W + pad) + pad, H + top + pad), (40, 40, 40))
    d = ImageDraw.Draw(canvas)
    head = f'zoom {z:g}  (step {st + 1} of {len(LADDER)}: ' + ' > '.join(f'{v:g}' for v in LADDER) + ')'
    d.text((pad, 4), o.get('label', '') + '   ' + head, fill=(255, 255, 255), font=font)
    for i, (t, im) in enumerate(tiles):
        X = pad + i * (W + pad)
        d.text((X, 23), t, fill=(220, 220, 220), font=font)
        canvas.paste(Image.fromarray(np.clip(im, 0, 255).astype(np.uint8)).resize((W, H), Image.NEAREST), (X, top))
    frames.append(canvas)
ms = int(o.get('ms', 700))
frames[0].save(out, save_all=True, append_images=frames[1:], duration=ms, loop=0, optimize=True)
frames[0].save(os.path.splitext(out)[0] + '.webp', save_all=True, append_images=frames[1:], duration=ms, loop=0,
               lossless=True, method=4)
for st, f in zip(steps, frames):
    f.save(os.path.splitext(out)[0] + f'_{st:02}.png')
print(out, len(frames), frames[0].size)
