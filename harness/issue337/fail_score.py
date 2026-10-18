#!/usr/bin/env python3
"""fail_score.py: the 23 reftest pairs s48 (master ad762cd5 + #408 + #403) draws more than 0.15 % px>20 off Chromium:
femtovg's test frame against each browser's (worst framing of z1, z2, z4, hd), and each browser's own test frame
against its reference frame (whether the suite's reference agrees with that browser). Writes fail_score.json."""
import json, os
import numpy as np
from PIL import Image
R = os.path.expanduser('~/src/femtovg-wt/runs/wpt22')
FR = ['z1', 'z2', 'z4', 'hd']
L = lambda p: np.asarray(Image.open(p).convert('RGB'), dtype=np.int16) if os.path.exists(p) else None
def px20(a, b):
    if a is None or b is None:
        return None
    h, w = min(a.shape[0], b.shape[0]), min(a.shape[1], b.shape[1])
    return 100 * float((np.abs(a[:h, :w] - b[:h, :w]).max(axis=2) > 20).mean())
def worst(vals):
    vals = [v for v in vals if v is not None]
    return round(max(vals), 2) if vals else None
rows = []
for pid, tk, rk in json.load(open('fail_pairs.json')):
    row = {'pair': pid, 'group': tk.split('__')[1][:2]}
    ours = {fr: L(f'{R}/png/s48_{tk}_{fr}.png') for fr in FR}
    row['self'] = worst(px20(ours[fr], L(f'{R}/png/s48_{rk}_{fr}.png')) for fr in FR)
    for b in ('chr', 'ff', 'wk'):
        row[f'vs_{b}'] = worst(px20(ours[fr], L(f'{R}/refs/{b}_{tk}_{fr}.png')) for fr in FR)
        row[f'{b}_self'] = worst(px20(L(f'{R}/refs/{b}_{tk}_{fr}.png'), L(f'{R}/refs/{b}_{rk}_{fr}.png')) for fr in FR)
    row['chr_vs_ff'] = worst(px20(L(f'{R}/refs/chr_{tk}_{fr}.png'), L(f'{R}/refs/ff_{tk}_{fr}.png')) for fr in FR)
    row['chr_vs_wk'] = worst(px20(L(f'{R}/refs/chr_{tk}_{fr}.png'), L(f'{R}/refs/wk_{tk}_{fr}.png')) for fr in FR)
    rows.append(row)
json.dump(rows, open('fail_score.json', 'w'), indent=1)
print(f'{"pair":44s} grp  self   vsChr   vsFF   vsWK | chrSelf ffSelf wkSelf | chr~ff chr~wk')
for r in sorted(rows, key=lambda r: (r['group'], r['pair'])):
    f = lambda v: f'{v:6.2f}' if v is not None else '     -'
    print(f"{r['pair'][:44]:44s} {r['group']}  {f(r['self'])} {f(r['vs_chr'])} {f(r['vs_ff'])} {f(r['vs_wk'])} | {f(r['chr_self'])} {f(r['ff_self'])} {f(r['wk_self'])} | {f(r['chr_vs_ff'])} {f(r['chr_vs_wk'])}")
