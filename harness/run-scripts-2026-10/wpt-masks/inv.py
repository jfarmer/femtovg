#!/usr/bin/env python3
"""Per test and framing: % of pixels beyond 20/255 of the area reference (refs/id_*), for builds and browsers.

  inv.py BUILD[,BUILD...] [group=NAME]... [match=SUBSTR]... [refs=chr,chg,ff,wk] [tests=1] [fmt=md|tsv] [only_fail=1]

A test passes when it is within 0.15 % at every framing (z1 z2 z4 hd)."""
import json, os, sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
FR = ['z1', 'z2', 'z4', 'hd']
builds = sys.argv[1].split(',')
groups, matches, refs, only_fail, fmt, include_refs = set(), [], ['chr', 'chg', 'ff', 'wk'], False, 'md', False
refdir = None
for a in sys.argv[2:]:
    k, v = a.split('=', 1)
    if k == 'group':
        groups.add(v)
    elif k == 'match':
        matches.append(v)
    elif k == 'refs':
        refs = v.split(',') if v else []
    elif k == 'only_fail':
        only_fail = v == '1'
    elif k == 'fmt':
        fmt = v
    elif k == 'refdir':
        refdir = v
    elif k == 'with_refs':
        include_refs = v == '1'
fs = json.load(open(f'{HERE}/files.json'))
fs = [f for f in fs if (not groups or f['group'] in groups) and (not matches or any(m in f['key'] for m in matches))
      and (include_refs or not (f['key'].endswith('-ref') or f['key'].endswith('-expected')))]
_cache = {}


def load(p):
    if p not in _cache:
        _cache[p] = np.asarray(Image.open(p).convert('RGB'), dtype=np.int16) if os.path.exists(p) else None
    return _cache[p]


def beyond(a, b):
    if a is None or b is None or a.shape != b.shape:
        return None
    return 100 * float((np.abs(a - b).max(axis=2) > 20).mean())


def frame(who, key, fr):
    if who in ('chr', 'chg', 'ff', 'wk', 'id'):
        if refdir and os.path.exists(f'{HERE}/{refdir}/{who}_{key}_{fr}.png'):
            return load(f'{HERE}/{refdir}/{who}_{key}_{fr}.png')
        return load(f'{HERE}/refs/{who}_{key}_{fr}.png')
    return load(f'{HERE}/png/{who}_{key}_{fr}.png')


who = builds + refs
rows = []
for f in fs:
    k = f['key']
    vals = {w: [beyond(frame(w, k, fr), frame('id', k, fr)) for fr in FR] for w in who}
    passes = {w: all(v is not None and v <= 0.15 for v in vals[w]) for w in who}
    rows.append((f['group'], k, vals, passes))


def cell(vs, ok):
    s = '/'.join('-' if v is None else (f'{v:.2f}' if v < 10 else f'{v:.1f}') for v in vs)
    return f'**{s}**' if not ok else s


if fmt == 'md':
    print('| group | test | ' + ' | '.join(who) + ' |')
    print('|---|---|' + '---|' * len(who))
for g, k, vals, passes in rows:
    if only_fail and all(passes[b] for b in builds):
        continue
    name = k.split('__', 2)[-1] if g == 'wpt' else k.split('__')[-1]
    if fmt == 'md':
        print(f'| {g} | {name} | ' + ' | '.join(cell(vals[w], passes[w]) for w in who) + ' |')
    else:
        print('\t'.join([g, name] + [cell(vals[w], passes[w]) for w in who]))
print()
for w in who:
    n = sum(1 for _, _, _, p in rows if p[w])
    print(f'{w}: {n} of {len(rows)} within 0.15 % at every framing')
