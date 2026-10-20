#!/usr/bin/env python3
"""legs.py DEV PREFIX : per ABBA leg and phase, the median steady frame's GPU time, fragment time, reads and
writes, so drift between legs of the same variant shows next to the difference between variants."""
import glob, json, os, statistics as st, sys
from collections import defaultdict

dev, prefix = sys.argv[1], sys.argv[2]
d = f'{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}/{dev}'
for path in sorted(glob.glob(f'{d}/frames-{prefix}-*.jsonl')):
    leg = os.path.basename(path)[len('frames-'):-len('.jsonl')]
    by = defaultdict(list)
    for line in open(path):
        r = json.loads(line)
        if r['rep'] >= 1 and r['gpu_ms'] is not None:
            by[r['phase']].append(r)
    cells = []
    for phase in ('curve', 'curvehd', 'busey', 'buseyhd', 'empty', 'emptyhd'):
        rows = by.get(phase)
        if not rows:
            continue
        cell = f'{phase} gpu {st.median(r["gpu_ms"] for r in rows):6.2f}'
        if 'read_mb' in rows[0]:
            cell += f' rd {st.median(r["read_mb"] for r in rows):5.2f} wr {st.median(r["write_mb"] for r in rows):5.2f}'
        cells.append(cell)
    print(f'{dev} {leg:9s} ' + ' | '.join(cells))
