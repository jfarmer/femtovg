#!/usr/bin/env python3
"""0.28 release-notes strips from the renders in this directory."""
import numpy as np
from PIL import Image, ImageDraw, ImageFont
R = '/Users/matt/src/femtovg-wt/runs/rel028/'
BG, INK, DIM = (246, 248, 250), (31, 35, 40), (101, 109, 118)
F = lambda s, bold=False: ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', s, index=1 if bold else 0)
G = 24  # gutter


def img(f):
    return Image.open(R + f).convert('RGB')


def off(a, b):
    a, b = (np.asarray(x).astype(int) for x in (a, b))
    return 100 * (np.abs(a - b).max(2) > 20).mean()


def pct(v):
    return f'{v:.2f} %' if v < 1 else f'{v:.1f} %'


def columns(out, panels, heads, notes, insets=None, inset_label=None):
    """panels: three images of one size; notes: a caption under each."""
    w, h = panels[0].size
    head_h, note_h = 52, 40
    ih = insets[0].height + 44 if insets else 0
    W = 3 * w + 4 * G
    s = Image.new('RGB', (W, head_h + h + note_h + ih + G), BG)
    d = ImageDraw.Draw(s)
    for k, (p, t, n) in enumerate(zip(panels, heads, notes)):
        x = G + k * (w + G)
        d.text((x, 16), t, font=F(24, True), fill=INK)
        s.paste(p, (x, head_h))
        d.text((x, head_h + h + 10), n, font=F(19), fill=DIM)
        if insets:
            if k == 0:
                d.text((x, head_h + h + note_h + 6), inset_label, font=F(17), fill=DIM)
            s.paste(insets[k], (x, head_h + h + note_h + 34))
    s.save(R + 'out/' + out)
    print(out, s.size)


# BuseyBench GPT-6 Astra, 1080p frame, face crop.
box = (420 + 100, 30, 420 + 980, 910)
b = [img(f).crop((420, 0, 1500, 1080)) for f in ('v027_gpt-6-astra.ppm', 'v028_gpt-6-astra.ppm', 'chr_gpt-6-astra.png')]
o = [off(b[0], b[2]), off(b[1], b[2])]
p = [img(f).crop(box).resize((560, 560), Image.LANCZOS) for f in ('v027_gpt-6-astra.ppm', 'v028_gpt-6-astra.ppm', 'chr_gpt-6-astra.png')]
columns('femtovg-0.28-buseybench.png', p, ['femtovg 0.27', 'femtovg 0.28', 'Chromium'],
        [f'{pct(o[0])} of pixels off Chromium', f'{pct(o[1])} of pixels off Chromium', 'reference'])

# SolidJS banner at 350 x 70, shown 3x.
names = [('femtovg 0.27', 'v027_b350.ppm'), ('femtovg 0.28', 'v028_b350.ppm'), ('Chromium', 'chr_b350.png')]
ims = [img(f) for _, f in names]
o = [off(ims[0], ims[2]), off(ims[1], ims[2])]
Z, lab = 3, 230
bw, bh = 350 * Z, 70 * Z
s = Image.new('RGB', (lab + bw + 2 * G, 3 * (bh + G) + G), BG)
d = ImageDraw.Draw(s)
for k, ((t, _), im) in enumerate(zip(names, ims)):
    y = G + k * (bh + G)
    d.text((G, y + 60), t, font=F(24, True), fill=INK)
    d.text((G, y + 96), [f'{pct(o[0])} off', f'{pct(o[1])} off', 'reference'][k], font=F(19), fill=DIM)
    s.paste(im.resize((bw, bh), Image.NEAREST), (lab + G, y))
s.save(R + 'out/femtovg-0.28-solidjs-banner.png')
print('banner', s.size)

# Text: RTL glyph runs with a gradient and a glow, right-aligned at x < 0.
names = ['text_v027.ppm', 'text_v028.ppm', 'text_ff.png']
ims = [img(f) for f in names]
o = [off(ims[0], ims[2]), off(ims[1], ims[2])]
p = [i.crop((90, 30, 590, 345)).resize((560, 353), Image.LANCZOS) for i in ims]
ins = [i.crop((470, 300, 563, 324)).resize((560, 145), Image.NEAREST) for i in ims]
columns('femtovg-0.28-text.png', p, ['femtovg 0.27', 'femtovg 0.28', 'Firefox (Canvas 2D)'],
        [f'{pct(o[0])} of pixels off Firefox', f'{pct(o[1])} of pixels off Firefox', 'reference'],
        ins, 'glyph spacing at x < 0 with swash, 6x')
