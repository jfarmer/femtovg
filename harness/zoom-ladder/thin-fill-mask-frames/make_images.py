#!/usr/bin/env python3
"""Images for the thin-fill mask frames issue, from frames already rendered (nothing is rendered here).

  make_images.py OUTDIR

before: femtovg master 06243b80 (_logos_full_zm2): the zoom ladder's frames (CORPUS_RUN_OUT=runs/zoom,
png/zl_zm_svg/<key>/NN.png) and the investigation's still-scene frames (ZOOM_LADDER=z,z,...: NAME.ppm.NN.ppm).
after: the same commit with instrumentation.patch and INV_MASKS_A_FRAME=100000000 (the share of 256 masks a frame
lifted), frame 00 at each zoom; bit-identical to master's settled frame at every zoom where both exist.
References: Chromium 131 (software) and WebKit, runs/zoom/fresh/refs. Frames are 460 x 260, the SVG fitted into a
200 px box at (130, 30), then zoomed about the frame's centre.

Writes sheet.png (house five columns), ladder.gif + ladder.webp (the 21-step zoom ladder, five panels a step) and
tiger9-flicker.gif (a still scene on master, frame to frame)."""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

RUNS = os.path.expanduser('~/src/femtovg-wt/runs/zoom')
KEY = 'corpus__babylon__vertex-pulling-normals-uvs-colors-tangents__1'
LADDER = [1, 1.25, 1.5, 1.75, 2, 3, 4, 3, 2, 1.75, 1.5, 1.25, 1, 0.75, 0.5, 0.33, 0.25, 0.33, 0.5, 0.75, 1]
TAG = {1: '1', 1.25: '125', 1.5: '15', 1.75: '175', 2: '2', 3: '3', 4: '4', 0.75: '075', 0.5: '05', 0.33: '033',
       0.25: '025'}
INV = f'{RUNS}/investigate'
LADDER_DIR = f'{RUNS}/png/zl_zm_svg/{KEY}'
# The share lifted, frame 00 of a fresh process at each zoom (no fill is thin at 3 and 4: master's frame).
AFTER = {'025': 'inv-masks-v2/n_025.ppm', '033': 'inv-masks-v2/n_033.ppm', '05': 'inv-masks-v2/n_05.ppm',
         '075': 'inv-masks-v2/n_075.ppm', '1': 'inv-masks-v2/n_1.ppm', '125': 'inv-masks/var/nocap/z1.25.ppm.00.ppm',
         '15': 'inv-masks-v2/n_15.ppm', '175': 'inv-masks-v2/n_175.ppm', '2': 'inv-masks/var/nocap/z2.ppm.00.ppm',
         '3': 'inv-masks-v2/n_3.ppm', '4': 'inv-masks-v2/n_4.ppm'}


def font(size):
    return ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', size)


def load(path):
    return np.asarray(Image.open(path).convert('RGB'), dtype=np.int16)


def ref(browser, tag):
    return load(f'{RUNS}/fresh/refs/{browser}_{KEY}_z{tag}.png')


def after(tag):
    return load(f'{INV}/{AFTER[tag]}')


def n8(a, b):
    return int((np.abs(a - b).max(axis=2) > 8).sum())


def picture(a, box, zoom=1):
    x, y, w, h = box
    im = Image.fromarray(np.clip(a[y:y + h, x:x + w], 0, 255).astype(np.uint8))
    return im.resize((w * zoom, h * zoom), Image.NEAREST) if zoom > 1 else im


def heat(a, b, box, zoom=1):
    """sheet.py's difference panel: white within 8/255, orange 9-20, red beyond."""
    x, y, w, h = box
    d = np.abs(a - b).max(axis=2)[y:y + h, x:x + w]
    out = np.full(d.shape + (3,), 255, np.uint8)
    out[d > 8] = [255, 160, 0]
    out[d > 20] = [255, 0, 0]
    im = Image.fromarray(out)
    return im.resize((w * zoom, h * zoom), Image.NEAREST) if zoom > 1 else im


