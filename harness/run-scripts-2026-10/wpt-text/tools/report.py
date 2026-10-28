#!/usr/bin/env python3
"""report.py BUILD [BUILD2]: per test file of the text groups, femtovg's frame vs Chromium and Firefox of the same
file (px20, %), Chromium vs Firefox, and the self-reftest (femtovg test vs femtovg ref, Chromium test vs Chromium ref).
Worst framing per file."""
import collections, json, os, sys
import numpy as np
from PIL import Image
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
builds = sys.argv[1:]
acc = {}
for l in open(f'{R}/accuracy.jsonl'):
    r = json.loads(l)
    if 'vs_chr' in r:
        acc[(r['key'], r['framing'], r['build'])] = r
pairs = json.load(open(f'{R}/pairs.json'))
def load(p):
    return np.asarray(Image.open(p).convert('RGB'), dtype=np.int16) if os.path.exists(p) else None
def px20(a, b):
    if a is None or b is None: return None
    h, w = min(a.shape[0], b.shape[0]), min(a.shape[1], b.shape[1])
    return 100.0 * (np.abs(a[:h, :w] - b[:h, :w]).max(axis=2) > 20).mean()
FR = ['z1', 'z2', 'hd']
def worst(vals):
    v = [x for x in vals if x is not None]
    return max(v) if v else None
f = lambda x: '   -' if x is None else f'{x:6.2f}'
print(f"{'pair':58s} " + ' '.join(f'{b+"/chr":>9s} {b+"/ff":>8s}' for b in builds) + '  chr/ff  self  chrself')
for pid, tk, rk in pairs:
    cols = []
    for b in builds:
        cols.append(worst(acc.get((tk, fr, b), {}).get('vs_chr', {}).get('px20') for fr in FR))
        cols.append(worst(acc.get((tk, fr, b), {}).get('vs_ff', {}).get('px20') for fr in FR))
    chrff = worst(acc.get((tk, fr, builds[0]), {}).get('chr_vs_ff', {}).get('px20') for fr in FR)
    selfr = worst(px20(load(f'{R}/png/{builds[0]}_{tk}_{fr}.png'), load(f'{R}/png/{builds[0]}_{rk}_{fr}.png')) for fr in FR)
    chrself = worst(px20(load(f'{R}/refs/chr_{tk}_{fr}.png'), load(f'{R}/refs/chr_{rk}_{fr}.png')) for fr in FR)
    print(f"{tk.split('__',1)[1][:58]:58s} " + ' '.join(f'{f(c):>9s}' for c in cols) + f'  {f(chrff)} {f(selfr)} {f(chrself)}')
