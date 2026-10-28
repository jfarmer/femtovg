# blur-ancestor-clip-containment at zoom 0.33, decomposed: full file, no cover rect,
# blur alone, cover alone; femtovg / Chromium DSF1 / Chromium DSF8 box-downsampled (area).
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
D = '/Users/matt/src/femtovg-wt/runs/zoom/triage/blur/cc/'
font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 13)
def L(p): return np.asarray(Image.open(p).convert('RGB')).astype(float)
def diff(a, b):
    d = np.abs(a-b).max(axis=2); img = np.stack([np.clip(d*4, 0, 255)]*3, -1); img[d > 8] = [230, 30, 30]
    return img, int((d > 8).sum()), int(round(d.max()))
rows = [('A  the file: blurred red under a rect clip, green cover on top', 'A'),
        ('B  no cover: femtovg = area; Chromium clips aliased (0.1-covered column empty, 0.9-covered full)', 'B'),
        ('C  blur alone, no clip: both round the filter region out to whole pixels', 'C'),
        ('D  cover alone: femtovg fringe corners (0.1x0.1 -> 0.1, 0.9x0.9 -> 0.9)', 'D')]
cx, cy, cw, ch, S = 202, 102, 42, 42, 6
tw = cw*S; pad = 8; rowh = tw + 44
sheet = Image.new('RGB', (6*(tw+pad)+pad, len(rows)*rowh + 28), (40, 40, 40))
d = ImageDraw.Draw(sheet)
d.text((pad, 6), 'blur-ancestor-clip-containment, zoom 0.33: rect edges at x 206.9 / 239.9, y 106.9 / 139.9', fill=(255,255,255), font=font)
for ri, (title, n) in enumerate(rows):
    oy = 28 + ri*rowh
    d.text((pad, oy), title, fill=(255, 220, 120), font=font)
    f, c, a = L(D+f'{n}.0.33.fvg.png'), L(D+f'{n}.0.33.chr.png'), L(D+f'{n}.0.33.area.png')
    ts = [('femtovg master', f), ('Chromium 131', c), ('Chromium 8x, box-downsampled', a)]
    for nm, x, y in [('femtovg vs Chromium', f, c), ('femtovg vs area', f, a), ('Chromium vs area', c, a)]:
        img, k, m = diff(x, y); ts.append((f'{nm}: {k} px, max {m}', img))
    for i, (nm, img) in enumerate(ts):
        im = Image.fromarray(np.clip(img[cy:cy+ch, cx:cx+cw], 0, 255).astype(np.uint8)).resize((tw, tw), Image.NEAREST)
        ox = pad + i*(tw+pad)
        d.text((ox, oy+18), nm, fill=(255,255,255), font=font)
        sheet.paste(im, (ox, oy+38))
sheet.save(sys.argv[1]); print(sys.argv[1], sheet.size)
