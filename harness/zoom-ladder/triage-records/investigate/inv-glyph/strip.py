import numpy as np
from PIL import Image, ImageDraw, ImageFont
L = [1, 1.25, 1.5, 1.75, 2, 3, 4, 3, 2, 1.75, 1.5, 1.25, 1, 0.75, 0.5, 0.33, 0.25, 0.33, 0.5, 0.75, 1]
def rgb(p): return np.asarray(Image.open(p).convert('RGB').crop((0, 0, 460, 260))).astype(int)
def diffpanel(a, b, dilate=True):
    d = np.abs(a - b).max(2)
    # dilate so a one-pixel deviation stays visible when the strip is scaled down
    m20 = d > 20; m8 = (d > 8)
    def dil(m):
        if not dilate:
            return m
        o = m.copy()
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                o |= np.roll(np.roll(m, dy, 0), dx, 1)
        return o
    out = np.full(a.shape, 255, np.uint8)
    out[dil(m8)] = (255, 165, 0)
    out[dil(m20)] = (220, 0, 0)
    # faint frame content for orientation
    g = (a.mean(2) < 200)
    out[g & ~dil(m8)] = (215, 215, 215)
    return out, int((d > 8).sum())
font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 15)
small = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 13)
frames = []
W, H, PAD, CAP = 460, 260, 6, 22
for i, z in enumerate(L):
    bl = rgb(f'strip/before/l.ppm.{i:02d}.ppm'); bf = rgb(f'strip/before/f{z}.ppm')
    al = rgb(f'strip/after/l.ppm.{i:02d}.ppm'); af = rgb(f'strip/after/f{z}.ppm')
    ch = rgb(f'chr/chr_{z}.png')
    no = int((np.abs(rgb(f'strip/outline/f{z}.ppm') - ch).max(2) > 8).sum())
    # crop to the text block (union of ink in the three pictures), magnified by a whole factor
    ink = (bl.min(2) < 245) | (al.min(2) < 245) | (ch.min(2) < 245)
    ys, xs = np.nonzero(ink)
    if len(xs):
        x0, x1, y0, y1 = max(xs.min() - 6, 0), min(xs.max() + 7, 460), max(ys.min() - 6, 0), min(ys.max() + 7, 260)
    else:
        x0, x1, y0, y1 = 0, 460, 0, 260
    f = max(1, min(W // (x1 - x0), H // (y1 - y0)))
    bvc, nb = diffpanel(bl, ch, f == 1); avc, na = diffpanel(al, ch, f == 1)
    bvf, nbf = diffpanel(bl, bf, f == 1); avf, naf = diffpanel(al, af, f == 1)
    def crop(im):
        c = im[y0:y1, x0:x1]
        c = np.repeat(np.repeat(c, f, 0), f, 1)
        out = np.full((H, W, 3), 255, np.uint8); out[:c.shape[0], :c.shape[1]] = c[:H, :W]
        return out
    bvc, bvf, avc = crop(bvc), crop(bvf), crop(avc)
    bl, al, ch = crop(bl.astype(np.uint8)), crop(al.astype(np.uint8)), crop(ch.astype(np.uint8))
    panels = [
        (bl.astype(np.uint8), 'before (master 06243b80), ladder frame'),
        (al.astype(np.uint8), 'after (device-grid + subpixel masks), ladder'),
        (ch.astype(np.uint8), 'Chromium 131'),
        (bvc, f'before vs Chromium: {nb} px > 8/255'),
        (avc, f'after vs Chromium: {na} px > 8/255 (outline text: {no} px)'),
        (bvf, f'before, ladder vs fresh process: {nbf} px'),
    ]
    sheet = Image.new('RGB', (3 * W + 4 * PAD, 2 * (H + CAP) + 3 * PAD + 26), 'white')
    dr = ImageDraw.Draw(sheet)
    prev = f' (after zoom {L[i-1]})' if i else ''
    dr.text((PAD, 4), f'text-subpixel-negative-x-offsets.svg, FEMTOVG_TEXT=glyphs - ladder step {i+1}/21, zoom {z}{prev}; text block x{f}; after, ladder vs fresh: {naf} px', font=font, fill='black')
    for k, (im, cap) in enumerate(panels):
        x = PAD + (k % 3) * (W + PAD); y = 26 + PAD + (k // 3) * (H + CAP + PAD)
        dr.text((x, y), cap, font=small, fill='black')
        sheet.paste(Image.fromarray(im), (x, y + CAP))
        dr.rectangle((x - 1, y + CAP - 1, x + W, y + CAP + H), outline=(160, 160, 160))
    frames.append(sheet)
    print(i, z, 'before n8 vs chr', nb, 'after', na, 'ladder-vs-fresh before', nbf, 'after', naf)
frames[0].save('strip/zoom_ladder_glyph_history.gif', save_all=True, append_images=frames[1:], duration=900, loop=0)
frames[0].save('strip/zoom_ladder_glyph_history.webp', save_all=True, append_images=frames[1:], duration=900, loop=0, lossless=True)
