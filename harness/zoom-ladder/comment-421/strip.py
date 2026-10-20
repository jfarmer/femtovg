#!/usr/bin/env python3
"""strip.py OUT.gif [steps=13,0,1,2,3,4,5] [crop=68x128] [follow=173.0,110.3] [scale=3] [ms=1100]

The #421 comment's zoom-ladder strip for corpus/firefox lists-empty-state-light, five panels per ladder step:
master 06243b80 (the ladder's own frame) | #421 prototype | WebKit | master vs WebKit | prototype vs WebKit.
A difference panel is white within 8/255 of WebKit, grey below that (x6), blue where the frame is lighter than WebKit
by more than 8/255 (less ink: the round joins) and red where it is darker (more ink). The header's counts are the
whole frame. The crop follows a frame point given at zoom 1 (the ladder zooms about the frame centre, 230,130).
Writes OUT.gif, OUT.webp (lossless) and OUT_<step>.png per step.

Inputs:
  master     ~/src/femtovg-wt/runs/zoom/png/zl_zm_svg/<key>/<step>.png
  prototype  ~/src/femtovg-wt/runs/zoom/triage/firefox-artwork/var/le_p421_<framing>.ppm
             (femtovg 06243b80 + harness/round-cap-tessellation/prototype.patch, rendered by the firefox-artwork
             triage from its experiment_with_421_prototype.patch, the same prototype plus switches left off)
  WebKit     ~/src/femtovg-wt/runs/zoom/fresh/refs/wk_<key>_<framing>.png"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.expanduser('~/src/femtovg-wt/da/harness/corpus_run'))
from zoom_ladder import LADDER, FRAMING_OF

KEY = 'corpus__firefox__lists-empty-state-light'
Z = os.path.expanduser('~/src/femtovg-wt/runs/zoom')
out = sys.argv[1]
opts = dict(a.split('=', 1) for a in sys.argv[2:])
steps = [int(s) for s in opts.get('steps', '13,0,1,2,3,4,5').split(',')]
cw, ch = (int(v) for v in opts.get('crop', '68x128').split('x'))
fx, fy = (float(v) for v in opts.get('follow', '173.0,110.3').split(','))
s = int(opts.get('scale', 3))
font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 14)
small = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 13)


def load(p):
    return np.asarray(Image.open(p).convert('RGB'), dtype=np.int32)


def diff(a, ref):
    m = np.abs(a - ref).max(axis=2)
    sd = (a - ref).mean(axis=2)  # > 0: lighter than the reference, less ink
    img = np.repeat(np.clip(255 - m * 6, 200, 255)[..., None], 3, axis=2)
    img[(m > 8) & (sd > 0)] = [40, 110, 255]
    img[(m > 8) & (sd <= 0)] = [235, 30, 30]
    return img, int(((m > 8) & (sd > 0)).sum()), int(((m > 8) & (sd <= 0)).sum())


frames = []
for st in steps:
    z = LADDER[st]
    fr = FRAMING_OF[z]
    before = load(f'{Z}/png/zl_zm_svg/{KEY}/{st:02}.png')
    after = load(f'{Z}/triage/firefox-artwork/var/le_p421_{fr}.ppm')
    wk = load(f'{Z}/fresh/refs/wk_{KEY}_{fr}.png')
    db, bl, bd = diff(before, wk)
    da, al, ad = diff(after, wk)
    H, W = before.shape[:2]
    x = max(0, min(W - cw, int(round(230 + (fx - 230) * z - cw / 2))))
    y = max(0, min(H - ch, int(round(130 + (fy - 130) * z - ch / 2))))
    tiles = [('master 06243b80', before), ('#421 prototype', after), ('WebKit (macOS 27.2)', wk),
             ('master vs WebKit', db), ('prototype vs WebKit', da)]
    pw, ph = cw * s, ch * s
    pad, top = 8, 66
    canvas = Image.new('RGB', (len(tiles) * (pw + pad) + pad, ph + top + pad), (255, 255, 255))
    d = ImageDraw.Draw(canvas)
    d.text((pad, 6), f'lists-empty-state-light, checkbox corners (round joins, width 2)   zoom {z:g}, ladder step {st + 1} of {len(LADDER)}',
           fill=(0, 0, 0), font=font)
    d.text((pad, 25), f'px > 8/255 off WebKit, whole frame, lighter (blue) + darker (red): master {bl} + {bd}, prototype {al} + {ad}',
           fill=(0, 0, 0), font=small)
    for i, (label, a) in enumerate(tiles):
        X = pad + i * (pw + pad)
        d.text((X, 46), label, fill=(70, 70, 70), font=small)
        im = Image.fromarray(np.clip(a[y:y + ch, x:x + cw], 0, 255).astype(np.uint8)).resize((pw, ph), Image.NEAREST)
        canvas.paste(im, (X, top))
        d.rectangle([X - 1, top - 1, X + pw, top + ph], outline=(190, 190, 190))
    frames.append(canvas)
    print(f'zoom {z:g} step {st}: crop {x},{y}  master {bl}+{bd}  prototype {al}+{ad}')
ms = int(opts.get('ms', 1100))
# One palette for every GIF frame, holding the difference colours exactly (a per-frame palette greyed the blue).
tall = Image.new('RGB', (frames[0].width, frames[0].height * len(frames)))
for i, f in enumerate(frames):
    tall.paste(f, (0, i * f.height))
pal = tall.quantize(colors=252, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
entries = pal.getpalette()[:252 * 3] + [40, 110, 255, 235, 30, 30, 0, 0, 0, 255, 255, 255]
pal.putpalette(entries)
gif = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
gif[0].save(out, save_all=True, append_images=gif[1:], duration=ms, loop=0)
frames[0].save(os.path.splitext(out)[0] + '.webp', save_all=True, append_images=frames[1:], duration=ms, loop=0,
               lossless=True, method=4)
for st, f in zip(steps, frames):
    f.save(os.path.splitext(out)[0] + f'_{st:02}.png')
print(out, len(frames), frames[0].size)
