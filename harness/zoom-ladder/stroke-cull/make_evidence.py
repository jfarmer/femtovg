#!/usr/bin/env python3
"""The issue's five-column sheet and its zoom-ladder strip: before (master 06243b80) | after (prototype) | Chromium 131 |
before vs Chromium | after vs Chromium (red: more than 8/255 off; grey: the difference amplified 4x). Whole 460 x 260
frames shown at 0.4x (area-averaged) so the images read at an issue's width; the counts are taken at full size.

  make_evidence.py OUTDIR
Frames: frames/<master|prototype>/<name>/NN.png from render_ladder.py; browser frames from runs/zoom/fresh/refs."""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
CORPUS_RUN = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'corpus_run')  # harness/corpus_run on demo-assets
sys.path.insert(0, CORPUS_RUN if os.path.isdir(CORPUS_RUN) else os.path.expanduser('~/src/femtovg-wt/da/harness/corpus_run'))
from zoom_ladder import LADDER, FRAMING_OF

HERE = os.path.dirname(os.path.abspath(__file__))
FRAMES = os.environ.get('FRAMES', f'{HERE}/frames')
REFS = os.path.expanduser('~/src/femtovg-wt/runs/zoom/fresh/refs')
FILES = {'miter-acute': ('wpt22__21-degenerate-paths-dashes-and-joins__wpt-2d-line-miter-acute', 'wpt-2d-line-miter-acute.svg'),
         'mask-thin': ('corpus__wpt__tests__mask-on-thin-stroked-path-userspaceonuse', 'mask-on-thin-stroked-path-userspaceonuse.svg')}
font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 13)
W, H = 184, 104  # 460 x 260 at 0.4x
PAD = 8
WIDTH = 5 * (W + PAD) + PAD
WHITE, GREY, YELLOW, BG = (255, 255, 255), (200, 200, 200), (255, 210, 60), (40, 40, 40)
COLUMNS = ('before: master 06243b80', 'after: prototype', 'Chromium 131', 'before vs Chromium', 'after vs Chromium')
CAPTION = ("before: femtovg master 06243b80 on WGPU. after: prototype.patch, the cull widened to the stroke's outer antialiased edge.",
           'Difference maps against Chromium 131: red beyond 8/255, grey the difference x4. Whole 460 x 260 frames at 0.4x.')
out = sys.argv[1]
os.makedirs(out, exist_ok=True)


def load(p):
    return np.asarray(Image.open(p).convert('RGB'), dtype=np.int16)


def diff(a, b):
    d = np.abs(a - b).max(axis=2)
    img = np.stack([np.clip(d * 4, 0, 255)] * 3, -1)
    img[d > 8] = [230, 30, 30]
    return img, int((d > 8).sum())


def small(a):
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).resize((W, H), Image.BOX)


def frame(name, step, ladder_line=False):
    """One row: a title line (file, zoom, counts, which browsers match Chromium), the column labels, the five panels."""
    key, svg = FILES[name]
    z = LADDER[step]
    before = load(f'{FRAMES}/master/{name}/{step:02}.png')
    after = load(f'{FRAMES}/prototype/{name}/{step:02}.png')
    chrome = load(f'{REFS}/chr_{key}_{FRAMING_OF[z]}.png')
    db, nb = diff(before, chrome)
    da, na = diff(after, chrome)
    same, missing = [], []
    for b, label in (('ff', 'Firefox 159'), ('wk', 'WebKit')):
        p = f'{REFS}/{b}_{key}_{FRAMING_OF[z]}.png'
        if not os.path.exists(p):
            missing.append(label)
        elif not np.abs(load(p) - chrome).any():
            same.append(label)
    note = ''
    if same:
        note = f'; {" and ".join(same)} identical to it'
    if missing:
        note += f' (no {" or ".join(missing)} frame at this zoom)'
    title = f'{svg} at zoom {z:g}: {nb:,} -> {na:,} px more than 8/255 off Chromium 131{note}'
    top = 4
    rows = 2 if ladder_line else 1
    label_y = top + 18 * rows + 2
    panel_y = label_y + 18
    im = Image.new('RGB', (WIDTH, panel_y + H + PAD), BG)
    draw = ImageDraw.Draw(im)
    draw.text((PAD, top), title, fill=WHITE, font=font)
    if ladder_line:
        # The ladder, the current step in yellow.
        x = PAD
        lead = f'step {step + 1} of {len(LADDER)}:  '
        draw.text((x, top + 18), lead, fill=GREY, font=font)
        x += draw.textlength(lead, font=font)
        for i, zz in enumerate(LADDER):
            for t, colour in ((f'{zz:g}', YELLOW if i == step else GREY), (' > ' if i + 1 < len(LADDER) else '', GREY)):
                draw.text((x, top + 18), t, fill=colour, font=font)
                x += draw.textlength(t, font=font)
    for i, (label, a) in enumerate(zip(COLUMNS, (before, after, chrome, db, da))):
        x = PAD + i * (W + PAD)
        draw.text((x, label_y), label, fill=GREY, font=font)
        im.paste(small(a), (x, panel_y))
    return im


def caption():
    im = Image.new('RGB', (WIDTH, 4 + 18 * len(CAPTION) + 4), BG)
    draw = ImageDraw.Draw(im)
    for i, line in enumerate(CAPTION):
        draw.text((PAD, 4 + 18 * i), line, fill=WHITE, font=font)
    return im


def stack(parts):
    im = Image.new('RGB', (WIDTH, sum(p.height for p in parts)), BG)
    y = 0
    for p in parts:
        im.paste(p, (0, y))
        y += p.height
    return im


cap = caption()
# The strip: every step of the ladder on the miter file.
frames = [stack([cap, frame('miter-acute', s, ladder_line=True)]) for s in range(len(LADDER))]
frames[0].save(f'{out}/strip.gif', save_all=True, append_images=frames[1:], duration=700, loop=0, optimize=True)
frames[0].save(f'{out}/strip.webp', save_all=True, append_images=frames[1:], duration=700, loop=0, lossless=True, method=4)
# The sheet: the last zoom that passes and two that fail on the miter file, and the mask file at 3.
sheet = stack([cap] + [frame(n, s) for n, s in [('miter-acute', 1), ('miter-acute', 2), ('miter-acute', 6), ('mask-thin', 5)]])
sheet.save(f'{out}/sheet.png', optimize=True)
print(out, len(frames), 'strip frames', frames[0].size, 'sheet', sheet.size)