def wrap(text, width, f):
    words, lines, line = text.split(' '), [], ''
    for word in words:
        trial = f'{line} {word}'.strip()
        if f.getlength(trial) > width and line:
            lines.append(line)
            line = word
        else:
            line = trial
    return lines + [line]


def sheet(out):
    orange = ('Orange left on the after panel: where Chromium is itself 6-17/255 off WebKit; the after frame is '
              'within 5/255 of WebKit.')
    rows = [
        (load(f'{INV}/inv-masks/conv/z1.25.ppm.00.ppm'), '125', (130, 30, 200, 200), 1,
         'zoom 1.25, frame 00: 256 masks made and 128 found; 65,152 of the 65,536 thin fills left to their fringe. '
         '16,384 distinct outlines: master settles at frame 64', orange),
        (load(f'{INV}/inv-masks/conv/z1.25.ppm.32.ppm'), '125', (130, 30, 200, 200), 1,
         'zoom 1.25, frame 32 of the same still scene: the masked band has come a quarter of the way down; '
         'frame 64 flips the rest at once', orange),
        (load(f'{INV}/inv-masks/conv/z2.ppm.00.ppm'), '2', (130, 0, 200, 200), 1,
         'zoom 2, frame 00: the band at the top is the 3,856 fills masked (256 made, 3,600 found); 39,152 left to '
         'their fringe. 320 distinct outlines: frame 01 is final', orange),
        (load(f'{INV}/inv-masks/conv/fresh0.5.ppm'), '05', (180, 80, 100, 100), 2,
         'zoom 0.5, frame 00, the whole image at 2x: 4,096 distinct outlines, master settles at frame 16', ''),
    ]
    head = ('before: femtovg master 06243b80 on WGPU, the frame of a still scene each row names. after: the same commit '
            'with the share of 256 masks a frame lifted (a measurement switch), its frame 00, bit-identical to '
            'master\'s settled frame. Babylon vertex-pulling-normals-uvs-colors-tangents (460x260 frame, 200 px box at '
            'zoom 1). Difference maps against Chromium 131: red beyond 20/255, orange 9-20/255.')
    gap = 8
    built = []
    for before, tag, box, zoom, text, note in rows:
        a, c = after(tag), ref('chr', tag)
        panels = [('before: master', picture(before, box, zoom)), ('after: share lifted', picture(a, box, zoom)),
                  ('Chromium 131', picture(c, box, zoom)), ('before vs Chromium', heat(before, c, box, zoom)),
                  ('after vs Chromium', heat(a, c, box, zoom))]
        caption = f'{text}. Beyond 8/255 of Chromium, whole frame: {n8(before, c):,} -> {n8(a, c):,} px'
        built.append((caption, note, panels))
        print(caption)
    column = max(p.width for _, _, ps in built for _, p in ps) + gap
    width = 5 * column + gap
    lines = lambda text: wrap(text, width - 2 * gap, font(12)) if text else []
    head_lines = lines(head)
    top = gap + 16 * len(head_lines) + 6
    blocks = [(lines(c), lines(n), ps) for c, n, ps in built]
    height = top + sum(16 * (len(c) + len(n)) + 18 + max(p.height for _, p in ps) + gap for c, n, ps in blocks) + gap
    im = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(im)
    for k, line in enumerate(head_lines):
        draw.text((gap, gap + 16 * k), line, fill=(0, 0, 0), font=font(12))
    y = top
    for caption, note, panels in blocks:
        for line in caption:
            draw.text((gap, y), line, fill=(0, 0, 0), font=font(12))
            y += 16
        for line in note:
            draw.text((gap, y), line, fill=(160, 0, 0), font=font(12))
            y += 16
        for i, (label, p) in enumerate(panels):
            x = gap + i * column
            draw.text((x, y + 2), label, fill=(90, 90, 90), font=font(11))
            im.paste(p, (x, y + 18))
            draw.rectangle([x - 1, y + 17, x + p.width, y + 18 + p.height], outline=(200, 200, 200))
        y += 18 + max(p.height for _, p in panels) + gap
    im.save(out)
    print(out, im.size)


