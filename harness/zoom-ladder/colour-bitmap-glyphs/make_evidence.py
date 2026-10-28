#!/usr/bin/env python3
"""Sheet and zoom-ladder strip for the colour bitmap glyph issue, from saved frames (no rendering).

  make_evidence.py sheet OUT.png
  make_evidence.py strip OUT.gif      (writes OUT.gif and OUT.webp)
  make_evidence.py numbers            (every number the issue quotes, to stdout)

Frames: femtovg master 06243b80 and the prototype (prototype.patch, env-switched) on WGPU/Metal through the corpus
harness with FEMTOVG_TEXT=glyphs (fill_glyph_run), kept under INV (default ~/src/femtovg-wt/runs/inv-emoji):
probe/{base,fixqc,chr}/crabS_*.png (one crab at (40, 150), 200x200 at 1:1) and ladder/{base,fin}/<file>/step.ppm.NN.png
(the 21-step zoom ladder on one canvas, 460x260 framing), with Chromium 131 at each zoom in refs/; WebKit re-shot
with make_ref.py's UTF-8 declaration (demo-assets 2c9de6c0) under REFS (default ~/src/femtovg-wt/runs/zoom/fresh/refs).
Difference panels: white within 8/255 of Chromium, orange 9-20/255, red beyond 20/255."""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

INV = os.path.expanduser(os.environ.get('INV', '~/src/femtovg-wt/runs/inv-emoji'))
LADDER = [1, 1.25, 1.5, 1.75, 2, 3, 4, 3, 2, 1.75, 1.5, 1.25, 1, 0.75, 0.5, 0.33, 0.25, 0.33, 0.5, 0.75, 1]
FONT = '/System/Library/Fonts/Helvetica.ttc'
# The prototype's switches for the probe frames (probe/fixqc); the ladder frames (ladder/fin) add
# EMOJI_DIRECT_SCALE=1 EMOJI_LINEAR=1. At 1:1 the crab takes the atlas route, where those two change nothing.
PROTO_ATLAS = ('EMOJI_NOPAD=1 EMOJI_DROP=0.125 EMOJI_ROUNDSIZE=1 EMOJI_FILTER=catmullrom EMOJI_QUARTERX=1 '
               'EMOJI_SNAPBL=1 EMOJI_CEILSTRIKE=1')


def font(size):
    return ImageFont.truetype(FONT, size)


def load(p):
    return np.asarray(Image.open(f'{INV}/{p}').convert('RGB'), dtype=np.int16)


def dmax(a, r):
    return np.abs(a - r).max(axis=2)


def heat(d):
    o = np.full(d.shape + (3,), 255, np.uint8)
    o[d > 8] = (255, 160, 0)
    o[d > 20] = (255, 0, 0)
    return o


def cut(a, box, zoom):
    x, y, w, h = box
    im = Image.fromarray(np.clip(a[y:y + h, x:x + w], 0, 255).astype(np.uint8))
    return im.resize((w * zoom, h * zoom), Image.NEAREST) if zoom > 1 else im


def wrap(draw, text, f, width):
    lines, line = [], ''
    for word in text.split(' '):
        t = (line + ' ' + word).strip()
        if draw.textlength(t, font=f) > width and line:
            lines.append(line)
            line = word
        else:
            line = t
    return lines + [line]


def five(before, after, ref, box, zoom):
    return [cut(before, box, zoom), cut(after, box, zoom), cut(ref, box, zoom),
            cut(heat(dmax(before, ref)), box, zoom), cut(heat(dmax(after, ref)), box, zoom)]


LABELS = ['before: master', 'after: prototype', 'Chromium 131', 'before vs Chromium', 'after vs Chromium']


