#!/usr/bin/env python3
"""Five-column evidence strip for an issue comment: before | after | reference | before vs reference |
after vs reference. A difference panel is white where the frame is within 8/255 of the reference, orange from 9
to 20 and red beyond; the caption gives the share of the whole frame beyond 20/255.

  strip.py OUT.png BEFORE.png=label AFTER.png=label REF.png=label [box=X,Y,W,H] [zoom=N] [note=TEXT]"""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

out, *rest = sys.argv[1:]
files = [a.split('=', 1) for a in rest if '=' in a and a.split('=', 1)[0].endswith('.png')]
opts = dict(a.split('=', 1) for a in rest if '=' in a and not a.split('=', 1)[0].endswith('.png'))
(bf, bl), (af, al), (rf, rl) = files
load = lambda f: np.asarray(Image.open(f).convert('RGB')).astype(np.int16)
b, a, r = load(bf), load(af), load(rf)
box = [int(v) for v in opts['box'].split(',')] if 'box' in opts else [0, 0, r.shape[1], r.shape[0]]
zoom = int(opts.get('zoom', 1))
share = lambda im: 100 * (np.abs(im - r).max(2) > 20).mean()


def diff(im):
    d = np.abs(im - r).max(2)
    p = np.full(im.shape, 255, np.uint8)
    p[d > 8] = (255, 170, 60)
    p[d > 20] = (220, 30, 40)
    return p


def crop(p):
    x, y, w, h = box
    return Image.fromarray(np.asarray(p, np.uint8)[y:y + h, x:x + w]).resize((w * zoom, h * zoom), Image.NEAREST)


panels = [(crop(b), bl), (crop(a), al), (crop(r), rl),
          (crop(diff(b)), f'{bl} vs {rl}: {share(b):.2f} %'), (crop(diff(a)), f'{al} vs {rl}: {share(a):.2f} %')]
font = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 22)
pw, ph, gap, top = panels[0][0].width, panels[0][0].height, 12, 34
note = opts.get('note')
sheet = Image.new('RGB', (len(panels) * (pw + gap) - gap, top + ph + (30 if note else 0)), 'white')
g = ImageDraw.Draw(sheet)
for i, (p, label) in enumerate(panels):
    x = i * (pw + gap)
    sheet.paste(p, (x, top))
    g.rectangle([x - 1, top - 1, x + pw, top + ph], outline=(200, 200, 200))
    g.text((x, 6), label, fill=(20, 20, 20), font=font)
if note:
    g.text((0, top + ph + 6), note, fill=(90, 90, 90), font=font)
sheet.save(out)
print(out, sheet.size, f'before {share(b):.2f} %, after {share(a):.2f} %')
