#!/usr/bin/env python3
"""score.py BUILD: BuseyBench (31 files) with BUILD against Chromium 131, Firefox 159, WebKit (macOS 27.2) and the 8x
area reference at z1 (460x260), z2 and hd (1080p): px > 20/255 and structural share (beyond 20/255 after a 2 px
erosion) per file, the browsers' envelopes, and the files ranked by how far they are from the nearest browser.
Writes score_BUILD.json."""
import json, os, sys, statistics as st
import numpy as np
from PIL import Image
b = sys.argv[1]
R = 'refs'
def erode(m, it=2):
    for _ in range(it):
        m = m & np.roll(m, 1, 0) & np.roll(m, -1, 0) & np.roll(m, 1, 1) & np.roll(m, -1, 1)
    return m
def cmp(a, c):
    h, w = min(a.shape[0], c.shape[0]), min(a.shape[1], c.shape[1])
    d = np.abs(a[:h, :w] - c[:h, :w]).max(axis=2) > 20
    return round(100 * float(d.mean()), 4), round(100 * float(erode(d).mean()), 4)
L = lambda p: np.asarray(Image.open(p).convert('RGB'), dtype=np.int16) if os.path.exists(p) else None
files = json.load(open('files.json'))
rows = {}
for fr in ('z1', 'z2', 'hd'):
    for f in files:
        k = f['key']
        ours = L(f'png/{b}_{k}_{fr}.png')
        if ours is None:
            continue
        refs = {x: L(f'{R}/{x}_{k}_{fr}.png') for x in ('chr', 'ff', 'wk', 'id')}
        r = {x: cmp(ours, ref) for x, ref in refs.items() if ref is not None}
        if refs['chr'] is not None:
            for x in ('ff', 'wk'):
                if refs[x] is not None:
                    r[f'chr_vs_{x}'] = cmp(refs[x], refs['chr'])
            if refs['ff'] is not None and refs['wk'] is not None:
                r['ff_vs_wk'] = cmp(refs['wk'], refs['ff'])
        rows[f'{fr}|{k}'] = r
json.dump(rows, open(f'score_{b}.json', 'w'), indent=1)
for fr in ('z1', 'z2', 'hd'):
    rs = {k.split('|')[1]: v for k, v in rows.items() if k.startswith(fr + '|')}
    print(f'--- {fr}: mean px>20 / structural over {len(rs)} files')
    for x in ('chr', 'ff', 'wk', 'id', 'chr_vs_ff', 'chr_vs_wk', 'ff_vs_wk'):
        vals = [v[x] for v in rs.values() if x in v]
        print(f'  {x:10s} {st.mean(p for p, _ in vals):6.3f} % / {st.mean(s for _, s in vals):6.3f} %   structural < 0.5 %: {sum(s < 0.5 for _, s in vals)}/{len(vals)}')
    worst = sorted(rs.items(), key=lambda kv: -min(kv[1][x][1] for x in ('chr', 'ff', 'wk')))[:10]
    print('  farthest from the nearest browser (structural chr/ff/wk/area, browsers own spread chr~ff chr~wk):')
    for k, v in worst:
        print(f"    {k.split('__')[-1]:38s} {v['chr'][1]:6.3f} {v['ff'][1]:6.3f} {v['wk'][1]:6.3f} {v['id'][1]:6.3f}   spread {v['chr_vs_ff'][1]:6.3f} {v['chr_vs_wk'][1]:6.3f}   px>20 chr {v['chr'][0]:6.3f}")