def sheet(out):
    rows = []
    # 1. The default route: one crab at 50 px. Strike 52 ppem, resampled with Nearest to the padded 54 px cell.
    b, a, r = load('probe/base/crab50_glyphs_z1.png'), load('probe/fixqc/crab50_glyphs_z1.png'), load('probe/chr/crab50_z1.png')
    rows.append((f'crab50.svg at 1x, 3x: one crab at 50 px, pen (40, 150). Master point-samples the 52 ppem strike onto the '
                 f'whole padded cell, 50 px and a padding texel each side: 52 px wide from x 39, its ink 7 px above Chromium\'s at the top and 5 at the bottom. '
                 f'After: 50 px at Chromium\'s place. {int((dmax(b, r) > 20).sum())} -> {int((dmax(a, r) > 20).sum())} px beyond 20/255; '
                 f'the red left (at most {int(dmax(a, r).max())}/255) is the resampling filter: CatmullRom, where CoreGraphics\' '
                 f'high-quality kernel is not known.', five(b, a, r, (37, 99, 58, 58), 3)))
    # 2. Size rounding: 30 px on the 32 ppem strike.
    b, a, r = load('probe/base/crab30_glyphs_z1.png'), load('probe/fixqc/crab30_glyphs_z1.png'), load('probe/chr/crab30_z1.png')
    rows.append((f'crab30.svg at 1x, 5x: at 30 px, ceil() of 30/800 x 800 in f32 gives 31, and the padding stretch makes '
                 f'it 33 px from x 39, its top 5 px high. After: 30 px. {int((dmax(b, r) > 20).sum())} -> '
                 f'{int((dmax(a, r) > 20).sum())} px beyond 20/255.', five(b, a, r, (37, 119, 36, 36), 5)))
    # 3. The direct route under zoom: the flag at zoom 4 (128 px > 92) is baked at 32 px and magnified 4x, NEAREST.
    f, i = 'resvg-compound-emojis-rainbow-flag', 6
    b, a, r = load(f'ladder/base/{f}/step.ppm.{i:02d}.png'), load(f'ladder/fin/{f}/step.ppm.{i:02d}.png'), load(f'refs/chr_{f}_z4.png')
    rows.append((f'resvg-compound-emojis-rainbow-flag.svg, zoom-ladder step 7 (zoom 4), 1x: at 128 px on the device the '
                 f'flag takes the direct route, baked at its 32 px font size and magnified 4x from a NEAREST atlas, in 4 px '
                 f'blocks, its bottom 12 px and its top 19 px above Chromium\'s. After (baked at the device size, sampled linearly): {int((dmax(b, r) > 20).sum())} -> '
                 f'{int((dmax(a, r) > 20).sum())} px beyond 20/255.', five(b, a, r, (174, 60, 128, 110), 1)))
    # 4. The direct route under rotation, zoom 2.
    f, i = 'emoji-under-scale-and-rotate', 4
    b, a, r = load(f'ladder/base/{f}/step.ppm.{i:02d}.png'), load(f'ladder/fin/{f}/step.ppm.{i:02d}.png'), load(f'refs/chr_{f}_z2.png')
    rows.append((f'emoji-under-scale-and-rotate.svg, zoom-ladder step 5 (zoom 2), 1x: rotate(30) sends the emoji to the '
                 f'direct route; master bakes them at their 60 px font size and draws them 1.49x larger (scale(1.3), the '
                 f'frame\'s 200/350, zoom 2), point-sampled. '
                 f'{int((dmax(b, r) > 20).sum())} -> {int((dmax(a, r) > 20).sum())} px beyond 20/255. The red left after runs '
                 f'along the edges and is not attributed; under rotation the browsers differ too (WebKit is 733 px off '
                 f'Chromium here).',
                 five(b, a, r, (117, 26, 164, 136), 1)))
    gap, pad, W = 8, 14, 924
    col = (W - 2 * pad - 4 * gap) // 5
    probe = Image.new('RGB', (10, 10))
    draw = ImageDraw.Draw(probe)
    head = ('femtovg on WGPU (Metal), through the corpus harness with FEMTOVG_TEXT=glyphs (fill_glyph_run; fill_text is '
            'identical), Apple Color Emoji. Difference panels: white within 8/255 of Chromium 131, orange 9-20/255, red '
            'beyond 20/255. At 30 and 50 px Chromium, WebKit and CoreText (CTFontDrawGlyphs) are 0 px apart.')
    hl = wrap(draw, head, font(15), W - 2 * pad)
    blocks = []
    for cap, panels in rows:
        cl = wrap(draw, cap, font(15), W - 2 * pad)
        ph = max(p.height for p in panels)
        blocks.append((cl, panels, ph))
    H = pad + 19 * len(hl) + gap + sum(19 * len(cl) + 22 + ph + 2 * gap + 2 for cl, _, ph in blocks) + pad
    img = Image.new('RGB', (W, H), 'white')
    d = ImageDraw.Draw(img)
    y = pad
    for line in hl:
        d.text((pad, y), line, fill=(60, 60, 60), font=font(15))
        y += 19
    y += gap
    for cl, panels, ph in blocks:
        d.line([(pad, y), (W - pad, y)], fill=(225, 225, 225))
        y += gap
        for line in cl:
            d.text((pad, y), line, fill=(0, 0, 0), font=font(15))
            y += 19
        for k, (lab, p) in enumerate(zip(LABELS, panels)):
            x = pad + k * (col + gap)
            d.text((x, y + 3), lab, fill=(100, 100, 100), font=font(13))
            if p.width > col:
                p = p.crop(((p.width - col) // 2, 0, (p.width - col) // 2 + col, p.height))
            ox = x + (col - p.width) // 2
            img.paste(p, (ox, y + 22))
            d.rectangle([ox - 1, y + 21, ox + p.width, y + 22 + p.height], outline=(200, 200, 200))
        y += 22 + ph + gap + 2
    img = img.crop((0, 0, W, y + pad - gap))
    img.save(out)
    print(out, img.size)


def strip(out):
    f = 'resvg-compound-emojis-rainbow-flag'
    box, zoom = (176, 60, 124, 108), 2
    gap, top, foot = 8, 46, 22
    frames = []
    for i, z in enumerate(LADDER):
        b = load(f'ladder/base/{f}/step.ppm.{i:02d}.png')
        a = load(f'ladder/fin/{f}/step.ppm.{i:02d}.png')
        r = load(f'refs/chr_{f}_z{z:g}.png')
        nb, na = int((dmax(b, r) > 20).sum()), int((dmax(a, r) > 20).sum())
        panels = five(b, a, r, box, zoom)
        labels = ['before: master 06243b80', 'after: prototype', 'Chromium 131', f'before vs Chromium: {nb} px',
                  f'after vs Chromium: {na} px']
        w, h = panels[0].size
        img = Image.new('RGB', (5 * w + 6 * gap, h + top + foot), (40, 40, 40))
        d = ImageDraw.Draw(img)
        route = 'direct route (> 92 px)' if 32 * z > 92 else 'atlas'
        d.text((gap, 5), f'zoom {z:g}   step {i + 1} of 21:  ' + ' > '.join(f'{v:g}' for v in LADDER),
               fill=(255, 255, 255), font=font(14))
        for k, (lab, p) in enumerate(zip(labels, panels)):
            x = gap + k * (w + gap)
            d.text((x, 26), lab, fill=(220, 220, 220), font=font(13))
            img.paste(p, (x, top))
        d.text((gap, top + h + 4), f'resvg-compound-emojis-rainbow-flag.svg, 32 px emoji, {32 * z:g} px on the device: '
               f'{route}. Difference panels: orange 9-20/255, red beyond 20/255 (counted, whole frame).',
               fill=(200, 200, 200), font=font(12))
        frames.append(img)
    frames[0].save(out, save_all=True, append_images=frames[1:], duration=900, loop=0, optimize=True)
    frames[0].save(os.path.splitext(out)[0] + '.webp', save_all=True, append_images=frames[1:], duration=900, loop=0,
                   lossless=True, method=4)
    print(out, frames[0].size)


def numbers(_=None):
    count = lambda a, r, t=20: int((dmax(a, r) > t).sum())
    sizes = [16, 20, 24, 30, 36, 40, 48, 50, 60, 64, 72, 80, 90]
    variants = [('base', 'master 06243b80'), ('nopad', 'padding kept'), ('drop', '1/8 em drop'),
                ('nopad_drop', 'padding kept + drop'), ('ndr_nearest', '+ rounded size, Nearest'),
                ('ndr_cr', '+ CatmullRom'), ('ndr_l3', '+ Lanczos3 instead'), ('fixqc', 'prototype (atlas changes)'),
                ('ndrs_cr', '+ CatmullRom + EMOJI_CTSMALL'), ('swash', 'swash route (swash feature)'),
                ('ct', 'CoreText CTFontDrawGlyphs'), ('wk', 'WebKit')]
    print('1. One crab (Apple Color Emoji) at (40, 150), 200x200 at 1:1, fill_glyph_run. Pixels beyond 20/255 off '
          'Chromium 131; ink box width and top edge against Chromium\'s (24/255 ink threshold).')
    print('Switches of prototype.patch per row (master: none): padding kept EMOJI_NOPAD=1; drop EMOJI_DROP=0.125; '
          'padding kept + drop both; + rounded size adds EMOJI_ROUNDSIZE=1; + CatmullRom adds EMOJI_FILTER=catmullrom '
          '(+ Lanczos3: EMOJI_FILTER=lanczos3); prototype (atlas changes) = ' + PROTO_ATLAS + '; + EMOJI_CTSMALL adds '
          'EMOJI_CTSMALL=1 to the CatmullRom row.')
    print(f'{"":34s}' + ''.join(f'{s:>14d}' for s in sizes))
    def box(a):
        ys, xs = np.nonzero((255 - a).max(axis=2) > 24)
        return xs.min(), ys.min(), xs.max() + 1
    for tag, name in variants:
        row = f'{name:34s}'
        for s in sizes:
            r = load(f'probe/chr/crab{s}_z1.png')
            a = load(f'probe/{tag}/crab{s}_z1.png' if tag in ('ct', 'wk') else f'probe/{tag}/crab{s}_glyphs_z1.png')
            (ax0, ay0, ax1), (rx0, ry0, rx1) = box(a), box(r)
            row += f'{count(a, r):6d} {ax1 - ax0 - (rx1 - rx0):+d}w{ay0 - ry0:+d}y'.rjust(14)
        print(row)
    for tag, path in (('master', 'probe/base/crab50_glyphs_z1.png'), ('Chromium', 'probe/chr/crab50_z1.png'),
                      ('WebKit', 'probe/wk/crab50_z1.png'), ('CoreText', 'probe/ct/crab50_z1.png')):
        a = load(path)
        ys, xs = np.nonzero((255 - a).max(axis=2) > 24)
        print(f'crab50 ink box, {tag}: x {xs.min()}-{xs.max() + 1}, y {ys.min()}-{ys.max() + 1}')
    files = sorted(os.listdir(f'{INV}/ladder/base'))
    R = os.path.expanduser(os.environ.get('REFS', '~/src/femtovg-wt/runs/zoom/fresh/refs'))
    FR = {1: 'z1', 1.25: 'z125', 1.5: 'z15', 1.75: 'z175', 2: 'z2', 3: 'z3', 4: 'z4', 0.75: 'z075', 0.5: 'z05',
          0.33: 'z033', 0.25: 'z025'}
    wk = lambda f, z: np.asarray(Image.open(f'{R}/wk_wpttext__28-color-emoji-and-png-glyphs__{f}_{FR[z]}.png')
                                 .convert('RGB'), dtype=np.int16)
    print('\n2. Group 28 (28-color-emoji-and-png-glyphs), 460x260 framing, through fill_glyph_run. Pixels beyond 20/255 '
          'off Chromium 131 at each of the 21 ladder steps, master (base) and prototype (fin: the atlas changes and the '
          'direct-route bake at the device scale, sampled linearly: ' + PROTO_ATLAS + ' EMOJI_DIRECT_SCALE=1 '
          'EMOJI_LINEAR=1); then the step against a fresh frame of its zoom.')
    print('steps: ' + ' '.join(f'{z:g}' for z in LADDER))
    sums = {}
    for f in files:
        print(f)
        for tag in ('base', 'fin'):
            c, hyst = [], 0
            for i, z in enumerate(LADDER):
                a = load(f'ladder/{tag}/{f}/step.ppm.{i:02d}.png')
                c.append(count(a, load(f'refs/chr_{f}_z{z:g}.png')))
                hyst = max(hyst, int((dmax(a, load(f'ladder/{tag}/{f}/fresh_{z:g}.png')) > 0).sum()))
            k = c.index(max(c))
            s = sums.setdefault(tag, [0, 0])
            s[0] += c[0]; s[1] += max(c)
            print(f'  {tag:4s} zoom 1 {c[0]:6d}  worst {max(c):6d} at {LADDER[k]:g}  vs WebKit at zoom 1 '
                  f'{count(load(f"ladder/{tag}/{f}/step.ppm.00.png"), wk(f, 1)):6d}  step-vs-fresh max {hyst}  | '
                  + ' '.join(str(v) for v in c))
        cw = [count(load(f'refs/chr_{f}_z{z:g}.png'), wk(f, z)) for z in FR]
        print(f'  Chromium vs WebKit per zoom ({", ".join(f"{z:g}" for z in FR)}): ' + ' '.join(str(v) for v in cw))
    for tag, (z1, worst) in sums.items():
        print(f'all 12 files, {tag}: zoom 1 summed {z1}, worst steps summed {worst}')

    print('\n3. The browsers among themselves at zoom 1 (pixels beyond 20/255 off Chromium 131): Firefox (refs of the '
          'wpt-text run), WebKit re-shot.')
    FF = os.path.expanduser('~/src/femtovg-wt/runs/wpt-text/refs')
    for f in files:
        c = load(f'refs/chr_{f}_z1.png')
        ff = np.asarray(Image.open(f'{FF}/ff_wpttext__28-color-emoji-and-png-glyphs__{f}_z1.png').convert('RGB'),
                        dtype=np.int16)
        print(f'  {f:42s} Firefox {count(ff, c):6d}  WebKit {count(wk(f, 1), c):6d}')
    same = all(int((dmax(load(f'probe/base/crab{s}_glyphs_z1.png'), load(f'probe/base/crab{s}_shape_z1.png')) > 0).sum()) == 0
               for s in sizes)
    print(f'\n4. fill_text (FEMTOVG_TEXT=shape) and fill_glyph_run frames of the crab probe identical at all 13 sizes: {same}')


if __name__ == '__main__':
    {'sheet': sheet, 'strip': strip, 'numbers': numbers}[sys.argv[1]](*sys.argv[2:3])
