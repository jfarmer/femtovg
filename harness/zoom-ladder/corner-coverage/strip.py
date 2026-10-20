#!/usr/bin/env python3
"""The zoom ladder as an animated strip, drawn as harness/corpus_run/zoom_strip.py draws it, but with the window
following one rect corner from step to step: the bottom-left corner of the rect at user (150, 70), its pixel 13 px
from the window's left and 6 from its top, so that the 1 px frame stays out of the window at every zoom. Panels: master 06243b80 (the ladder's frame) | all fills masked (all-masks-experiment.patch,
ZL_ALL_MASKS=1) | Chromium 131 | master vs Chromium | masked vs Chromium; a difference panel is red where the frame
is beyond 8/255 off Chromium, the difference amplified 4x in grey below that. The header counts the whole frame
against the nearest browser, as the ladder does. Writes OUT.gif and OUT.webp (lossless).

  strip.py OUT.gif"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1]
H = os.path.expanduser('~/src/femtovg-wt/runs/zoom')
KEY = 'wpt22__21-degenerate-paths-dashes-and-joins__resvg-dasharray-0-n-square-caps-ref'
LADDER = [1, 1.25, 1.5, 1.75, 2, 3, 4, 3, 2, 1.75, 1.5, 1.25, 1, 0.75, 0.5, 0.33, 0.25, 0.33, 0.5, 0.75, 1]
FR = {1: 'z1', 1.25: 'z125', 1.5: 'z15', 1.75: 'z175', 2: 'z2', 3: 'z3', 4: 'z4', 0.75: 'z075', 0.5: 'z05',
      0.33: 'z033', 0.25: 'z025'}
CW, CH, SCALE, UX, UY = 22, 13, 8, 150, 90
font = lambda s: ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', s)
F_HEAD, F_LAB = font(14), font(13)


def load(p):
    return np.asarray(Image.open(p).convert('RGB'), dtype=np.int16) if os.path.exists(p) else None


def n8(a, b):
    return int((np.abs(a - b).max(axis=2) > 8).sum())


frames = []
for step, z in enumerate(LADDER):
    m = load(f'{H}/png/zl_zm_svg/{KEY}/{step:02}.png')
    e = load(f'{H}/triage/dasharray/exp/mask_resvg-dasharray-0-n-square-caps-ref_{z:g}.png')
    refs = {b: load(f'{H}/fresh/refs/{b}_{KEY}_{FR[z]}.png') for b in ('chr', 'ff', 'wk')}
    refs = {b: r for b, r in refs.items() if r is not None}
    c = refs['chr']
    best_m, best_e = min(n8(m, r) for r in refs.values()), min(n8(e, r) for r in refs.values())
    cx, cy = int(np.floor(230 + (UX - 100) * z)), int(np.floor(130 + (UY - 100) * z))
    x0, y0 = cx - 13, cy - 6

    def cut(a):
        return a[y0:y0 + CH, x0:x0 + CW]

    def diff(a):
        d = np.abs(cut(a) - cut(c)).max(axis=2)
        img = np.stack([np.clip(d * 4, 0, 255)] * 3, -1)
        img[d > 8] = [230, 30, 30]
        return img, int((d > 8).sum())

    dm, km = diff(m)
    de, ke = diff(e)
    tiles = [('master 06243b80', cut(m)), ('all fills masked', cut(e)), ('Chromium 131', cut(c)),
             (f'master vs Chromium: {km} px', dm), (f'masked vs Chromium: {ke} px', de)]
    pw, ph, pad, top = CW * SCALE, CH * SCALE, 8, 64
    canvas = Image.new('RGB', (len(tiles) * (pw + pad) + pad, ph + top + pad), (40, 40, 40))
    draw = ImageDraw.Draw(canvas)
    verdict = lambda n: f'{n} px ({"fails" if n > 24 else "passes"})'
    draw.text((pad, 4), f'zoom {z:g}, step {step + 1} of {len(LADDER)}. Whole frame, px beyond 8/255 off the '
              f'nearest browser: master {verdict(best_m)}, masked {verdict(best_e)}', fill=(255, 255, 255),
              font=F_HEAD)
    x = pad
    for i, v in enumerate(LADDER):
        t = f'{v:g}' + (' > ' if i < len(LADDER) - 1 else '')
        draw.text((x, 23), t, fill=(255, 210, 0) if i == step else (150, 150, 150), font=F_HEAD)
        x += F_HEAD.getlength(t)
    for i, (label, a) in enumerate(tiles):
        assert F_LAB.getlength(label) <= pw + pad - 2, label
        px = pad + i * (pw + pad)
        draw.text((px, 44), label, fill=(220, 220, 220), font=F_LAB)
        im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).resize((pw, ph), Image.NEAREST)
        canvas.paste(im, (px, top))
    frames.append(canvas)
    print(f'step {step:2} zoom {z:<4g} crop ({x0},{y0}) master {km} masked {ke} in the crop; whole frame best '
          f'{best_m} -> {best_e}')
frames[0].save(OUT, save_all=True, append_images=frames[1:], duration=900, loop=0, optimize=True)
frames[0].save(os.path.splitext(OUT)[0] + '.webp', save_all=True, append_images=frames[1:], duration=900, loop=0,
               lossless=True, method=4)
print(OUT, len(frames), 'frames', frames[0].size)
