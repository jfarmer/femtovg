#!/usr/bin/env python3
"""Where the extra work of a variant goes: per app frame (first frame in the app
binary on the sampled stack) and per leaf function, the sampled share of
instructions / L1D load misses in each variant, scaled by the variant's exact
instructions per pass (thread_selfcounts, summary.json), minus master's.
usage: functions.py <dev-dir> <phase> [variant] [key: app|leaf] [n]"""
import json, glob, sys, collections, re
D, PH = sys.argv[1], sys.argv[2]
V = sys.argv[3] if len(sys.argv) > 3 else "a"
KEY = sys.argv[4] if len(sys.argv) > 4 else "app"
N = int(sys.argv[5]) if len(sys.argv) > 5 else 25
summ = json.load(open(f"{D}/summary.json"))
def load(v):
    instr = collections.Counter(); l1d = collections.Counter(); simd = collections.Counter(); tot = collections.Counter()
    for f in glob.glob(f"{D}/rec/agg-{v}-set*-r*.json"):
        s = re.search(r"-(set\w+)-r", f).group(1)
        if s not in ("set1", "set3"):   # column 5 is L1D_CACHE_MISS_LD in these two
            continue
        d = json.load(open(f))
        table = d["per_app_frame"] if KEY == "app" else d["per_leaf"]
        for k, vec in table.items():
            ph, *rest = k.split("|")
            if ph != PH: continue
            binary = "app" if len(rest) > 1 and re.match(r"(Flat|macdrv_)", rest[1] or "") else (rest[1] if len(rest) > 1 else "")
            name = rest[0] if (KEY == "app" or len(rest) < 2) else f"{rest[0]} [{binary}]"
            instr[(s, name)] += vec[1]; tot[(s, "instr")] += vec[1]
            l1d[(s, name)] += vec[5]; tot[(s, "l1d")] += vec[5]
            if s == "set1":
                simd[name] += vec[2] + vec[3] + vec[4]
    I = summ["plain"][v][PH]["instr"]
    names = {n for (_, n) in instr}
    out = {}
    for n in names:
        sets = [s for s in ("set1", "set3") if tot[(s, "instr")]]
        sh = [instr[(s, n)] / tot[(s, "instr")] for s in sets]
        share = sum(sh) / len(sh)
        lsh = [l1d[(s, n)] / tot[(s, "instr")] for s in sets]
        out[n] = (share * I, sum(lsh) / len(lsh) * I, simd[n] / tot[("set1", "instr")] * I if tot[("set1", "instr")] else 0)
    return out, I
m, Im = load("m"); a, Ia = load(V)
rows = []
for n in set(m) | set(a):
    x = m.get(n, (0, 0, 0)); y = a.get(n, (0, 0, 0))
    rows.append((y[0] - x[0], n, x, y))
rows.sort(key=lambda r: -abs(r[0]))
print(f"phase {PH}: master {Im/1e6:.1f} M instr/pass, {V} {Ia/1e6:.1f} M (+{(Ia-Im)/1e6:.1f} M); by {KEY} frame")
print("| function | master M instr/pass | %s | extra M instr | extra L1D ld misses (k) | extra SIMD (M) |" % V)
print("|---|---|---|---|---|---|")
for d, n, x, y in rows[:N]:
    print(f"| {n[:90]} | {x[0]/1e6:.1f} | {y[0]/1e6:.1f} | {d/1e6:+.2f} | {(y[1]-x[1])/1e3:+.0f} | {(y[2]-x[2])/1e6:+.2f} |")
