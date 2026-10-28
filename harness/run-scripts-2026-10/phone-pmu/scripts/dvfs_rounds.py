#!/usr/bin/env python3
"""Run-to-run spread of the fixed-clock comparison: dvfs.py's estimate computed for
each plain round k separately (runs <v>-p<k> of all variants; keys every variant
has in the clock bin in that round), and the per-round deltas vs master.
usage: dvfs_rounds.py <runs> <dev> lo:hi"""
import csv, glob, os, re, statistics, sys, collections
RUNS, DEV = sys.argv[1], sys.argv[2]
lo, hi = map(float, sys.argv[3].split(":"))
VARS = ["m", "a", "b", "c", "pp", "pc"]
per = collections.defaultdict(dict)
for f in glob.glob(os.path.join(RUNS, DEV, "plain", "soak-*-p*.csv")):
    m = re.search(r"soak-(m|a|b|c|pp|pc)-p(\d+)\.csv$", f)
    v, k = m.group(1), int(m.group(2))
    by = collections.defaultdict(list)
    for r in csv.DictReader(open(f)):
        if r["pass"] == "0" or r["rep"] == "0" or int(r["p_cyc"]) or float(r["encode_ms"]) < 0.5 or r["phase"] not in ("curve", "curvehd"):
            continue
        g = int(r["enc_e_cyc"]) / float(r["encode_ms"]) / 1e6
        if lo <= g < hi:
            by[(r["phase"], r["file"], r["zoom"])].append(r)
    per[k][v] = {key: (statistics.median(int(r["e_cyc"]) for r in rs), statistics.median(int(r["e_instr"]) for r in rs)) for key, rs in by.items()}
print(f"{DEV} clock {lo}-{hi} GHz, curve + curvehd, per round: cycles (instr) vs master, keys")
res = collections.defaultdict(list)
for k in sorted(per):
    if len(per[k]) < len(VARS):
        continue
    keys = set.intersection(*[set(per[k][v]) for v in VARS])
    if len(keys) < 30:
        print(f"round {k}: only {len(keys)} common keys"); continue
    mC = sum(per[k]["m"][x][0] for x in keys); mI = sum(per[k]["m"][x][1] for x in keys)
    cells = []
    for v in VARS[1:]:
        C = sum(per[k][v][x][0] for x in keys); I = sum(per[k][v][x][1] for x in keys)
        res[v].append((C / mC - 1) * 100)
        cells.append(f"{v} {(C/mC-1)*100:+.1f} ({(I/mI-1)*100:+.1f})")
    print(f"round {k} [{len(keys)} keys]: " + "  ".join(cells))
for v, xs in res.items():
    print(f"  {v}: cycles vs master mean {statistics.mean(xs):+.1f} %, range {min(xs):+.1f}..{max(xs):+.1f} over {len(xs)} rounds")
