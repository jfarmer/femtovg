#!/usr/bin/env python3
"""nyt_408.py [builds=snpf_off,snpf0,snp4,snp8,snp16] [framings=z01,z025,z05,z1]: the NYT marks of #327's table and the
SolidJS banner drawn by each build, against Chromium 131 (runs/pr/refs/chr_*), within the artwork's ink box: ink weight
(sum of 255 - luminance) relative to Chromium's, and the share of the box beyond 20/255. Frames saved to png/ here."""
import json, os, subprocess, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.expanduser('~/src/femtovg-wt/da/harness/corpus_run'))
os.environ.setdefault('CORPUS_RUN_OUT', os.path.expanduser('~/src/femtovg-wt/runs/thin'))
from common import *  # noqa
HERE = os.path.dirname(os.path.abspath(__file__))
REFS = [os.path.expanduser('~/src/femtovg-wt/runs/pr/refs'), os.path.expanduser('~/src/femtovg-wt/runs/thin/refs')]
opts = dict(a.split('=', 1) for a in sys.argv[1:])
builds = opts.get('builds', 'snpf_off,snpf0,snp4,snp8,snp16').split(',')
framings = opts.get('framings', 'z01,z025,z05,z1').split(',')
marks = opts.get('marks', 'enterprise-nyt-evenodd,NYTSiteLogoBlack,NYT-bbcae2eb81842d89e3d0,NYT-letter-boxed,NYT-Crossplay-AppIcon,banner').split(',')
fs = {f['key']: f for f in files()}
lum = lambda X: 0.299 * X[:, :, 0] + 0.587 * X[:, :, 1] + 0.114 * X[:, :, 2]
os.makedirs(f'{HERE}/png', exist_ok=True)


def frame(build, key, fr):
    out = f'{HERE}/png/{build}_{key}_{fr}.png'
    if not os.path.exists(out):
        binary, extra = BUILDS[build]; env, z = FRAMINGS[fr]
        ppm = f'{HERE}/png/tmp.ppm'
        subprocess.run([binary, f'{z:g}', ppm, fs[key]['path']], env={**os.environ, **env, **SWEEP_ENV, **extra}, capture_output=True)
        Image.open(ppm).save(out); os.remove(ppm)
    return np.asarray(Image.open(out).convert('RGB'), dtype=np.int16)


rows = []
print(f"{'mark':28s} {'fr':5s} " + ' '.join(f'{b:>16s}' for b in builds) + '   (ink vs Chromium, % of box beyond 20/255)')
for m in marks:
    key = next(k for k in fs if k.endswith('__' + m))
    for fr in framings:
        ref = next((f'{d}/chr_{key}_{fr}.png' for d in REFS if os.path.exists(f'{d}/chr_{key}_{fr}.png')), None)
        if not ref:
            continue
        C = np.asarray(Image.open(ref).convert('RGB'), dtype=np.int16)
        A = {b: frame(b, key, fr) for b in builds}
        ink = C.sum(axis=2) < 765
        for X in A.values():
            ink |= X[:C.shape[0], :C.shape[1]].sum(axis=2) < 765
        ys, xs = np.nonzero(ink)
        sl = (slice(max(0, ys.min() - 2), ys.max() + 3), slice(max(0, xs.min() - 2), xs.max() + 3))
        wc = (255 - lum(C)[sl]).sum()
        row = {'mark': m, 'framing': fr, 'box': [int(sl[1].start), int(sl[0].start), int(sl[1].stop), int(sl[0].stop)]}
        cells = []
        for b in builds:
            X = A[b][:C.shape[0], :C.shape[1]]
            d = np.abs(X - C).max(axis=2)[sl]
            inkp = 100 * ((255 - lum(X)[sl]).sum() - wc) / max(wc, 1)
            row[b] = [round(inkp, 1), round(100 * float((d > 20).mean()), 2)]
            cells.append(f'{inkp:+6.0f}% {100 * (d > 20).mean():5.1f}%')
        rows.append(row)
        print(f'{m[:28]:28s} {fr:5s} ' + ' '.join(f'{c:>16s}' for c in cells), flush=True)
json.dump(rows, open(f'{HERE}/nyt_408.json', 'w'), indent=1)
