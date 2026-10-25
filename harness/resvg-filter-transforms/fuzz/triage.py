#!/usr/bin/env python3
"""Triage of run.py results: outcomes per build, the cases where the patched build ('both') is worse than 0.49
('base') or better, and the outsized cases grouped by the filter primitives they contain.

  triage.py DIR [cpu=1.0] [rss=256]
"""
import collections, json, re, sys

d = sys.argv[1]
opts = dict(a.split('=', 1) for a in sys.argv[2:])
CPU, RSS = float(opts.get('cpu', 1.0)), float(opts.get('rss', 256))
res = collections.defaultdict(dict)
for l in open(f'{d}/results.jsonl'):
    r = json.loads(l)
    res[r['case']][r['build']] = r


def outcome(r):
    if r['rc'] in ('mem', 'timeout'):
        return r['rc']
    if r['panic']:
        return 'panic ' + re.sub(r".*panicked at .*?src/", '', r['msg'])[:60]
    if r['rc'] != 0:
        return f'rc {r["rc"]} ' + r['msg'][:40]
    if r['cpu'] > CPU or (r['rss_mb'] or 0) > RSS:
        return 'outsized'
    return 'ok'


def bad(r):
    return outcome(r) != 'ok'


for b in ('base', 'both'):
    c = collections.Counter(outcome(v[b]) for v in res.values() if b in v)
    print(b, dict(c.most_common()))

worse, better = [], []
for case, v in sorted(res.items()):
    if 'base' not in v or 'both' not in v:
        continue
    a, b = v['base'], v['both']
    wa, wb = bad(a), bad(b)
    heavier = (b['cpu'] > max(2 * a['cpu'], a['cpu'] + 0.5)) or ((b['rss_mb'] or 0) > max(2 * (a['rss_mb'] or 0), (a['rss_mb'] or 0) + 100))
    if (wb and not wa) or (wb and wa and outcome(a) != outcome(b) and outcome(b) in ('mem', 'timeout') and outcome(a) == 'outsized') or (heavier and wb):
        worse.append((case, outcome(a), a['cpu'], a['rss_mb'], outcome(b), b['cpu'], b['rss_mb']))
    elif wa and not wb:
        better.append((case, outcome(a), a['cpu'], a['rss_mb'], outcome(b), b['cpu'], b['rss_mb']))
print(f'\npatched worse: {len(worse)}')
for w in worse[:40]:
    print('  ', w)
print(f'patched better: {len(better)}')
for w in better[:15]:
    print('  ', w)

# Which primitives the outsized cases hold (either build), against their share of all cases.
prims = collections.Counter()
hit = collections.Counter()
for case, v in res.items():
    src = open(f'{d}/{case}').read()
    kinds = set(re.findall(r'<(fe[A-Z][A-Za-z]+)', src)) | ({'nearskew'} if re.search(r'skew[XY]\(-?(89\.9|90)', src) else set())
    for k in kinds:
        prims[k] += 1
    if any(bad(r) and outcome(r) != 'ok' for r in v.values()):
        for k in kinds:
            hit[k] += 1
print('\nprimitive: share of bad cases holding it (bad / all holding it)')
for k, n in sorted(prims.items(), key=lambda kv: -hit[kv[0]] / kv[1]):
    print(f'  {k:22} {hit[k]:4} / {n:4}  {hit[k] / n * 100:5.1f} %')
