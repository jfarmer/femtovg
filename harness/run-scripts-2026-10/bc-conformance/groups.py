#!/usr/bin/env python3
"""Per-group distance from the area reference (refs/id_*) for master (m7), A (m7f), B (fb), C (fc) and the browsers,
and BuseyBench against software Chromium from accuracy.jsonl.

  groups.py [check]   (check: verify the eval.jsonl 'm'/'p' rows against kept m7/m7f frames first)

m7 and m7f per-frame counts come from tmp/flat/eval.jsonl (variants m and p, bit-identical to m7 and m7f); fb and fc
take the m7 counts where their frame hash equals m7's, else are measured from the kept frame. Writes
bc-conformance/groups_rows.jsonl (one row per frame) and prints markdown tables."""
import collections, json, os, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.expanduser('~/src/femtovg-wt/da/harness/corpus_run'))
from common import OUT, REFS, files

HERE = os.path.dirname(os.path.abspath(__file__))
fs = {f['key']: f['group'] for f in files()}
rec = {}
for line in open(f'{OUT}/accuracy.jsonl'):
    try:
        r = json.loads(line)
    except Exception:
        continue
    if r['build'] in ('m7', 'm7f', 'fb', 'fc'):
        rec[(r['build'], r['key'], r['framing'])] = r
ev = {}
for line in open(f'{OUT}/tmp/flat/eval.jsonl'):
    r = json.loads(line)
    if r['variant'] in ('m', 'p'):
        ev[({'m': 'm7', 'p': 'm7f'}[r['variant']], r['key'], r['framing'])] = (r['far20'], r['far8'])


def load(p):
    return np.asarray(Image.open(p).convert('RGB'), dtype=np.int16) if os.path.exists(p) else None


def frame(build, key, framing):
    for d in ('png_wpt', 'png_nyt', 'png', 'png_changed'):
        a = load(f'{OUT}/{d}/{build}_{key}_{framing}.png')
        if a is not None:
            return a
    return None


def far(a, r):
    d = np.abs(a - r).max(axis=2)
    return int((d > 20).sum()), int((d > 8).sum())


frames = sorted(n[3:-4].rsplit('_', 1) for n in os.listdir(REFS) if n.startswith('id_') and n.endswith('.png'))
if len(sys.argv) > 1 and sys.argv[1] == 'check':
    bad = n = 0
    for key, framing in frames:
        for b in ('m7', 'm7f'):
            a = frame(b, key, framing)
            if a is None or (b, key, framing) not in ev:
                continue
            r = load(f'{REFS}/id_{key}_{framing}.png')
            n += 1
            if far(a, r) != ev[(b, key, framing)]:
                bad += 1
                print('mismatch', b, key, framing, far(a, r), ev[(b, key, framing)])
    print(f'checked {n} kept frames against eval.jsonl, {bad} mismatches')
    sys.exit()

rows = []
for key, framing in frames:
    if key not in fs:
        continue
    area = load(f'{REFS}/id_{key}_{framing}.png')
    row = {'key': key, 'framing': framing, 'group': fs[key], 'size': int(area.shape[0] * area.shape[1])}
    for b in ('m7', 'm7f'):
        a = frame(b, key, framing)  # a kept frame where there is one, else the bit-identical eval.jsonl variant
        row[b] = far(a, area) if a is not None and a.shape == area.shape else ev.get((b, key, framing))
    for b in ('fb', 'fc'):
        h, h0 = rec.get((b, key, framing), {}).get('hash'), rec.get(('m7', key, framing), {}).get('hash')
        if h and h == h0:
            row[b] = row['m7']
        else:
            a = frame(b, key, framing)
            row[b] = far(a, area) if a is not None and a.shape == area.shape else None
    for ref in ('chr', 'chg', 'ff', 'wk'):
        a = load(f'{REFS}/{ref}_{key}_{framing}.png')
        row[ref] = far(a, area) if a is not None and a.shape == area.shape else None
    rows.append(row)
with open(f'{HERE}/groups_rows.jsonl', 'w') as out:
    for r in rows:
        out.write(json.dumps(r) + '\n')

who = ['m7', 'm7f', 'fb', 'fc', 'chg', 'chr', 'ff', 'wk']
label = {'m7': 'master', 'm7f': 'A', 'fb': 'B', 'fc': 'C', 'chg': 'Chr GPU', 'chr': 'Chr sw', 'ff': 'Firefox', 'wk': 'WebKit'}
order = ['svgenius', 'firefox', 'firefox-com', 'buseybench', 'tiger', 'icons', 'nyt', 'wpt', 'wpt-clip-path-reftests',
         'wpt-other', 'other']


def bucket(g):
    if g in order:
        return g
    if g.startswith('wpt-'):
        return 'wpt-other'
    return 'other'


for i, name in ((0, 'beyond 20/255'), (1, 'beyond 8/255')):
    print(f'\nPixels {name} of the area reference, frames where every renderer has a frame (Chr GPU/WebKit as available)')
    print('| group | frames | ' + ' | '.join(label[w] for w in who) + ' |')
    print('|---|---:|' + '---:|' * len(who))
    tot = collections.Counter(); totn = 0
    for g in order + ['all']:
        sel = [r for r in rows if (g == 'all' or bucket(r['group']) == g) and all(r[w] is not None for w in who[:4])]
        if not sel:
            continue
        cells = []
        for w in who:
            have = [r for r in sel if r[w] is not None]
            s = sum(r[w][i] for r in have)
            cells.append(f'{s:,}' + ('' if len(have) == len(sel) else f' ({len(have)})'))
        print(f'| {g} | {len(sel)} | ' + ' | '.join(cells) + ' |')

# BuseyBench against software Chromium (accuracy.jsonl), every framing
print('\nBuseyBench vs Chromium software (accuracy.jsonl vs_chr), 27 files x 4 framings')
print('| build | frames | px beyond 20/255 | px beyond 8/255 | exact mismatch px | sum of per-frame max | worst frame max | frames identical to master |')
print('|---|---:|---:|---:|---:|---:|---:|---:|')
for b in ('m7', 'm7f', 'fb', 'fc'):
    sel = [r for (bb, k, f), r in rec.items() if bb == b and r['group'] == 'buseybench' and 'vs_chr' in r]
    size = lambda r: (1920 * 1080) if r['framing'] == 'hd' else (460 * 260)
    p20 = sum(round(r['vs_chr']['px20'] / 100 * size(r)) for r in sel)
    p8 = sum(round(r['vs_chr']['px8'] / 100 * size(r)) for r in sel)
    ex = sum(r['vs_chr']['exact'] for r in sel)
    mx = sum(r['vs_chr']['max'] for r in sel)
    wm = max(r['vs_chr']['max'] for r in sel)
    same = sum(r.get('hash') == rec.get(('m7', r['key'], r['framing']), {}).get('hash') for r in sel)
    print(f'| {label[b]} | {len(sel)} | {p20:,} | {p8:,} | {ex:,} | {mx:,} | {wm} | {same} |')
