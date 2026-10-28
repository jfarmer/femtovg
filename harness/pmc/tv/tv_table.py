#!/usr/bin/env python3
"""tv_table.py TAG... : the moving frames (rep >= 1) of each run's soak CSV, per variant (the tag's last part: off,
pp = old rasterizer, pc = new) and per file and phase: median E-core cycles and instructions of the render thread a
frame, wall time, and the median of the frames' peak footprint and its graphics part. Runs of one variant are pooled."""
import collections, csv, statistics as st, sys

rows = collections.defaultdict(lambda: collections.defaultdict(list))
for tag in sys.argv[1:]:
    variant = tag.rsplit('-', 1)[1]
    for r in csv.DictReader(open(f'soak-{tag}.csv')):
        if int(r['rep']) < 1:
            continue
        key = (r['phase'], r['file'])
        rows[key][variant].append((int(r['e_cyc']), int(r['e_instr']), float(r['wall_ms']), int(r['peak_footprint']),
                                   int(r['peak_graphics'])))

variants = ['off', 'pp', 'pc']
names = {'off': 'masks off', 'pp': 'old raster', 'pc': 'new raster'}
total = collections.defaultdict(lambda: [0.0, 0.0])
for (phase, name), by in sorted(rows.items()):
    med = {v: [st.median(c) for c in zip(*by[v])] for v in variants if by.get(v)}
    if 'off' not in med:
        continue
    line = f'{phase:6s} {name[2:]:10s}'
    for v in variants:
        if v not in med:
            continue
        cyc, ins, wall, peak, gfx = med[v]
        total[v][0] += cyc
        total[v][1] += ins
        d = 100 * (cyc / med['off'][0] - 1)
        line += f' | {names[v]} {cyc / 1e6:6.2f} M cyc ({d:+4.0f} %) {wall:6.2f} ms {peak / 2**20:5.1f}/{gfx / 2**20:5.1f} MiB'
    print(line)
print('sum of the medians:', ' | '.join(f'{names[v]} {total[v][0] / 1e6:.1f} M cycles, {total[v][1] / 1e6:.1f} M instr'
                                       for v in variants if v in total))
