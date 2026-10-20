#!/usr/bin/env python3
"""The morphology/offset PR's key set (morph_keys.json), before build vs after build (argv[1], argv[2];
default pyr, mo): every frame whose pixels change, with px>20, structural, max and the Chromium-Firefox
envelope; then the count of frames that stayed bit-identical."""
import json, collections, sys, os
R = os.path.dirname(os.path.abspath(__file__))
BEFORE, AFTER = (sys.argv[1], sys.argv[2]) if len(sys.argv) > 2 else ('pyr', 'mo')
rows = [json.loads(l) for l in open(f'{R}/accuracy.jsonl')]
keys = json.load(open(f'{R}/morph_keys.json'))
by = collections.defaultdict(dict)
for r in rows:
    if r['key'] in keys:
        by[(r['key'], r['framing'])][r['build']] = r
same = 0
print(f'| file | framing | px>20 {BEFORE} -> {AFTER} | structural | max | Chromium vs Firefox |')
print('|---|---|---:|---:|---:|---:|')
for key in keys:
    for fr in ['z1', 'z2', 'z4', 'hd']:
        v = by.get((key, fr), {})
        a, b = v.get(BEFORE), v.get(AFTER)
        if not a or not b or 'vs_chr' not in a or 'vs_chr' not in b:
            continue
        if a.get('hash') == b.get('hash'):
            same += 1
            continue
        env = b.get('chr_vs_ff', {}).get('px20', float('nan'))
        print(f"| {key.split('__')[-1][:44]} | {fr} | {a['vs_chr']['px20']:.2f} % -> {b['vs_chr']['px20']:.2f} % | {a['vs_chr']['struct']:.3f} % -> {b['vs_chr']['struct']:.3f} % | {a['vs_chr']['max']} -> {b['vs_chr']['max']} | {env:.2f} % |")
print(f'\nbit-identical frames in the key set: {same}')
