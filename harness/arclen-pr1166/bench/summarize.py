#!/usr/bin/env python3
"""usage: summarize.py out.csv [more.csv ...]  -> median per-call instructions/cycles/IPC per workload x variant, E-core."""
import csv, sys, statistics as st, collections
rows = collections.defaultdict(list)
for p in sys.argv[1:]:
    for r in csv.DictReader(open(p)):
        n = int(r["inner"]); ie, ce, ip, cp = (int(r[k]) for k in ("instr_e", "cyc_e", "instr_p", "cyc_p"))
        rows[(r["workload"], r["variant"])].append((ie / n, ce / n, ip / n, cp / n))
order = []
for (w, v) in rows:
    if w not in order: order.append(w)
vs = []
for (w, v) in rows:
    if v not in vs: vs.append(v)
base = "plain0.001"
print(f"{'workload':14} {'variant':12} {'instr/call':>12} {'cyc/call':>12} {'IPC':>5} {'P-core%':>7} {'vs '+base+' instr':>18} {'cyc':>7}  cyc spread")
for w in order:
    b = rows.get((w, base))
    bi = st.median(x[0] for x in b) if b else None
    bc = st.median(x[1] for x in b) if b else None
    for v in vs:
        r = rows.get((w, v))
        if not r: continue
        i = st.median(x[0] for x in r); c = st.median(x[1] for x in r)
        pi = st.median(x[2] for x in r)
        cs = sorted(x[1] for x in r)
        print(f"{w:14} {v:12} {i:12.0f} {c:12.0f} {i/c if c else 0:5.2f} {100*pi/(i+pi) if i+pi else 0:7.1f} {(100*(i/bi-1) if bi else 0):+17.1f}% {(100*(c/bc-1) if bc else 0):+6.1f}%  {cs[0]:.0f}..{cs[-1]:.0f}")
