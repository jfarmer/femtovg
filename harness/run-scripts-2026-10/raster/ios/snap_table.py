#!/usr/bin/env python3
"""snap_table.py DIR...: the snapping rounds (DIR/soak-r<N>-<i>-<off|exact|s4|s8>.csv), moving frames (rep >= MINREP, default 1): per
variant the sums over files and phases of the median render-thread efficiency-core cycles and instructions, process
energy, and the median peak footprint; the masks' cost against the masks off, and the files where it is largest."""
import collections, csv, glob, os, statistics as st, sys
MINREP = int(os.environ.get('MINREP', 1))  # the first moving frame counted; MINREP=50 skips a long run's warm-up
COLS = ['e_cyc', 'e_instr', 'task_energy_nj', 'peak_footprint']
for d in sys.argv[1:]:
    rows = collections.defaultdict(lambda: collections.defaultdict(list))
    for path in glob.glob(f'{d}/soak-r*.csv'):
        v = path.rsplit('-', 1)[1][:-4]
        for r in csv.DictReader(open(path)):
            if int(r['rep']) >= MINREP:
                rows[(r['phase'], r['file'])][v].append([float(r[c]) for c in COLS])
    med = {k: {v: [st.median(c) for c in zip(*x)] for v, x in by.items()} for k, by in rows.items()}
    tot = collections.defaultdict(lambda: [0.0] * 4)
    for k, m in med.items():
        for v, x in m.items():
            for i in range(3):
                tot[v][i] += x[i]
            tot[v][3] = max(tot[v][3], x[3])
    print(f'{d}: sums of the moving frames\' medians over {len(med)} file x phase')
    for v in ('off', 'exact', 's4', 's8', 's16'):
        if v in tot:
            c, i, e, p = tot[v]
            rel = '' if v == 'off' else f'  vs off: cycles {100 * (c / tot["off"][0] - 1):+5.1f} %, instructions {100 * (i / tot["off"][1] - 1):+5.1f} %, energy {100 * (e / tot["off"][2] - 1):+5.1f} %'
            print(f'  {v:5s} E cycles {c / 1e6:7.1f} M  instr {i / 1e6:7.1f} M  energy {e / 1e6:5.2f} mJ  peak {p / 2**20:6.1f} MiB{rel}')
    print('  largest costs (cycles vs off): ' + ', '.join(
        f"{k[0]}/{k[1][2:]} exact {100 * (m['exact'][0] / m['off'][0] - 1):+.0f} % s4 {100 * (m['s4'][0] / m['off'][0] - 1):+.0f} % s8 {100 * (m['s8'][0] / m['off'][0] - 1):+.0f} %"
        for k, m in sorted(med.items(), key=lambda km: -(km[1]['exact'][0] / km[1]['off'][0]))[:4] if all(v in m for v in ('off', 'exact', 's4', 's8'))))
