#!/usr/bin/env python3
"""ios_table.py TAG... : the moving frames (rep >= 1) of each run's soak CSV, per variant (the tag's last part) and per
file and phase: median render-thread efficiency-core cycles and instructions a frame, the process's cycles and energy,
and the median of the frames' peak footprint and its graphics part. Runs of one variant are pooled. Variants: pp = #408,
a = + frame-setup belt, pc = + image staging; off<v> = that build with NO_THIN_FILL_MASKS=1."""
import collections, csv, statistics as st, sys

COLS = ['e_cyc', 'e_instr', 'task_cyc', 'task_energy_nj', 'wall_ms', 'peak_footprint', 'peak_graphics']
rows = collections.defaultdict(lambda: collections.defaultdict(list))
for tag in sys.argv[1:]:
    variant = tag.rsplit('-', 1)[1]
    for r in csv.DictReader(open(f'soak-{tag}.csv')):
        if int(r['rep']) < 1:
            continue
        rows[(r['phase'], r['file'])][variant].append([float(r[c]) for c in COLS])

builds = [('pp', '#408'), ('a', '+ belt'), ('pc', '+ image staging')]
present = {v for by in rows.values() for v in by}
med = {key: {v: [st.median(c) for c in zip(*by[v])] for v in by} for key, by in rows.items()}
total = collections.defaultdict(lambda: [0.0] * len(COLS))
for key in sorted(med):
    for v, m in med[key].items():
        for i, x in enumerate(m):
            total[v][i] += x

def pct(a, b):
    return 100 * (a / b - 1) if b else float('nan')

print('Render thread E-core cycles a moving frame, median (masks on vs the same build off | vs offpc):')
for (phase, name), m in sorted(med.items()):
    line = f'{phase:6s} {name[2:]:10s}'
    for v, label in builds:
        if v in m and 'off' + v in m:
            line += f' | {label} {m[v][0] / 1e6:6.2f} M ({pct(m[v][0], m["off" + v][0]):+4.0f} %'
            line += f', {pct(m[v][0], m["offpc"][0]):+4.0f} %)' if 'offpc' in m else ')'
    print(line)
print()
names = {'offpp': '#408 off', 'pp': '#408', 'offa': '+ belt off', 'a': '+ belt', 'offpc': '+ staging off', 'pc': '+ staging'}
for v in ['offpp', 'pp', 'offa', 'a', 'offpc', 'pc']:
    if v not in total:
        continue
    t = total[v]
    base = total.get('offpc')
    rel = f'  vs offpc: cyc {pct(t[0], base[0]):+5.1f} % instr {pct(t[1], base[1]):+5.1f} % task {pct(t[2], base[2]):+5.1f} % energy {pct(t[3], base[3]):+5.1f} %' if base else ''
    print(f'{names[v]:14s} sum of medians: E cyc {t[0] / 1e6:7.1f} M  E instr {t[1] / 1e6:7.1f} M  process cyc {t[2] / 1e6:7.1f} M  '
          f'energy {t[3] / 1e6:6.1f} mJ{rel}')
print()
for v, label in builds:
    if v in total and 'off' + v in total:
        on, off = total[v], total['off' + v]
        print(f'{label:16s} masks on vs off: E cyc {pct(on[0], off[0]):+5.1f} %  E instr {pct(on[1], off[1]):+5.1f} %  '
              f'process cyc {pct(on[2], off[2]):+5.1f} %  energy {pct(on[3], off[3]):+5.1f} %')
print()
print('Peak footprint / graphics part, median over the moving frames, MiB:')
for (phase, name), m in sorted(med.items()):
    print(f'{phase:6s} {name[2:]:10s} ' + '  '.join(f'{names[v]} {m[v][5] / 2**20:5.1f}/{m[v][6] / 2**20:5.1f}'
                                                   for v in ['offpp', 'pp', 'offa', 'a', 'offpc', 'pc'] if v in m))
