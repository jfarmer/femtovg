#!/usr/bin/env python3
"""inventory.md: every WPT mask/clip test of files.json, % of pixels beyond 20/255 of the area reference per framing
(z1/z2/z4/hd), for the builds and the four browsers; 'old refs' = corpus_run's make_ref.py, the rest refs_fixed/
(this directory's make_ref.py) where it made one. Bold = not within 0.15 % at every framing."""
import json, os, numpy as np
from PIL import Image
H = os.path.dirname(os.path.abspath(__file__))
FR = ['z1', 'z2', 'z4', 'hd']
fs = [f for f in json.load(open(f'{H}/files.json')) if f['group'].startswith('wpt') and f['group'] != 'wpt-pservers-reftests'
      and not (f['key'].endswith('-ref') or f['key'].endswith('-expected'))]
cache = {}


def L(p):
    if p not in cache:
        cache[p] = np.asarray(Image.open(p).convert('RGB'), dtype=np.int16) if os.path.exists(p) else None
    return cache[p]


def ref(w, k, fr, fixed):
    if fixed and os.path.exists(f'{H}/refs_fixed/{w}_{k}_{fr}.png'):
        return L(f'{H}/refs_fixed/{w}_{k}_{fr}.png')
    return L(f'{H}/refs/{w}_{k}_{fr}.png')


def b(a, c):
    return None if a is None or c is None else 100 * float((np.abs(a - c).max(axis=2) > 20).mean())


def cell(v):
    ok = all(x is not None and x <= 0.15 for x in v)
    s = '/'.join('-' if x is None else (f'{x:.2f}' if x < 10 else f'{x:.1f}') for x in v)
    return s if ok else f'**{s}**'


cols = [('m7 (old refs)', 'm7', False), ('cm8 (old refs)', 'cm8', False), ('m7', 'm7', True), ('cm8', 'cm8', True),
        ('wmp', 'wmp', True), ('wmm', 'wmm', True), ('wm1', 'wm1', True),
        ('chr', 'chr', True), ('chg', 'chg', True), ('ff', 'ff', True), ('wk', 'wk', True)]
out = ['| group | test | ' + ' | '.join(c[0] for c in cols) + ' |', '|---|---|' + '---|' * len(cols)]
passes = {c[0]: [0, 0] for c in cols}
for f in fs:
    k = f['key']
    row = []
    for label, w, fixed in cols:
        if w in ('chr', 'chg', 'ff', 'wk'):
            v = [b(ref(w, k, fr, fixed), ref('id', k, fr, fixed)) for fr in FR]
        else:
            v = [b(L(f'{H}/png/{w}_{k}_{fr}.png'), ref('id', k, fr, fixed)) for fr in FR]
        if any(x is None for x in v):
            row.append('n/a')
            continue
        passes[label][1] += 1
        if all(x <= 0.15 for x in v):
            passes[label][0] += 1
        row.append(cell(v))
    name = k.split('__', 2)[-1] if f['group'] == 'wpt' else k.split('__')[-1]
    out.append(f"| {f['group']} | {name} | " + ' | '.join(row) + ' |')
out.append('')
out.append('Within 0.15 % of the area reference at every framing: ' + ', '.join(f'{k} {p}/{n}' for k, (p, n) in passes.items()))
open(f'{H}/inventory.md', 'w').write('\n'.join(out) + '\n')
print(out[-1])
