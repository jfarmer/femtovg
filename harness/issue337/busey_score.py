#!/usr/bin/env python3
"""busey_score.py: BuseyBench (27 files) with s48 (master ad762cd5 + #408 + #403) against Chromium 131, Firefox DE 159
and WebKit (macOS 27.2), at 460x260 (z1) and 1080p (hd): mean px > 20/255 and structural share (beyond 20/255 after a
2 px erosion), with the browsers' own envelopes. Writes busey_score.json."""
import glob, json, os, statistics as st
import numpy as np
from PIL import Image
REFS = os.path.expanduser('~/src/femtovg-wt/runs/thin/refs')
PNG = 'busey_png'
def erode(m, it=2):
    for _ in range(it):
        m = m & np.roll(m, 1, 0) & np.roll(m, -1, 0) & np.roll(m, 1, 1) & np.roll(m, -1, 1)
    return m
def cmp(a, b):
    h, w = min(a.shape[0], b.shape[0]), min(a.shape[1], b.shape[1])
    d = np.abs(a[:h, :w] - b[:h, :w]).max(axis=2) > 20
    return 100 * float(d.mean()), 100 * float(erode(d).mean())
L = lambda p: np.asarray(Image.open(p).convert('RGB'), dtype=np.int16) if os.path.exists(p) else None
keys = sorted({os.path.basename(p)[4:-7] for p in glob.glob(f'{PNG}/s48_*_z1.png')})
rows = {}
for fr in ('z1', 'hd'):
    for k in keys:
        ours = L(f'{PNG}/s48_{k}_{fr}.png')
        refs = {b: L(f'{REFS}/{b}_{k}_{fr}.png') for b in ('chr', 'ff', 'wk', 'id')}
        r = {}
        for b, ref in refs.items():
            if ref is not None:
                r[b] = cmp(ours, ref)
        if refs['chr'] is not None:
            for b in ('ff', 'wk'):
                if refs[b] is not None:
                    r[f'chr_vs_{b}'] = cmp(refs[b], refs['chr'])
        rows[(fr, k)] = r
json.dump({f'{fr}|{k}': v for (fr, k), v in rows.items()}, open('busey_score.json', 'w'), indent=1)
for fr in ('z1', 'hd'):
    print(f'--- {fr}')
    for b in ('chr', 'ff', 'wk', 'id', 'chr_vs_ff', 'chr_vs_wk'):
        vals = [v[b] for (f, k), v in rows.items() if f == fr and b in v]
        if vals:
            under = sum(s < 0.5 for _, s in vals)
            print(f'{b:10s} n={len(vals):2d} mean px>20 {st.mean(p for p, _ in vals):6.3f} %  mean structural {st.mean(s for _, s in vals):6.3f} %  structural < 0.5 %: {under}/{len(vals)}')
    worst = sorted(((v['chr'][1], k) for (f, k), v in rows.items() if f == fr and 'chr' in v), reverse=True)[:6]
    print('worst structural vs Chromium:', [(k.split('__')[-1], round(s, 3)) for s, k in worst])
