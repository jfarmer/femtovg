#!/usr/bin/env python3
"""mystrip.py OUT.gif crop=x,y,w,h scale=N steps=a,b,c ref=NAME label=TEXT name=pattern ... [diff=name,name]
Animated strip over zoom-ladder steps: one panel per name=pattern ({fr} -> framing), then, for each name in diff=,
its difference against the ref= panel: red where it puts down more ink than the reference by more than 8/255,
blue where less; fainter shades below 8/255 (x6). Writes OUT.gif and OUT.webp (lossless)."""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.expanduser('~/src/femtovg-wt/da/harness/corpus_run'))
from zoom_ladder import LADDER, FRAMING_OF
out = sys.argv[1]
opts = {}; panels = []
for a in sys.argv[2:]:
    k, v = a.split('=', 1)
    if k in ('crop', 'scale', 'steps', 'ref', 'label', 'diff', 'ms', 'follow'):
        opts[k] = v
    else:
        panels.append((k, v))
x, y, w, h = map(int, opts['crop'].split(','))
s = int(opts.get('scale', 3))
steps = [int(t) for t in opts['steps'].split(',')]
ref = opts['ref']; diffs = opts.get('diff', '').split(',') if opts.get('diff') else []
try:
    font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 13)
except OSError:
    font = ImageFont.load_default()
frames = []
for st in steps:
    z = LADDER[st]; fr = FRAMING_OF[z]
    imgs = {}
    for n, p in panels:
        f = p.replace('{fr}', fr).replace('{step}', f'{st:02}')
        imgs[n] = np.asarray(Image.open(f).convert('RGB'), dtype=np.int32) if os.path.exists(f) else None
    tiles = [(n, imgs[n]) for n, _ in panels]
    r = imgs[ref]
    for n in diffs:
        a = imgs[n]
        if a is None or r is None:
            tiles.append((f'{n} vs {ref}: -', None)); continue
        sd = (a - r).mean(axis=2); m = np.abs(a - r).max(axis=2)
        img = np.zeros(a.shape, np.int32) + 24
        img[..., 0] += np.clip(-sd * 6, 0, 200).astype(np.int32)
        img[..., 2] += np.clip(sd * 6, 0, 200).astype(np.int32)
        bad = m > 8
        img[bad & (sd <= 0)] = [255, 50, 50]; img[bad & (sd > 0)] = [70, 140, 255]
        tiles.append((f'{n} vs {ref}: {int(bad.sum())} px > 8/255', img))
    if opts.get('follow'):  # follow=cx,cy: a frame point at zoom 1 the crop stays centred on as the ladder zooms
        fx, fy = map(float, opts['follow'].split(','))
        x = max(0, min(460 - w, int(round(230 + (fx - 230) * z - w / 2)))); y = max(0, min(260 - h, int(round(130 + (fy - 130) * z - h / 2))))
    W, H = w * s, h * s
    pad, top = 6, 42
    canvas = Image.new('RGB', (len(tiles) * (W + pad) + pad, H + top + pad), (36, 36, 36))
    d = ImageDraw.Draw(canvas)
    d.text((pad, 4), f"{opts.get('label', '')}   zoom {z:g} (ladder step {st + 1} of {len(LADDER)})", fill=(255, 255, 255), font=font)
    for i, (n, a) in enumerate(tiles):
        X = pad + i * (W + pad)
        d.text((X, 23), n, fill=(220, 220, 220), font=font)
        if a is not None:
            im = Image.fromarray(np.clip(a[y:y + h, x:x + w], 0, 255).astype(np.uint8)).resize((W, H), Image.NEAREST)
            canvas.paste(im, (X, top))
    frames.append(canvas)
ms = int(opts.get('ms', 900))
frames[0].save(out, save_all=True, append_images=frames[1:], duration=ms, loop=0, optimize=True)
frames[0].save(os.path.splitext(out)[0] + '.webp', save_all=True, append_images=frames[1:], duration=ms, loop=0, lossless=True, method=4)
for i, f in enumerate(frames):
    f.save(os.path.splitext(out)[0] + f'_{steps[i]:02}.png')
print(out, len(frames), frames[0].size)
