#!/usr/bin/env python3
"""BuseyBench strip for narrow screens: where 0.27 and 0.28 differ from Chromium, and the 0.28 render."""
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
R = '/Users/matt/src/femtovg-wt/runs/rel028/'
BG, INK, DIM, RED = (246, 248, 250), (31, 35, 40), (90, 98, 108), (220, 30, 40)
F = lambda s, bold=False: ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', s, index=1 if bold else 0)
P, G = 420, 28  # panel size, gutter
crop = (100, 30, 980, 910)  # the face, in the 1080 px box


def box(f):
    return Image.open(R + f).convert('RGB').crop((420, 0, 1500, 1080))


old, new, ref = box('v027_gpt-6-astra.ppm'), box('v028_gpt-6-astra.ppm'), box('chr_gpt-6-astra.png')
a = {k: np.asarray(v).astype(int) for k, v in (('old', old), ('new', new), ('ref', ref))}


def diff_panel(build):
    off = np.abs(a[build] - a['ref']).max(2) > 20
    share = 100 * off.mean()
    # A pixel off stays visible at phone size: grow it 1 px, then keep any off pixel of a reduced block.
    mask = Image.fromarray((off * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3)).crop(crop)
    mask = mask.resize((P, P), Image.BOX).point(lambda v: 255 if v > 0 else 0)
    # A faint copy of the reference shows where on the face the differences are.
    ghost = ref.crop(crop).resize((P, P), Image.LANCZOS).convert('L').point(lambda v: 225 + v * 30 // 255)
    panel = Image.merge('RGB', [ghost] * 3)
    panel.paste(Image.new('RGB', (P, P), RED), (0, 0), mask)
    return panel, share


(d_old, s_old), (d_new, s_new) = diff_panel('old'), diff_panel('new')
render = new.crop(crop).resize((P, P), Image.LANCZOS)
pct = lambda v: f'{v:.2f} %' if v < 1 else f'{v:.1f} %'
cols = [(d_old, '0.27 vs Chromium', f'{pct(s_old)} of pixels off'),
        (d_new, '0.28 vs Chromium', f'{pct(s_new)} of pixels off'),
        (render, 'femtovg 0.28', 'BuseyBench GPT-6 Astra')]
head, foot = 70, 62
s = Image.new('RGB', (3 * P + 4 * G, head + P + foot), BG)
d = ImageDraw.Draw(s)
for k, (im, t, n) in enumerate(cols):
    x = G + k * (P + G)
    d.text((x, 18), t, font=F(36, True), fill=INK)
    s.paste(im, (x, head))
    d.text((x, head + P + 12), n, font=F(32), fill=RED if k < 2 else DIM)
s.save(R + 'out/femtovg-0.28-buseybench.png')
print(s.size, pct(s_old), pct(s_new))
