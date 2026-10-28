#!/usr/bin/env python3
"""Pairwise share of pixels beyond 20/255 (max channel) between renderers, per file: compare.json + a table."""
import json, os, sys
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
R = ['r48', 'r49', 'rfx', 'chrome', 'firefox', 'webkit', 'stp']
B = ['chrome', 'firefox', 'webkit', 'stp']
def load(r, n):
    p = f'{HERE}/out/{r}/{n}.png'
    return np.asarray(Image.open(p).convert('RGB'), dtype=np.int16) if os.path.exists(p) else None
def diff(a, b):
    if a is None or b is None or a.shape != b.shape: return None
    return float((np.abs(a - b).max(2) > 20).mean() * 100)
names = sorted(f[:-4] for f in os.listdir(f'{HERE}/svg') if f.endswith('.svg'))
res = {}
for n in names:
    im = {r: load(r, n) for r in R}
    res[n] = {f'{a}~{b}': diff(im[a], im[b]) for i, a in enumerate(R) for b in R[i + 1:]}
json.dump(res, open(f'{HERE}/compare.json', 'w'), indent=1)
f = lambda v: '   -  ' if v is None else f'{v:6.2f}'
print(f'{"file":52} | {"ch~ff":>6} {"ch~wk":>6} {"ff~wk":>6} {"wk~tp":>6} | r48: {"ch":>6} {"ff":>6} {"wk":>6} | r49: {"ch":>6} {"ff":>6} {"tp":>6} | fix: {"ch":>6} {"ff":>6} {"tp":>6}')
for n in names:
    d = res[n]
    print(f'{n[-52:]:52} | {f(d["chrome~firefox"])} {f(d["chrome~webkit"])} {f(d["firefox~webkit"])} {f(d["webkit~stp"])} |      {f(d["r48~chrome"])} {f(d["r48~firefox"])} {f(d["r48~webkit"])} |      {f(d["r49~chrome"])} {f(d["r49~firefox"])} {f(d["r49~stp"])} |      {f(d["rfx~chrome"])} {f(d["rfx~firefox"])} {f(d["rfx~stp"])}')
