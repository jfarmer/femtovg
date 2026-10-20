#!/usr/bin/env python3
"""compare.py: the 13 suite scenes - pixels more than 20/255 off Chromium, master (9f5ad26) and #403 (305f12d), WGPU and
OpenGL; and whether the two backends draw the same."""
import json
import numpy as np
from PIL import Image
names = [s['name'] for s in json.load(open('scenes.json'))['scenes']]
load = lambda d, i: np.asarray(Image.open(f'{d}/{i}.png').convert('RGB'), dtype=np.int16)
tot = {k: 0 for k in ('wgpu-mst', 'wgpu-403', 'gl-mst', 'gl-403')}
print(f'{"scene":46s} {"WGPU master":>12s} {"WGPU #403":>10s} {"GL master":>10s} {"GL #403":>8s}  backends')
for i, name in enumerate(names):
    ref = load('chromium', i)
    row = {}
    for k in tot:
        im = load(k, i)
        row[k] = int((np.abs(im - ref).max(axis=2) > 20).sum())
        tot[k] += row[k]
    same = all((load(f'wgpu-{b}', i) == load(f'gl-{b}', i)).all() for b in ('mst', '403'))
    print(f'{name:46s} {row["wgpu-mst"]:12d} {row["wgpu-403"]:10d} {row["gl-mst"]:10d} {row["gl-403"]:8d}  {"identical" if same else "differ"}')
print(f'{"total":46s} {tot["wgpu-mst"]:12d} {tot["wgpu-403"]:10d} {tot["gl-mst"]:10d} {tot["gl-403"]:8d}')