def ladder(out):
    box = (130, 0, 200, 260)
    frames = []
    for step, zoom in enumerate(LADDER):
        tag = TAG[zoom]
        b, a, c = load(f'{LADDER_DIR}/{step:02}.png'), after(tag), ref('chr', tag)
        tiles = [('before: master, this step', picture(b, box)), ('after: share lifted, frame 00', picture(a, box)),
                 ('Chromium 131', picture(c, box)), (f'before vs Chromium: {n8(b, c):,} px', heat(b, c, box)),
                 (f'after vs Chromium: {n8(a, c):,} px', heat(a, c, box))]
        w, h = box[2], box[3]
        pad, top = 8, 44
        canvas = Image.new('RGB', (5 * (w + pad) + pad, h + top + pad + 18), (40, 40, 40))
        draw = ImageDraw.Draw(canvas)
        path = ' > '.join(f'{z:g}' for z in LADDER)
        draw.text((pad, 4), f'zoom {zoom:g}   step {step + 1} of {len(LADDER)}: {path}', fill=(255, 255, 255),
                  font=font(13))
        for i, (t, im) in enumerate(tiles):
            x = pad + i * (w + pad)
            draw.text((x, 24), t, fill=(220, 220, 220), font=font(12))
            canvas.paste(im, (x, top))
        draw.text((pad, top + h + 4), 'Babylon vertex-pulling-normals-uvs-colors-tangents, 460x260 frame (x 130-330 '
                  'shown); px beyond 8/255 over the whole frame; orange 9-20/255, red beyond 20/255',
                  fill=(200, 200, 200), font=font(11))
        frames.append(canvas)
        print(step, zoom, tiles[3][0], '|', tiles[4][0])
    frames[0].save(out + '.gif', save_all=True, append_images=frames[1:], duration=900, loop=0, optimize=True)
    frames[0].save(out + '.webp', save_all=True, append_images=frames[1:], duration=900, loop=0, lossless=True,
                   method=4)
    print(out, len(frames), frames[0].size)


def flicker(out):
    """tiger9.svg (3 x 3 Ghostscript tigers, 1,656 thin fills) drawn still at zoom 1 on master: frames 01-04."""
    box, zoom = (130, 30, 200, 200), 2
    fr = [load(f'{INV}/inv-masks/tiger/t1.ppm.{i:02d}.ppm') for i in range(6)]
    frames = []
    for i in range(1, 5):
        d = np.abs(fr[i] - fr[i - 1]).max(axis=2)
        x, y, w, h = box
        diff = np.full((h, w, 3), 255, np.uint8)
        diff[d[y:y + h, x:x + w] > 8] = [255, 160, 0]
        diff[d[y:y + h, x:x + w] > 20] = [255, 0, 0]
        dim = Image.fromarray(diff).resize((w * zoom, h * zoom), Image.NEAREST)
        tiles = [(f'master, frame {i:02d} of a still scene', picture(fr[i], box, zoom)),
                 (f'vs frame {i - 1:02d}: {int((d > 8).sum()):,} px beyond 8/255, max {int(d.max())}/255',
                  dim)]
        pad, top = 8, 26
        canvas = Image.new('RGB', (2 * (w * zoom + pad) + pad, h * zoom + top + pad), 'white')
        draw = ImageDraw.Draw(canvas)
        for k, (t, im) in enumerate(tiles):
            cx = pad + k * (w * zoom + pad)
            draw.text((cx, 6), t, fill=(0, 0, 0), font=font(12))
            canvas.paste(im, (cx, top))
            draw.rectangle([cx - 1, top - 1, cx + im.width, top + im.height], outline=(200, 200, 200))
        frames.append(canvas)
    frames[0].save(out, save_all=True, append_images=frames[1:], duration=600, loop=0, optimize=True)
    print(out, len(frames), frames[0].size)


if __name__ == '__main__':
    o = sys.argv[1]
    os.makedirs(o, exist_ok=True)
    sheet(f'{o}/sheet.png')
    ladder(f'{o}/ladder')
    flicker(f'{o}/tiger9-flicker.gif')
