#!/usr/bin/env python3
"""The issue's sheet, in corpus_run/sheet.py's layout: master 06243b80 | gate fix (prototype) | WebKit |
master vs WebKit | gate fix vs WebKit | Chromium vs WebKit. A difference panel is white within 8/255, orange from 9 to
20 and red beyond. Counts are pixels beyond 8/255 in the region the caption names.

  sheet5.py OUT.png ZM_LADDER_DIR GATE_LADDER_DIR REFS_DIR REPRO_DIR TRIAGE_DIR

REPRO_DIR holds repro_master.png and repro_gate.png (repro.svg by the proof build, without and with FV_GATE_FIX=1);
TRIAGE_DIR the WebKit and Chromium frames of a longer probe whose rows A-C are repro.svg (its other rows are
fills of separate cause)."""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

out, zm, gate, refs, repro, triage = sys.argv[1:7]
KEY = 'svgenius__page_275_化妆品装饰_25821_icon_24'


def font(size):
    return ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', size)


def load(path):
    a = np.asarray(Image.open(path).convert('RGBA')).astype(float)
    return a[..., :3] * a[..., 3:4] / 255 + 255 * (1 - a[..., 3:4] / 255)


def count(a, b, band):
    y0, y1 = band
    return int((np.abs(a[y0:y1] - b[y0:y1]).max(axis=2) > 8).sum())


def picture(a, box, zoom):
    x, y, w, h = box
    im = Image.fromarray(np.clip(a[y:y + h, x:x + w], 0, 255).round().astype(np.uint8))
    return im.resize((w * zoom, h * zoom), Image.NEAREST)


def difference(a, b, box, zoom):
    x, y, w, h = box
    d = np.abs(a - b).max(axis=2)[y:y + h, x:x + w]
    heat = np.full(d.shape + (3,), 255, np.uint8)
    heat[d > 8] = [255, 160, 0]
    heat[d > 20] = [255, 0, 0]
    return Image.fromarray(heat).resize((w * zoom, h * zoom), Image.NEAREST)


rows = []
for title, m, g, wk, chr_, box, zoom, band, region in [
    ('svgenius makeup icon at 0.33 (ladder step 16): five rings of two convex contours, walls 1.09-1.16 px',
     f'{zm}/15.png', f'{gate}/15.png', f'{refs}/wk_{KEY}_z033.png', f'{refs}/chr_{KEY}_z033.png',
     (194, 94, 72, 72), 4, (0, 260), 'frame'),
    ('repro.svg at 1x, left ends: A, one 1.2 px bar (one contour); B, two of them in one path; C, a ring with 1.2 px walls',
     f'{repro}/repro_master.png', f'{repro}/repro_gate.png', f'{triage}/repro_wk.png', f'{triage}/repro_chr.png',
     (144, 46, 90, 78), 3, (40, 130), 'rows A-C'),
]:
    M, G, W, C = (load(p) for p in (m, g, wk, chr_))
    nm, ng, nc = count(M, W, band), count(G, W, band), count(C, W, band)
    caption = (f'{title}. Beyond 8/255 against WebKit ({region}): master {nm:,} px, gate fix {ng:,} px; '
               f'Chromium itself {nc:,} px')
    panels = [('femtovg master 06243b80', picture(M, box, zoom)), ('gate fix (prototype)', picture(G, box, zoom)),
              ('WebKit (macOS 27.2)', picture(W, box, zoom)), ('master vs WebKit', difference(M, W, box, zoom)),
              ('gate fix vs WebKit', difference(G, W, box, zoom)), ('Chromium 131 vs WebKit', difference(C, W, box, zoom))]
    rows.append((caption, panels))
    print(caption)

gap, cap = 8, 36
column = max(p.width for _, panels in rows for _, p in panels) + gap
width = max(len(rows[0][1]) * column + gap, max(int(font(13).getlength(c)) + 2 * gap for c, _ in rows))
sheet = Image.new('RGB', (width, sum(max(p.height for _, p in panels) + cap + gap for _, panels in rows) + gap), 'white')
draw = ImageDraw.Draw(sheet)
y = gap
for caption, panels in rows:
    draw.text((gap, y), caption, fill=(0, 0, 0), font=font(13))
    for i, (label, p) in enumerate(panels):
        x = gap + i * column
        draw.text((x, y + 19), label, fill=(90, 90, 90), font=font(11))
        sheet.paste(p, (x, y + cap))
        draw.rectangle([x - 1, y + cap - 1, x + p.width, y + cap + p.height], outline=(200, 200, 200))
    y += max(p.height for _, p in panels) + cap + gap
sheet.save(out)
print(out, sheet.size)
