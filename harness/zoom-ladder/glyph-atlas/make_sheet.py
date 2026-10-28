#!/usr/bin/env python3
"""Evidence sheet and zoom-ladder strip for the glyph-atlas history issue.

Frames: the zoom-ladder harness (harness/corpus_run/zoom_ladder.py framing: 460x260, the SVG in a 200 px box at
(130, 30), zoomed about (230, 130)) with FEMTOVG_TEXT=glyphs, master 06243b80 (before) and the prototype (after:
GLYPH_DEVICE_GRID=1 GLYPH_SUBPIXEL_MASK=1 on prototype.patch). l.ppm.NN.ppm = ladder step NN on one canvas,
fN.ppm = a fresh process at zoom N, outline/fN.ppm = the same text as outlines (no FEMTOVG_TEXT), chr_N.png =
Chromium 131. Difference panels: white within 8/255, orange 9-20/255, red beyond; light grey = ink, for orientation.

  make_sheet.py FRAMES_DIR CHR_DIR OUT_DIR
"""
import sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FR, CHR, OUT = sys.argv[1:4]
L = [1, 1.25, 1.5, 1.75, 2, 3, 4, 3, 2, 1.75, 1.5, 1.25, 1, 0.75, 0.5, 0.33, 0.25, 0.33, 0.5, 0.75, 1]
FILE = 'text-subpixel-negative-x-offsets.svg'


def rgb(p):
    return np.asarray(Image.open(p).convert('RGB')).astype(int)[:260, :460]


def frames(i):
    z = L[i]
    return dict(bl=rgb(f'{FR}/before/l.ppm.{i:02d}.ppm'), bf=rgb(f'{FR}/before/f{z}.ppm'),
                al=rgb(f'{FR}/after/l.ppm.{i:02d}.ppm'), af=rgb(f'{FR}/after/f{z}.ppm'),
                ch=rgb(f'{CHR}/chr_{z}.png'), ol=rgb(f'{FR}/outline/f{z}.ppm'))


def count(a, b):
    return int((np.abs(a - b).max(2) > 8).sum())


def diffpanel(a, b, ink, dilate):
    d = np.abs(a - b).max(2)
    m8, m20 = d > 8, d > 20
    if dilate:  # a one-pixel deviation stays visible when an unmagnified frame is scaled down
        def dil(m):
            o = m.copy()
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    o |= np.roll(np.roll(m, dy, 0), dx, 1)
            return o
        m8, m20 = dil(m8), dil(m20)
    out = np.full(a.shape, 255, np.uint8)
    out[ink & ~m8] = (215, 215, 215)
    out[m8] = (255, 165, 0)
    out[m20] = (220, 0, 0)
    return out


def font(n):
    return ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', n)


