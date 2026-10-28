#!/usr/bin/env python3
"""Frames of the wpt22 set within a threshold of each browser, per build: the share of pixels more than
20/255 off the reference (any channel) at or under LIMIT %.

  near_counts.py [limit=0.1] [builds=v027,v028] [framings=z1,z2,z4,hd]"""
import collections, json, os, sys
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from PIL import Image

D = os.path.dirname(os.path.abspath(__file__))
opts = dict(a.split('=', 1) for a in sys.argv[1:])
LIMIT = float(opts.get('limit', 0.1))
BUILDS = opts.get('builds', 'v027,v028').split(',')
FRAMINGS = opts.get('framings', 'z1,z2,z4,hd').split(',')
REFS = {'chr': 'Chromium 131', 'ff': 'Firefox 158', 'wk': 'WebKit (Safari 27.2)'}
keys = [f['key'] for f in json.load(open(f'{D}/files.json'))]


def load(p):
    return np.asarray(Image.open(p).convert('RGB')).astype(np.int16) if os.path.exists(p) else None


def job(kf):
    key, fr = kf
    refs = {r: load(f'{D}/refs/{r}_{key}_{fr}.png') for r in REFS}
    out = {}
    for b in BUILDS:
        im = load(f'{D}/png_rel/{b}_{key}_{fr}.png')
        for r, ref in refs.items():
            if im is not None and ref is not None and im.shape == ref.shape:
                out[(b, r)] = 100 * (np.abs(im - ref).max(2) > 20).mean()
    # The browsers against each other: how close the references themselves are.
    for a, c in (('ff', 'chr'), ('wk', 'chr'), ('wk', 'ff')):
        if refs[a] is not None and refs[c] is not None and refs[a].shape == refs[c].shape:
            out[(a, c)] = 100 * (np.abs(refs[a] - refs[c]).max(2) > 20).mean()
    return kf, out


def main():
    with ProcessPoolExecutor(8) as ex:
        rows = dict(ex.map(job, [(k, f) for k in keys for f in FRAMINGS], chunksize=16))
    json.dump({f'{k}|{f}': {f'{b}|{r}': v for (b, r), v in o.items()} for (k, f), o in rows.items()},
              open(f'{D}/near_counts.json', 'w'))

    print(f'frames within {LIMIT} % of pixels beyond 20/255 of the reference ({len(keys)} files x {len(FRAMINGS)} framings)')
    for r, name in REFS.items():
        line = [name.ljust(22)]
        for b in BUILDS:
            vals = [o[(b, r)] for o in rows.values() if (b, r) in o]
            line.append(f'{b}: {sum(v <= LIMIT for v in vals):5d} / {len(vals)}')
        # Frames both builds have a value for, to compare like with like.
        both = [o for o in rows.values() if all((b, r) in o for b in BUILDS)]
        gain = sum(o[(BUILDS[1], r)] <= LIMIT < o[(BUILDS[0], r)] for o in both)
        loss = sum(o[(BUILDS[0], r)] <= LIMIT < o[(BUILDS[1], r)] for o in both)
        line.append(f'newly within {gain}, no longer within {loss}')
        print('  '.join(line))
    any_b = {b: sum(any(o.get((b, r), 1e9) <= LIMIT for r in ('ff', 'wk')) for o in rows.values()) for b in BUILDS}
    print('within Firefox or WebKit:', ', '.join(f'{b} {n}' for b, n in any_b.items()))
    for a, c in (('ff', 'chr'), ('wk', 'chr'), ('wk', 'ff')):
        vals = [o[(a, c)] for o in rows.values() if (a, c) in o]
        print(f'{REFS[a]} vs {REFS[c]}: {sum(v <= LIMIT for v in vals)} / {len(vals)} within')
    per = collections.defaultdict(lambda: collections.Counter())
    for (k, f), o in rows.items():
        g = k.split('__')[1]
        for b in BUILDS:
            per[g][b] += any(o.get((b, r), 1e9) <= LIMIT for r in ('ff', 'wk'))
        per[g]['n'] += 1
    print('\nper group, within Firefox or WebKit:')
    for g in sorted(per):
        print(f'  {g:40} ' + '  '.join(f'{b} {per[g][b]:4d}' for b in BUILDS) + f'  of {per[g]["n"]}')


if __name__ == '__main__':
    main()
