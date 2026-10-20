#!/usr/bin/env python3
"""motion_table.py DIR... [minrep=50]: per variant (off, exact, s4, s8, s16) the sums over files and phases of the
medians of the moving frames (rep >= minrep) - render-thread efficiency-core cycles and instructions, wall time a
frame - and the largest peak footprint and graphics footprint over the runs; each against the masks off."""
import collections, csv, glob, statistics as st, sys
dirs = [a for a in sys.argv[1:] if '=' not in a]
opts = dict(a.split('=', 1) for a in sys.argv[1:] if '=' in a)
MINREP = int(opts.get('minrep', 50))
for d in dirs:
    med = collections.defaultdict(lambda: collections.defaultdict(list))
    peak = collections.defaultdict(lambda: [0.0, 0.0])
    for path in glob.glob(f'{d}/soak-r*.csv'):
        v = path.rsplit('-', 1)[1][:-4]
        n = 0
        for r in csv.DictReader(open(path)):
            n += 1
            peak[v][0] = max(peak[v][0], float(r['peak_footprint']) / 2**20)
            peak[v][1] = max(peak[v][1], float(r['peak_graphics']) / 2**20)
            if int(r['rep']) >= MINREP:
                med[(r['phase'], r['file'])][v].append((float(r['e_cyc']), float(r['e_instr']), float(r['wall_ms'])))
    keys = [k for k in med if 'off' in med[k]]
    tot = {}
    for v in opts.get('variants', 'off,exact,s4,s8,s16').split(','):
        if all(v in med[k] for k in keys) and keys:
            tot[v] = [sum(st.median(x[i] for x in med[k][v]) for k in keys) for i in range(3)]
    print(f'{d}: sums of medians over {len(keys)} file x phase, frames {MINREP}+ of each pan')
    for v, (c, i, w) in tot.items():
        o = tot['off']
        rel = '' if v == 'off' else f'  vs off: cycles {100 * (c / o[0] - 1):+5.1f} %, instr {100 * (i / o[1] - 1):+5.1f} %, wall {100 * (w / o[2] - 1):+5.1f} %'
        print(f'  {v:5s} cycles {c / 1e6:6.1f} M  instr {i / 1e6:6.1f} M  wall {w:6.1f} ms  peak {peak[v][0]:6.1f} MiB (graphics {peak[v][1]:5.1f}){rel}')