def panels(i, box=None, mag=None, W=460, H=260):
    """Six panels for ladder step i, cropped to box (x, y, w, h) and magnified mag times."""
    f = frames(i)
    ink = (f['bl'].min(2) < 245) | (f['ch'].min(2) < 245)
    if box is None:  # the text block of the three pictures, as large as fits W x H
        inkb = ink | (f['al'].min(2) < 245)
        ys, xs = np.nonzero(inkb)
        if len(xs):
            x0, x1, y0, y1 = max(xs.min() - 6, 0), min(xs.max() + 7, 460), max(ys.min() - 6, 0), min(ys.max() + 7, 260)
        else:  # the text is off the frame at this zoom
            x0, x1, y0, y1 = 0, 460, 0, 260
        box = (x0, y0, x1 - x0, y1 - y0)
        mag = max(1, min(W // box[2], H // box[3]))
    x0, y0, w, h = box
    n = dict(bc=count(f['bl'], f['ch']), ac=count(f['al'], f['ch']), oc=count(f['ol'], f['ch']),
             bh=count(f['bl'], f['bf']), ah=count(f['al'], f['af']))
    dil = mag == 1
    ims = [f['bl'], f['al'], f['ch'], diffpanel(f['bl'], f['ch'], ink, dil), diffpanel(f['al'], f['ch'], ink, dil),
           diffpanel(f['bl'], f['bf'], ink, dil)]

    def cut(im):
        c = np.asarray(im, np.uint8)[y0:y0 + h, x0:x0 + w]
        return np.repeat(np.repeat(c, mag, 0), mag, 1)
    return [cut(im) for im in ims], n, mag


def strip():
    W, H, PAD, CAP, TOP = 460, 260, 6, 24, 30
    out = []
    rows = []
    for i, z in enumerate(L):
        ims, n, mag = panels(i)
        rows.append((i, z, n))
        caps = ['before: master 06243b80', 'after: prototype', 'Chromium 131',
                f'before vs Chromium: {n["bc"]:,} px > 8/255',
                f'after vs Chromium: {n["ac"]:,} px (outline text: {n["oc"]:,})',
                f'before vs a fresh canvas at zoom {z:g}: {n["bh"]} px']
        sheet = Image.new('RGB', (3 * W + 4 * PAD, 2 * (H + CAP + PAD) + TOP + PAD), 'white')
        dr = ImageDraw.Draw(sheet)
        prev = f', after zoom {L[i - 1]:g}' if i else ', the first frame'
        off = '  (The text is off the frame at this zoom.)' if not (f_ink := (ims[0].min(2) < 245).any()) else ''
        dr.text((PAD, 6), f'{FILE} through fill_glyph_run, one canvas: step {i + 1} of 21, zoom {z:g}{prev}.  '
                f'Text x{mag}.  After vs a fresh canvas: {n["ah"]} px{off}', font=font(17), fill='black')
        for k, (im, cap) in enumerate(zip(ims, caps)):
            x = PAD + (k % 3) * (W + PAD)
            y = TOP + PAD + (k // 3) * (H + CAP + PAD)
            dr.text((x, y + 3), cap, font=font(16), fill='black')
            tile = np.full((H, W, 3), 255, np.uint8)
            tile[:min(H, im.shape[0]), :min(W, im.shape[1])] = im[:H, :W]
            sheet.paste(Image.fromarray(tile), (x, y + CAP))
            dr.rectangle((x - 1, y + CAP - 1, x + W, y + CAP + H), outline=(160, 160, 160))
        out.append(sheet)
    out[0].save(f'{OUT}/strip.gif', save_all=True, append_images=out[1:], duration=900, loop=0, optimize=True)
    out[0].save(f'{OUT}/strip.webp', save_all=True, append_images=out[1:], duration=900, loop=0, lossless=True,
                method=4)
    return rows


def sheet():
    # Row per ladder step where a frame differs from a fresh canvas; columns as the house sheet, plus the frame
    # against a fresh canvas at that zoom.
    spec = [(1, (154, 17, 52, 70), 4), (16, (212, 104, 22, 19), 10)]
    PAD, CAP, TOP = 8, 44, 34
    rows = []
    for i, box, mag in spec:
        ims, n, _ = panels(i, box, mag)
        rows.append((i, ims, n))
    pw = max(im.shape[1] for _, ims, _ in rows for im in ims)
    hs = [max(im.shape[0] for im in ims) for _, ims, _ in rows]
    Wt = 6 * (pw + PAD) + PAD
    Ht = TOP + sum(h + CAP + PAD for h in hs) + PAD
    S = Image.new('RGB', (Wt, Ht), 'white')
    dr = ImageDraw.Draw(S)
    dr.text((PAD, 8), f'{FILE} through fill_glyph_run; each row is a frame drawn on one canvas after the '
            'previous zoom of the ladder; counts are for the whole 460 x 260 frame.', font=font(17), fill='black')
    y = TOP
    for (i, ims, n), h in zip(rows, hs):
        z, p = L[i], L[i - 1]
        caps = [(f'zoom {z:g} after {p:g}', 'before: master 06243b80'), ('', 'after: prototype'),
                ('', 'Chromium 131'), ('before vs Chromium', f'{n["bc"]:,} px > 8/255'),
                ('after vs Chromium', f'{n["ac"]:,} (outline text {n["oc"]:,})'),
                ('before vs a fresh canvas', f'{n["bh"]} px (after: {n["ah"]})')]
        for k, (im, (c1, c2)) in enumerate(zip(ims, caps)):
            x = PAD + k * (pw + PAD)
            dr.text((x, y + 2), c1, font=font(17), fill='black')
            dr.text((x, y + 22), c2, font=font(17), fill='black')
            tile = np.full((h, pw, 3), 255, np.uint8)
            tile[:im.shape[0], :im.shape[1]] = im
            S.paste(Image.fromarray(tile), (x, y + CAP))
            dr.rectangle((x - 1, y + CAP - 1, x + pw, y + CAP + h), outline=(160, 160, 160))
        y += h + CAP + PAD
    S.save(f'{OUT}/sheet.png', optimize=True)


rows = strip()
sheet()
with open(f'{OUT}/steps.txt', 'w') as fh:
    fh.write(f'{FILE}, FEMTOVG_TEXT=glyphs, zoom ladder on one canvas (wgpu, Apple M4 Max). Pixels more than 8/255 off.\n')
    fh.write('step zoom | before vs fresh canvas | after vs fresh canvas | vs Chromium 131: before, after, outline text\n')
    for i, z, n in rows:
        fh.write(f'{i + 1:2d} {z:<5g} | {n["bh"]:3d} | {n["ah"]} | {n["bc"]:5d} {n["ac"]:5d} {n["oc"]:5d}\n')
print(open(f'{OUT}/steps.txt').read())
