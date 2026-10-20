#!/usr/bin/env python3
"""report.py BASE HEAD [threshold=0.15]: the 390 pairs of the extracted reftest suite (groups 01-22) on two builds.
For each pair and framing: the test frame's pixels beyond 20/255 of Chromium's frame of the same file (accuracy.jsonl),
the self-reftest - femtovg's test frame against femtovg's reference frame (png/) - and Chromium's own test frame against
its reference frame. A pair fails a build when its worst framing exceeds THRESHOLD % in the self-reftest. Prints the
counts per group, every pair whose self-reftest moved between the builds by more than the threshold, and the pairs
the head still fails, with Chromium's self-reftest beside them (a reference Chromium itself does not match is the
suite's, not femtovg's)."""
import collections, json, os, sys
import numpy as np
from PIL import Image

R = os.path.dirname(os.path.abspath(__file__))
SUITE = '/Users/matt/.gemini/antigravity/scratch/wpt_svg_reftests'
base, head = sys.argv[1:3]
opts = dict(a.split('=', 1) for a in sys.argv[3:])
THRESHOLD = float(opts.get('threshold', 0.15))
FRAMINGS = ['z1', 'z2', 'z4', 'hd']
manifest = json.load(open(f'{SUITE}/test-manifest.json'))['tests']
key = lambda path: f"wpt22__{path.split('/')[0]}__{os.path.basename(path)[:-4]}"
acc = {}
for line in open(f'{R}/accuracy.jsonl'):
    r = json.loads(line)
    if 'vs_chr' in r:
        acc[(r['key'], r['framing'], r['build'])] = r['vs_chr']['px20']


def load(path):
    return np.asarray(Image.open(path).convert('RGB'), dtype=np.int16) if os.path.exists(path) else None


def px20(a, b):
    if a is None or b is None:
        return None
    h, w = min(a.shape[0], b.shape[0]), min(a.shape[1], b.shape[1])
    return 100.0 * (np.abs(a[:h, :w] - b[:h, :w]).max(axis=2) > 20).mean()


rows = []
for t in manifest:
    tk, rk = key(t['test_file']), key(t['ref_file'])
    row = {'id': t['id'], 'group': t['category'], 'self': {}, 'vs_chr': {}, 'chr_self': None}
    chr_self = []
    for build in (base, head):
        worst = []
        for fr in FRAMINGS:
            worst.append((px20(load(f'{R}/png/{build}_{tk}_{fr}.png'), load(f'{R}/png/{build}_{rk}_{fr}.png')) or 0.0, fr))
        row['self'][build] = max(worst)
        row['vs_chr'][build] = max((acc.get((tk, fr, build)) or 0.0, fr) for fr in FRAMINGS)
    for fr in FRAMINGS:
        v = px20(load(f'{R}/refs/chr_{tk}_{fr}.png'), load(f'{R}/refs/chr_{rk}_{fr}.png'))
        if v is not None:
            chr_self.append(v)
    row['chr_self'] = max(chr_self) if chr_self else None
    rows.append(row)
json.dump(rows, open(f'{R}/report_{base}_{head}.json', 'w'), indent=1)

fails = lambda r, b: r['self'][b][0] > THRESHOLD
by_group = collections.defaultdict(lambda: [0, 0, 0])
for r in rows:
    g = by_group[r['group']]
    g[0] += 1; g[1] += fails(r, base); g[2] += fails(r, head)
print(f'self-reftest failures (worst framing > {THRESHOLD} % px>20), {base} -> {head}:')
for g, (n, a, b) in sorted(by_group.items()):
    print(f'  {g:44s} {n:3d} pairs: {a:3d} -> {b:3d}')
print(f'  {"all":44s} {sum(v[0] for v in by_group.values()):3d} pairs: {sum(v[1] for v in by_group.values()):3d} -> {sum(v[2] for v in by_group.values()):3d}')
fmt = lambda v: '-' if v is None else f'{v:.2f}'
moved = [r for r in rows if abs(r['self'][head][0] - r['self'][base][0]) > THRESHOLD]
print(f'\npairs whose self-reftest moved by more than {THRESHOLD} %: {len(moved)}')
print(f'| pair | group | {base} | {head} | vs Chromium {base} | vs Chromium {head} | Chromium self |')
print('|---|---|---:|---:|---:|---:|---:|')
for r in sorted(moved, key=lambda r: r['self'][head][0] - r['self'][base][0]):
    print(f"| {r['id'][:46]} | {r['group'][:2]} | {fmt(r['self'][base][0])} ({r['self'][base][1]}) | {fmt(r['self'][head][0])} ({r['self'][head][1]}) "
          f"| {fmt(r['vs_chr'][base][0])} | {fmt(r['vs_chr'][head][0])} | {fmt(r['chr_self'])} |")
still = [r for r in rows if fails(r, head)]
print(f'\npairs {head} fails: {len(still)}, of which Chromium fails its own reference too (> {THRESHOLD} %): '
      f'{sum(1 for r in still if (r["chr_self"] or 0) > THRESHOLD)}')
print(f'| pair | group | self ({head}) | vs Chromium | Chromium self |')
print('|---|---|---:|---:|---:|')
for r in sorted(still, key=lambda r: (r['group'], -r['self'][head][0])):
    print(f"| {r['id'][:46]} | {r['group'][:2]} | {fmt(r['self'][head][0])} ({r['self'][head][1]}) | {fmt(r['vs_chr'][head][0])} | {fmt(r['chr_self'])} |")
