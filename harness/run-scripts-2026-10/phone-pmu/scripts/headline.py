#!/usr/bin/env python3
"""One short table per device from <runs>/<dev>/summary.json (analyze.py) and
<dev>/dvfs.json (dvfs.py): warm-frame render-thread instructions (sum over
files x zooms of each frame's minimum over passes and repeats, mean of the runs;
run range in brackets), cycles at a fixed E-core clock (dvfs.py bins), the cold
frames' instructions, L1D load/store and L2-TLB misses and the SIMD share from the
Instruments samples (per-instruction ratios x exact instructions per pass),
the run's peak phys_footprint (lifetime max, reached on the 1080p BuseyBench
portraits) and the app's __text size.
usage: headline.py <runs> <dev> [...]"""
import json, sys, os, statistics
RUNS = sys.argv[1]
VARS = ["m", "a", "b", "c", "pp", "pc"]
VN = {"m": "master", "a": "A", "b": "B", "c": "C", "pp": "pp5", "pc": "pc2"}
sizes = {}
sp = os.path.join(RUNS, "size", "sizes.md")
if os.path.exists(sp):
    for line in open(sp):
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        if len(c) >= 6 and c[1] in VARS:
            sizes[c[1]] = int(c[4])
pct = lambda a, b: (a / b - 1) * 100 if b else float("nan")
CH, BU = ["curve", "curvehd"], ["busey", "buseyhd"]
G1, G2 = "curve (460x260, z1/2/4)", "curvehd (1080p)"
for dev in sys.argv[2:]:
    S = json.load(open(os.path.join(RUNS, dev, "summary.json")))
    P, R = S["plain"], S.get("rec", {})
    D = {}
    dp = os.path.join(RUNS, dev, "dvfs.json")
    if os.path.exists(dp):
        D = json.load(open(dp))["bands"]
    tot = lambda v, phs, key: sum(P[v][p][key] for p in phs) if v in P and all(p in P[v] and key in P[v][p] for p in phs) else float("nan")
    def rng(v, phs, key, base):
        try:
            r = [sum(x) for x in zip(*[P[v][p][key] for p in phs])]
        except KeyError:
            return ""
        return f" ({pct(min(r), base):+.1f}..{pct(max(r), base):+.1f})" if len(r) > 1 else ""
    def per_pass(v, names):
        x = 0
        for g, ph in ((G1, "curve"), (G2, "curvehd")):
            try:
                x += sum(R[v][g][n] for n in names) * P[v][ph]["instr"]
            except KeyError:
                return float("nan")
        return x
    def band_cyc(v, group):
        cells = []
        for b, res in D.items():
            r = res.get(group, {})
            if v in r and "m" in r:
                cells.append(f"{pct(r[v]['cyc'], r['m']['cyc']):+.1f} % @{b}")
        return "; ".join(cells) if cells else "n/a"
    print(f"\n### {dev}\n")
    print("| variant | curve-heavy instr/pass (vs master, run range) | curve-heavy cycles vs master at fixed clock (GHz) | BuseyBench instr vs master | BuseyBench cycles vs master at fixed clock | cold frames instr vs master | L1D ld misses/pass | L1D st misses/pass | L2 TLB misses/pass | SIMD share of instr | peak footprint (graphics part) | __text vs master |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|")
    nI = tot("m", CH, "min_instr"); bI = tot("m", BU, "min_instr"); cI = tot("m", CH + BU, "cold_instr")
    mld, mst, mtl = per_pass("m", ["L1D_CACHE_MISS_LD"]), per_pass("m", ["L1D_CACHE_MISS_ST"]), per_pass("m", ["L2_TLB_MISS_DATA"])
    def mem(v):
        vals = P.get(v, {}).get("mem")
        if not vals:
            return float("nan"), float("nan")
        return statistics.mean(x[4] for x in vals) / 2**20, statistics.mean(x[3] for x in vals) / 2**20
    mpk = mem("m")[0]
    for v in VARS:
        if v not in P or "curve" not in P[v]:
            continue
        I = tot(v, CH, "min_instr")
        simd = [sum(R.get(v, {}).get(g, {}).get(n, float("nan")) for n in ("INST_SIMD_ALU", "INST_SIMD_LD", "INST_SIMD_ST")) for g in (G1, G2)]
        ld, st, tl = per_pass(v, ["L1D_CACHE_MISS_LD"]), per_pass(v, ["L1D_CACHE_MISS_ST"]), per_pass(v, ["L2_TLB_MISS_DATA"])
        pk, gr = mem(v)
        sz = f"{sizes[v] - sizes['m']:+d} B" if v in sizes and "m" in sizes else ""
        f = lambda x, m, unit=1e3, u="k": f"{x/unit:.0f} {u} ({pct(x, m):+.1f} %)" if x == x else "n/a"
        print(f"| {VN[v]} | {I/1e6:.1f} M ({pct(I, nI):+.1f} %{rng(v, CH, 'runs_min_instr', nI)}) | {band_cyc(v, 'curve-heavy (curve + curvehd)')} | "
              f"{pct(tot(v, BU, 'min_instr'), bI):+.1f} % | {band_cyc(v, 'BuseyBench (busey + buseyhd)')} | {pct(tot(v, CH + BU, 'cold_instr'), cI):+.1f} % | "
              f"{f(ld, mld)} | {f(st, mst)} | {f(tl, mtl, 1e3, 'k')} | {statistics.mean(simd)*100:.1f} % | {pk:.1f} MiB ({pk - mpk:+.1f}; {gr:.0f}) | {sz} |")
