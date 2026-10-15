#!/usr/bin/env python3
"""corpus_strip.py A B OUT.png KEY:FRAMING ... : for each corpus frame, render builds A and B and Chromium 131,
crop CROP x CROP pixels (env, default 12) around the pixels A and B render differently, and write a five-column strip (A, B, Chromium,
A vs Chromium, B vs Chromium) with strip.py. Frames go to tmp/strip/."""
import json, os, subprocess, sys
from PIL import Image
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'corpus_run'))
from common import *  # noqa: E402,F403

A, B, out, frames = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:]
HERE = os.environ.get('CORPUS_RUN_OUT', os.getcwd())
TMP = f'{HERE}/tmp/strip'
os.makedirs(TMP, exist_ok=True)
by_key = {f['key']: f for f in files()}
rows = []
for spec in frames:
    key, framing = spec.rsplit(':', 1)
    f = by_key[key]
    fr, z = FRAMINGS[framing]
    w, h = int(fr['FRAME_W']), int(fr['FRAME_H'])
    tag = f"{key.split('__', 1)[1]}_{framing}".replace('/', '_')
    pngs = {}
    for build in (A, B):
        binary, extra = BUILDS[build]
        ppm = f'{TMP}/{tag}_{build}.ppm'
        subprocess.run([binary, f'{z:g}', ppm, f['path']], env={**os.environ, **fr, **SWEEP_ENV, **extra},
                       capture_output=True, timeout=600)
        pngs[build] = f'{TMP}/{tag}_{build}.png'
        Image.open(ppm).convert('RGB').save(pngs[build])
        os.remove(ppm)
    html = f'{TMP}/{tag}.html'
    r = subprocess.run([sys.executable, f'{HARN}/make_ref.py', f['path'], str(z)], capture_output=True, text=True,
                       env={**os.environ, **fr})
    open(html, 'w').write(r.stdout)
    chromium = f'{TMP}/{tag}_chromium.png'
    subprocess.run([CHR, '--headless', '--hide-scrollbars', '--force-device-scale-factor=1', f'--window-size={w},{h}',
                    f'--screenshot={chromium}', f'file://{html}'], capture_output=True, timeout=300)
    Image.open(chromium).convert('RGB').crop((0, 0, w, h)).save(chromium)
    a = np.asarray(Image.open(pngs[A])).astype(int)
    b = np.asarray(Image.open(pngs[B])).astype(int)
    ys, xs = np.nonzero(np.abs(a - b).max(axis=2) > 2)
    cx, cy = int(np.median(xs)), int(np.median(ys))
    c = int(os.environ.get('CROP', 12)); x0, y0 = min(max(cx - c // 2, 0), w - c), min(max(cy - c // 2, 0), h - c)
    label = f"{key.split('__', 1)[1]} at {framing}, pixels ({x0}..{x0 + c - 1}, {y0}..{y0 + c - 1})"
    rows.append(f'{label}={chromium},{pngs[A]},{pngs[B]}@{x0},{y0},{x0 + c},{y0 + c}')
subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'hard-mask-scenes', 'strip.py'), out] + rows,
               env={**os.environ, 'SCALE': os.environ.get('SCALE', '16')}, check=True)
