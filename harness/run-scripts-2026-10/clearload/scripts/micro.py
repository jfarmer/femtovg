#!/usr/bin/env python3
"""micro.py DEV : the microbenchmark ABBA (tags m-N-pp / m-N-pc) per frame file: each variant's median steady
frame (all passes, both legs) for GPU time, reads, writes, and post-encode time from the soak CSV."""
import csv, glob, json, os, statistics as st, sys
from collections import defaultdict

dev = sys.argv[1]
d = f'{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}/{dev}'
vals = defaultdict(lambda: defaultdict(list))
for path in sorted(glob.glob(f'{d}/frames-m-*.jsonl')):
    v = path.rsplit('-', 1)[1].split('.')[0]
    for line in open(path):
        r = json.loads(line)
        if r['rep'] >= 1 and r.get('gpu_ms') is not None:
            for m in ('gpu_ms', 'read_mb', 'write_mb'):
                if r.get(m) is not None:
                    vals[(r['phase'], r['file'])][f'{v}:{m}'].append(r[m])
for path in sorted(glob.glob(f'{d}/soak-m-*.csv')):
    v = path.rsplit('-', 1)[1].split('.')[0]
    for r in csv.DictReader(open(path)):
        if int(r['rep']) >= 1:
            vals[(r['phase'], r['file'])][f'{v}:post_ms'].append(float(r['wall_ms']) - float(r['encode_ms']))
for (phase, name), per in sorted(vals.items()):
    cells = []
    for m in ('gpu_ms', 'read_mb', 'write_mb', 'post_ms'):
        a, b = per.get(f'pp:{m}'), per.get(f'pc:{m}')
        if a and b:
            ma, mb = st.median(a), st.median(b)
            cells.append(f'{m} {ma:7.3f} -> {mb:7.3f} ({(mb - ma) / ma * 100:+.0f} %)')
    print(f'{dev} {phase:7s} {name:10s} ' + ' | '.join(cells))
