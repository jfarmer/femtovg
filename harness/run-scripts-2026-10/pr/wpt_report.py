#!/usr/bin/env python3
"""The extracted WPT reftest suite on the PR stack: for every test/ref pair of the manifest, the test
file's px>20 against Chromium on each build (base, ab, pyr, mo) at its worst framing, the reference
file's own px>20 against Chromium, the self-reftest (femtovg's test frame vs femtovg's ref frame, from
png_wpt/ where present) and the browser's self-reftest (Chromium test vs Chromium ref), then the pairs
whose worst framing on the stack head exceeds THRESHOLD, grouped by category.
  wpt_report.py [threshold=0.15] [build=mo]"""
import json, os, sys, collections
import numpy as np
from PIL import Image
R = os.path.dirname(os.path.abspath(__file__))
SUITE = '/Users/matt/.gemini/antigravity/scratch/wpt_svg_reftests'
args = dict(a.split('=', 1) for a in sys.argv[1:])
THRESHOLD = float(args.get('threshold', '0.15'))
HEAD = args.get('build', 'mo')
BUILDS = [b for b in ['base', 'ab', 'pyr', 'mo'] if b != HEAD] + [HEAD]
FRAMINGS = ['z1', 'z2', 'z4', 'hd']
manifest = json.load(open(f'{SUITE}/test-manifest.json'))
files = {f['key']: f for f in json.load(open(f'{R}/files.json'))}
by_base = collections.defaultdict(list)
for k in files:
    by_base[k.split('__')[-1]].append(k)
rows = collections.defaultdict(dict)
for line in open(f'{R}/accuracy.jsonl'):
    r = json.loads(line)
    rows[(r['key'], r['framing'])][r['build']] = r


def key_of(path):
    base = os.path.basename(path)[:-4]
    hits = by_base.get(base, [])
    return hits[0] if len(hits) == 1 else None


def px20(key, fr, build):
    r = rows.get((key, fr), {}).get(build)
    return r['vs_chr']['px20'] if r and 'vs_chr' in r else None


def diff20(a, b):
    if not (os.path.exists(a) and os.path.exists(b)):
        return None
    x = np.asarray(Image.open(a).convert('RGB'), dtype=np.int16)
    y = np.asarray(Image.open(b).convert('RGB'), dtype=np.int16)
    h, w = min(x.shape[0], y.shape[0]), min(x.shape[1], y.shape[1])
    d = np.abs(x[:h, :w] - y[:h, :w]).max(axis=2)
    return 100.0 * (d > 20).mean()


report = []
for t in manifest['tests']:
    tk, rk = key_of(t['test_file']), key_of(t['ref_file'])
    if tk is None or rk is None:
        report.append({'id': t['id'], 'category': t.get('category', ''), 'missing': True})
        continue
    worst_fr, worst = None, -1.0
    per_build = {}
    for fr in FRAMINGS:
        v = px20(tk, fr, HEAD)
        if v is not None and v > worst:
            worst, worst_fr = v, fr
    for b in BUILDS:
        per_build[b] = px20(tk, worst_fr, b) if worst_fr else None
    ref_vs_chr = px20(rk, worst_fr, HEAD) if worst_fr else None
    self_ref = diff20(f'{R}/png_wpt/{HEAD}_{tk}_{worst_fr}.png', f'{R}/png_wpt/{HEAD}_{rk}_{worst_fr}.png') if worst_fr else None
    browser_self = diff20(f'{R}/refs/chr_{tk}_{worst_fr}.png', f'{R}/refs/chr_{rk}_{worst_fr}.png') if worst_fr else None
    report.append({'id': t['id'], 'category': t.get('category', ''), 'test': tk, 'ref': rk, 'framing': worst_fr, 'worst': worst,
                   'builds': per_build, 'ref_vs_chr': ref_vs_chr, 'self_ref': self_ref, 'browser_self': browser_self,
                   'description': t.get('description', ''), 'features': t.get('femtovg_features', []), 'bugs': t.get('bug_trackers', [])})
json.dump(report, open(f'{R}/wpt_report.json', 'w'), indent=1)
have = [r for r in report if not r.get('missing') and r['framing']]
print(f'{len(have)} pairs measured of {len(manifest["tests"])}; threshold {THRESHOLD} % px>20 on {HEAD}')
bad = [r for r in have if r['worst'] > THRESHOLD]
print(f'{len(bad)} pairs above threshold\n')
for cat, group in sorted(collections.defaultdict(list, {c: [r for r in bad if r['category'] == c] for c in {r['category'] for r in bad}}).items()):
    print(f'## {cat} ({len(group)})')
    print('| test | framing | ' + ' | '.join(BUILDS) + ' | ref vs Chromium | self reftest | Chromium self |')
    print('|---|---|' + '---:|' * (len(BUILDS) + 3))
    for r in sorted(group, key=lambda r: -r['worst']):
        fmt = lambda v: '-' if v is None else f'{v:.2f}'
        print(f"| {r['test'].split('__')[-1][:48]} | {r['framing']} | " + ' | '.join(fmt(r['builds'][b]) for b in BUILDS) + f" | {fmt(r['ref_vs_chr'])} | {fmt(r['self_ref'])} | {fmt(r['browser_self'])} |")
    print()
