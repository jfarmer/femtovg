#!/usr/bin/env python3
"""Pyramid PR evidence from accuracy.jsonl and timing.jsonl: frames that change between the before and after
builds (argv[1], argv[2]; default base, bd), identity elsewhere, and cost (frame time, peak memory) by max device sigma."""
import json, collections, statistics, re, os, sys
BEFORE, AFTER = (sys.argv[1], sys.argv[2]) if len(sys.argv) > 2 else ('base', 'bd')
R = os.path.dirname(os.path.abspath(__file__))
files = {f['key']: f for f in json.load(open(f'{R}/files.json'))}
rows = [json.loads(l) for l in open(f'{R}/accuracy.jsonl')]
by = collections.defaultdict(dict)
for r in rows: by[(r['key'], r['framing'])][r['build']] = r
pairs = [(k, v) for k, v in by.items() if BEFORE in v and AFTER in v]
same = sum(1 for _, v in pairs if v[BEFORE].get('hash') == v[AFTER].get('hash') and 'hash' in v[BEFORE])
print(f'{BEFORE} -> {AFTER}: frames with both builds: {len(pairs)}; bit-identical: {same}')
changed = [(k, v) for k, v in pairs if 'vs_chr' in v[BEFORE] and 'vs_chr' in v[AFTER] and abs(v[BEFORE]['vs_chr']['px20'] - v[AFTER]['vs_chr']['px20']) > 0.1]
print('\n| file | framing | px>20 before -> after | structural before -> after | max | Chromium vs Firefox |')
print('|---|---|---:|---:|---:|---:|')
for k, v in sorted(changed, key=lambda kv: -(kv[1][BEFORE]['vs_chr']['px20'] - kv[1][AFTER]['vs_chr']['px20'])):
    b, a = v[BEFORE]['vs_chr'], v[AFTER]['vs_chr']
    env = v[AFTER].get('chr_vs_ff', {}).get('px20', float('nan'))
    print(f"| {k[0].split('__')[-1][:44]} | {k[1]} | {b['px20']:.2f} % -> {a['px20']:.2f} % | {b['struct']:.3f} % -> {a['struct']:.3f} % | {b['max']} -> {a['max']} | {env:.2f} % |")
# all blur-set frames that differ in hash but did not move beyond 0.1: how far did they move at all?
moved_small = [(k, v) for k, v in pairs if 'hash' in v[BEFORE] and v[BEFORE]['hash'] != v[AFTER].get('hash') and 'vs_chr' in v[BEFORE] and 'vs_chr' in v[AFTER] and abs(v[BEFORE]['vs_chr']['px20'] - v[AFTER]['vs_chr']['px20']) <= 0.1]
print(f'\nframes differing in pixels but within 0.1 points of px>20: {len(moved_small)}')
if moved_small:
    d = [v[AFTER]['vs_chr']['px20'] - v[BEFORE]['vs_chr']['px20'] for _, v in moved_small]
    d8 = [v[AFTER]['vs_chr']['px8'] - v[BEFORE]['vs_chr']['px8'] for _, v in moved_small]
    print(f'  px>20 delta median {statistics.median(d):+.3f} min {min(d):+.3f} max {max(d):+.3f}; px>8 delta median {statistics.median(d8):+.3f} min {min(d8):+.3f} max {max(d8):+.3f}')
# timing
if os.path.exists(f'{R}/timing.jsonl'):
    t = collections.defaultdict(dict)
    for r in map(json.loads, open(f'{R}/timing.jsonl')):
        if 'frame_ms' in r: t[(r['key'], r['framing'])][r['build']] = r
    print('\n## cost: one process per frame, frame time ms (record + flush + GPU wait) and peak footprint MiB, by the file\'s largest device sigma')
    print('| sigma band | frames | frame ms before median / max | after median / max | peak footprint MiB before median / max | after median / max |')
    print('|---|---:|---:|---:|---:|---:|')
    bands = [('sigma <= 8 (no pyramid)', lambda s: s <= 8), ('8 < sigma <= 32', lambda s: 8 < s <= 32), ('32 < sigma <= 128', lambda s: 32 < s <= 128), ('sigma > 128', lambda s: s > 128)]
    MiB = 1048576
    for name, sel in bands:
        xs = [v for v in t.values() if BEFORE in v and AFTER in v and sel(v[BEFORE]['max_sigma_px'])]
        if not xs: continue
        fb = [v[BEFORE]['frame_ms'] for v in xs]; fa = [v[AFTER]['frame_ms'] for v in xs]
        mb = [v[BEFORE]['peak_footprint'] / MiB for v in xs]; ma = [v[AFTER]['peak_footprint'] / MiB for v in xs]
        print(f'| {name} | {len(xs)} | {statistics.median(fb):.1f} / {max(fb):.1f} | {statistics.median(fa):.1f} / {max(fa):.1f} | {statistics.median(mb):.0f} / {max(mb):.0f} | {statistics.median(ma):.0f} / {max(ma):.0f} |')
    worst = sorted(((v[BEFORE]['frame_ms'], k, v) for k, v in t.items() if BEFORE in v and AFTER in v), reverse=True)[:8]
    print(f'\nslowest {BEFORE} frames: file framing sigma_px frame ms base -> bd, footprint MiB base -> bd')
    for ms, k, v in worst:
        print(f"  {k[0].split('__')[-1][:40]:40s} {k[1]} sigma {v[BEFORE]['max_sigma_px']:6.1f}  {ms:7.1f} -> {v[AFTER]['frame_ms']:7.1f} ms   {v[BEFORE]['peak_footprint']/MiB:5.0f} -> {v[AFTER]['peak_footprint']/MiB:5.0f} MiB")
