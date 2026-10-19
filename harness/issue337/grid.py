#!/usr/bin/env python3
"""grid.py BUILD ROWS.json OUT.png [AFTER] : the issue #337 grid. Each row is a BuseyBench portrait at 1080p (hd), cropped to
the region where femtovg master is furthest from the browsers: femtovg | Chromium 131 | Firefox 159 | WebKit (macOS
27.2) | femtovg against all three (red: more than 20/255 off all three; orange: off one or two; grey: the frame).
ROWS.json: [{"name": ..., "crop": [x0, y0, x1, y1], "label": ...}, ...] (crop in the 1920x1080 frame). With AFTER, a
sixth column: the same error map for build AFTER (e.g. master with a harness mapping switched on)."""
import json, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

b, rows_path, out = sys.argv[1:4]
after = sys.argv[4] if len(sys.argv) > 4 else None
after_head = sys.argv[5] if len(sys.argv) > 5 else f'{after} vs all three'
rows = json.load(open(rows_path))
font = lambda s: ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', s)
L = lambda p: np.asarray(Image.open(p).convert('RGB'), dtype=np.int16)
PW = 340  # panel width
heads = ['femtovg (master)', 'Chromium 131', 'Firefox 159', 'WebKit (macOS 27.2)', 'femtovg vs all three']
built = []
for r in rows:
    k = f"corpus__buseybench__{r['name']}"
    ours = L(f'png/{b}_{k}_hd.png')
    refs = [L(f'refs/{x}_{k}_hd.png') for x in ('chr', 'ff', 'wk')]
    def error_map(img):
        off = [np.abs(img - ref).max(axis=2) > 20 for ref in refs]
        all3 = off[0] & off[1] & off[2]
        some = (off[0] | off[1] | off[2]) & ~all3
        g = (img.mean(axis=2) * 0.35 + 120).clip(0, 255).astype('uint8')
        emap = np.stack([g, g, g], 2)
        emap[some] = [255, 170, 0]
        emap[all3] = [230, 0, 0]
        return emap, all3
    emap, all3 = error_map(ours)
    x0, y0, x1, y1 = r['crop']
    panels = [ours.astype('uint8')] + [ref.astype('uint8') for ref in refs] + [emap]
    if after:
        emap_after, all3_after = error_map(L(f'png/{after}_{k}_hd.png'))
        panels.append(emap_after)
        r = {**r, 'after_frame': int(all3_after.sum())}
    panels = [Image.fromarray(p[y0:y1, x0:x1]) for p in panels]
    scale = PW / (x1 - x0)
    ph = round((y1 - y0) * scale)
    panels = [p.resize((PW, ph), Image.LANCZOS if scale < 1 else Image.NEAREST) for p in panels]
    n_all3 = int(all3[y0:y1, x0:x1].sum())
    built.append((r, panels, ph, n_all3, int(all3.sum())))
    print(r['name'], 'crop', r['crop'], 'off all three in crop', n_all3, 'in frame', int(all3.sum()))
gap, cap, head = 8, 34, 22
ncol = 6 if after else 5
W = ncol * PW + (ncol + 1) * gap
H = head + sum(ph + cap + gap for _, _, ph, _, _ in built) + gap
sheet = Image.new('RGB', (W, H), 'white')
d = ImageDraw.Draw(sheet)
for i, t in enumerate(heads + ([after_head] if after else [])):
    d.text((gap + i * (PW + gap), 4), t, fill='black', font=font(14))
y = head
for r, panels, ph, n_crop, n_frame in built:
    d.text((gap, y + 2), f"{r['name']}: {r['label']}", fill='black', font=font(13))
    extra = f"; {r['after_frame']:,} with the linear merge" if 'after_frame' in r else ''
    d.text((gap, y + 18), f"{n_frame:,} pixels of the 1080p frame more than 20/255 off all three browsers{extra}", fill=(90, 90, 90), font=font(11))
    y += cap
    for i, p in enumerate(panels):
        x = gap + i * (PW + gap)
        sheet.paste(p, (x, y))
        d.rectangle([x - 1, y - 1, x + PW, y + ph], outline=(200, 200, 200))
    y += ph + gap
sheet.save(out)
print('wrote', out, sheet.size)
