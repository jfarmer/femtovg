#!/usr/bin/env python3
"""strip4.py OUT.png ROW...: rows of panels, each a build's frame (or Chromium's) cropped to the artwork and scaled
up with nearest neighbour, with ink weight against the reference (Chromium 131, or the 8x area) and the share of the crop beyond 20/255.
ROW = label|KEY|FRAMING|build[=name],build[=name],...  (the last panel is always Chromium 131)"""
import os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.expanduser('~/src/femtovg-wt/da/harness/corpus_run'))
os.environ.setdefault('CORPUS_RUN_OUT', os.path.expanduser('~/src/femtovg-wt/runs/thin'))
from common import *  # noqa
HERE = os.path.dirname(os.path.abspath(__file__))
REFS = [os.path.expanduser('~/src/femtovg-wt/runs/pr/refs'), os.path.expanduser('~/src/femtovg-wt/runs/thin/refs')]
fs = {f['key']: f for f in files()}
font = lambda n: ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', n)
lum = lambda X: 0.299 * X[:, :, 0] + 0.587 * X[:, :, 1] + 0.114 * X[:, :, 2]


def frame(build, key, fr):
    out = f'{HERE}/{build}_{key}_{fr}.png'
    if not os.path.exists(out):
        binary, extra = BUILDS[build]; env, z = FRAMINGS[fr]
        subprocess.run([binary, f'{z:g}', f'{HERE}/t.ppm', fs[key]['path']], env={**os.environ, **env, **SWEEP_ENV, **extra}, capture_output=True)
        Image.open(f'{HERE}/t.ppm').save(out); os.remove(f'{HERE}/t.ppm')
    return Image.open(out).convert('RGB')


rows = []
for spec in sys.argv[2:]:
    label, key, fr, builds = spec.split('|')
    key = next(k for k in fs if k.endswith(key))
    names = [(b.split('=') + [b])[:2] for b in builds.split(',')]
    ims = [(n, frame(b, key, fr)) for b, n in names]
    # Chromium 131, or the 8x area reference where no Chromium frame was made (the p240 framing).
    found = [(f'{d}/{p}_{key}_{fr}.png', n) for p, n in (('chr', 'Chromium 131'), ('id', '8x area')) for d in REFS
             if os.path.exists(f'{d}/{p}_{key}_{fr}.png')]
    ref, refname = found[0]
    ims.append((refname, Image.open(ref).convert('RGB')))
    A = [np.asarray(im, dtype=np.int16) for _, im in ims]
    C = A[-1]
    ink = np.zeros(C.shape[:2], bool)
    for X in A:
        ink |= X[:C.shape[0], :C.shape[1]].sum(axis=2) < 750
    ys, xs = np.nonzero(ink)
    box = (max(0, xs.min() - 2), max(0, ys.min() - 2), min(C.shape[1], xs.max() + 3), min(C.shape[0], ys.max() + 3))
    sl = (slice(box[1], box[3]), slice(box[0], box[2]))
    wc = (255 - lum(C)[sl]).sum()
    w, h = box[2] - box[0], box[3] - box[1]
    s = max(1, min(8, 260 // max(h, 1), 420 // max(w, 1)))
    panels = []
    for (n, im), X in zip(ims, A):
        X = X[:C.shape[0], :C.shape[1]]
        d = np.abs(X - C).max(axis=2)[sl]
        cap = n if n == refname else f'{n}: ink {100 * ((255 - lum(X)[sl]).sum() - wc) / max(wc, 1):+.0f} %, {100 * (d > 20).mean():.1f} % beyond'
        pic = im.crop(box).resize((w * s, h * s), Image.NEAREST)
        # Padded to its caption's width, so that captions do not run into each other.
        need = int(font(11).getlength(cap)) + 6
        if pic.size[0] < need:
            padded = Image.new('RGB', (need, pic.size[1]), 'white'); padded.paste(pic, ((need - pic.size[0]) // 2, 0)); pic = padded
        panels.append((cap, pic))
    rows.append((f'{label} ({w}x{h} px crop, x{s})', panels))
gap, head = 10, 34
W = max(sum(p.size[0] for _, p in ps) + gap * (len(ps) + 1) for _, ps in rows)
H = sum(ps[0][1].size[1] + head + gap for _, ps in rows) + gap
sheet = Image.new('RGB', (max(W, 900), H), 'white'); dr = ImageDraw.Draw(sheet); y = gap
for label, ps in rows:
    dr.text((gap, y), label, fill=(0, 0, 0), font=font(13)); x = gap
    for cap, p in ps:
        dr.text((x, y + 17), cap, fill=(80, 80, 80), font=font(11)); sheet.paste(p, (x, y + head))
        dr.rectangle([x - 1, y + head - 1, x + p.size[0], y + head + p.size[1]], outline=(200, 200, 200)); x += p.size[0] + gap
    y += ps[0][1].size[1] + head + gap
sheet.save(sys.argv[1]); print(sys.argv[1], sheet.size)
