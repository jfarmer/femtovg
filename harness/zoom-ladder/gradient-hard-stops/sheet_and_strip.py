# Five-column sheet and zoom-ladder strip for the hard-stop issue:
#   before (master 06243b80) | after (4096-texel probe) | Chromium 131 | before vs Chromium | after vs Chromium
# Each panel is a window centred on the hard stop at that zoom (stop x = 230 + 32 * zoom for the 0.7 files,
# 230 for zero-offset-in-the-middle). Counts are whole-frame pixels more than 8/255 off Chromium.
# Inputs: the ladder's frames (png/zl_zm_svg), the probe's single-zoom frames (on master a single-zoom render is
# bit-identical to the ladder frame of that zoom), and the browsers' frames (fresh/refs).
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

R = os.path.expanduser('~/src/femtovg-wt/runs/zoom/')
PROBE = R + 'triage/gradient-hard-stops/out/p4096_'
OUTDIR = sys.argv[1] if len(sys.argv) > 1 else '.'
LADDER = [1, 1.25, 1.5, 1.75, 2, 3, 4, 3, 2, 1.75, 1.5, 1.25, 1, 0.75, 0.5, 0.33, 0.25, 0.33, 0.5, 0.75, 1]
FR = {1: 'z1', 1.25: 'z125', 1.5: 'z15', 1.75: 'z175', 2: 'z2', 3: 'z3', 4: 'z4', 0.75: 'z075', 0.5: 'z05',
      0.33: 'z033', 0.25: 'z025'}
G = 'wpt22__22-gradient-stops-and-recursion-guards__resvg-'
EO1 = (G + 'stops-with-equal-offset-1', 'stops-with-equal-offset-1 (0 red, 0.7 yellow, 0.7 green)', lambda z: 230 + 32 * z)
ZERO = (G + 'stop-zero-offset-in-the-middle', 'stop-zero-offset-in-the-middle (0.5 yellow, 0 green clamped to 0.5, 0.8 green)', lambda z: 230)
W, H, Y0, SCALE = 48, 16, 120, 4   # 192 x 64 panels: the sheet is about 1,000 px wide, so GitHub shows it near full size
font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 14)
small = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 13)


def load(p):
    return np.asarray(Image.open(p).convert('RGB')).astype(int)


def diff(a, b):
    d = np.abs(a - b).max(axis=2)
    img = np.stack([np.clip(d * 4, 0, 255)] * 3, -1)
    img[d > 8] = [230, 30, 30]
    return img, int((d > 8).sum())


def row(spec, zoom, head):
    key, label, stop = spec
    before = load(f'{R}png/zl_zm_svg/{key}/{LADDER.index(zoom):02d}.png')
    after = load(f'{PROBE}{key}_{FR[zoom]}.png')
    chrome = load(f'{R}fresh/refs/chr_{key}_{FR[zoom]}.png')
    db, nb = diff(before, chrome)
    da, na = diff(after, chrome)
    x0 = int(round(stop(zoom))) - W // 2
    tiles = [('femtovg master 06243b80', before), ('probe: 4096-texel texture', after), ('Chromium 131', chrome),
             (f'master vs Chromium: {nb} px', db), (f'probe vs Chromium: {na} px', da)]
    pad, top = 8, 60
    pw, ph = W * SCALE, H * SCALE
    c = Image.new('RGB', (len(tiles) * (pw + pad) + pad, ph + top + pad), (40, 40, 40))
    dr = ImageDraw.Draw(c)
    dr.text((pad, 4), f'{label}   zoom {zoom:g}' + (f'   {head}' if head else ''), fill=(255, 255, 255), font=font)
    dr.text((pad, 22), f'window x {x0}..{x0 + W}, y {Y0}..{Y0 + H}   red: more than 8/255 off Chromium; counts over the whole frame',
            fill=(200, 200, 200), font=small)
    for i, (t, a) in enumerate(tiles):
        im = Image.fromarray(np.clip(a[Y0:Y0 + H, x0:x0 + W], 0, 255).astype(np.uint8))
        x = pad + i * (pw + pad)
        dr.text((x, 41), t, fill=(220, 220, 220), font=small)
        c.paste(im.resize((pw, ph), Image.NEAREST), (x, top))
    return c


# Static sheet: the 0.7 files at 1, 1.25, 2, 4; zero-offset-in-the-middle at 1.5, 1.75, 4.
rows = [row(EO1, z, '') for z in (1, 1.25, 2, 4)] + [row(ZERO, z, '') for z in (1.5, 1.75, 4)]
sheet = Image.new('RGB', (rows[0].width, sum(r.height for r in rows)), (40, 40, 40))
y = 0
for r in rows:
    sheet.paste(r, (0, y))
    y += r.height
sheet.save(f'{OUTDIR}/sheet.png', optimize=True)

# Zoom-ladder strip: every step of the ladder on the 0.7 file.
frames = [row(EO1, z, f'step {i + 1} of {len(LADDER)} (1 up to 4, down to 0.25, back to 1)') for i, z in enumerate(LADDER)]
frames[0].save(f'{OUTDIR}/strip.gif', save_all=True, append_images=frames[1:], duration=900, loop=0, optimize=True)
frames[0].save(f'{OUTDIR}/strip.webp', save_all=True, append_images=frames[1:], duration=900, loop=0,
               lossless=True, method=4)
print(sheet.size, frames[0].size)
