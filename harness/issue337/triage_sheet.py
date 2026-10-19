#!/usr/bin/env python3
"""triage_sheet.py BUILD FRAMING NAME... : per file, sheets/NAME_FRAMING.png - femtovg | Chromium 131 | Firefox 159 |
WebKit | error map (red: more than 20/255 off all three browsers; orange: off one or two; grey: the frame), cropped to
the box around the red pixels (with a margin), or the whole frame when there are none."""
import os, sys, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
b, fr, names = sys.argv[1], sys.argv[2], sys.argv[3:]
L = lambda p: np.asarray(Image.open(p).convert('RGB'), dtype=np.int16)
font = lambda s: ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', s)
for n in names:
    k = f'corpus__buseybench__{n}'
    ours = L(f'png/{b}_{k}_{fr}.png'); refs = [L(f'refs/{x}_{k}_{fr}.png') for x in ('chr', 'ff', 'wk')]
    h = min([ours.shape[0]] + [r.shape[0] for r in refs]); w = min([ours.shape[1]] + [r.shape[1] for r in refs])
    ours = ours[:h, :w]; refs = [r[:h, :w] for r in refs]
    off = [np.abs(ours - r).max(axis=2) > 20 for r in refs]
    all3 = off[0] & off[1] & off[2]; some = (off[0] | off[1] | off[2]) & ~all3
    g = (ours.mean(axis=2) * 0.35 + 120).clip(0, 255).astype('uint8')
    emap = np.stack([g, g, g], 2); emap[some] = [255, 170, 0]; emap[all3] = [230, 0, 0]
    ys, xs = np.nonzero(all3)
    if len(ys):
        m = 40
        y0, y1 = max(0, ys.min() - m), min(h, ys.max() + m); x0, x1 = max(0, xs.min() - m), min(w, xs.max() + m)
    else:
        y0, y1, x0, x1 = 0, h, 0, w
    panels = [ours.astype('uint8')] + [r.astype('uint8') for r in refs] + [emap]
    panels = [Image.fromarray(p[y0:y1, x0:x1]) for p in panels]
    pw, ph = panels[0].size
    scale = 1 if pw >= 300 else 2
    panels = [p.resize((pw * scale, ph * scale), Image.NEAREST) for p in panels]
    pw, ph = panels[0].size
    gap, cap = 6, 18
    sheet = Image.new('RGB', (5 * pw + 6 * gap, ph + cap + gap), 'white')
    d = ImageDraw.Draw(sheet)
    for i, (p, t) in enumerate(zip(panels, ['femtovg master', 'Chromium 131', 'Firefox 159', 'WebKit', f'{int(all3.sum())} px off all three'])):
        x = gap + i * (pw + gap)
        d.text((x, 2), f'{n} {fr}: {t}' if i == 0 else t, fill='black', font=font(12))
        sheet.paste(p, (x, cap))
    sheet.save(f'sheets/{n}_{fr}.png')
    print(n, fr, 'crop', (x0, y0, x1, y1), 'all3 px', int(all3.sum()))
