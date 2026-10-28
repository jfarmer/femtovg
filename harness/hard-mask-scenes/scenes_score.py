#!/usr/bin/env python3
"""scenes_score.py: the 13 suite scenes at 1x, 2x, 4x - pixels more than 20/255 off Chromium, Firefox and WebKit for
master (m403 = ad762cd5) and #403 (h403 = 59fbefb9) on WGPU and OpenGL, and, for every pixel the PR changes, whether it
moved toward each browser or away. Writes scenes_score.json."""
import json, os
import numpy as np
from PIL import Image
names = [s['name'] for s in json.load(open(os.path.expanduser('~/src/femtovg-wt/da/harness/hard-mask-scenes/scenes-suite18.json')))['scenes']]
L = lambda d, i: np.asarray(Image.open(f'{d}/{i}.png').convert('RGB'), dtype=np.int16)
dirs = {'wgpu': ('wgpu-mst-{s}', 'wgpu-hm-{s}'), 'gl': ('gl-m403-{s}', 'gl-h403-{s}')}
browsers = {'chr': 'chr-{s}', 'ff': 'fir-{s}', 'wk': 'web-{s}'}
rows = []
for s in (1, 2, 4):
    for i, name in enumerate(names):
        row = {'scene': name, 'scale': s}
        for be, (bd, ad) in dirs.items():
            before, after = L(bd.format(s=s), i), L(ad.format(s=s), i)
            changed = np.abs(before - after).max(axis=2) > 0
            row[f'{be}_changed'] = int(changed.sum())
            for br, rd in browsers.items():
                ref = L(rd.format(s=s), i)
                db, da = np.abs(before - ref).max(axis=2), np.abs(after - ref).max(axis=2)
                row[f'{be}_{br}'] = [int((db > 20).sum()), int((da > 20).sum())]
                row[f'{be}_{br}_toward'] = [int((changed & (da < db)).sum()), int((changed & (da > db)).sum())]
        row['backends_same'] = all((L(dirs['wgpu'][k].format(s=s), i) == L(dirs['gl'][k].format(s=s), i)).all() for k in (0, 1))
        rows.append(row)
json.dump(rows, open('scenes_score.json', 'w'), indent=1)
for s in (1, 2, 4):
    print(f'--- {s}x: px > 20 off Chromium / Firefox / WebKit, master -> #403 (WGPU; OpenGL)')
    tot = {}
    for r in (r for r in rows if r['scale'] == s):
        cells = []
        for be in ('wgpu', 'gl'):
            cells.append(' '.join(f"{r[f'{be}_{br}'][0]}->{r[f'{be}_{br}'][1]}" for br in browsers))
            for br in browsers:
                for k in (0, 1):
                    tot[(be, br, k)] = tot.get((be, br, k), 0) + r[f'{be}_{br}'][k]
        far = sum(r[f'{be}_{br}_toward'][1] for be in dirs for br in browsers)
        print(f"{r['scene'][10:]:34s} {cells[0]:26s}; {cells[1]:26s} changed {r['wgpu_changed']:5d}/{r['gl_changed']:5d} away {far} {'' if r['backends_same'] else 'BACKENDS DIFFER'}")
    print('total', {f'{be}_{br}': f'{tot[(be, br, 0)]}->{tot[(be, br, 1)]}' for be in dirs for br in browsers})
