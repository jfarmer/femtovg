#!/usr/bin/env python3
"""Cycles at a fixed E-core clock. The efficiency cores change clock between runs
and within a run (A14: frames at ~0.6 GHz and at ~1.8 GHz, rarely between); at a
higher clock a cache or TLB miss costs more cycles, so cycles from runs at
different clocks do not compare. Each warm frame's clock is measured as its
encode cycles over its encode wall time (E-core frames only); frames are binned
by clock, pooled over the runs of a variant, and the median per (phase, file,
zoom) is summed over the keys every variant has in that bin.
usage: dvfs.py <runs> <dev> [lo:hi GHz ...]   (default bands 0.45:0.65 1.65:2.0)
writes <dev>/dvfs.json and prints markdown"""
import csv, glob, json, os, re, statistics, sys, collections
RUNS, DEV = sys.argv[1], sys.argv[2]
BANDS = [tuple(map(float, b.split(":"))) for b in sys.argv[3:]] or [(0.45, 0.65), (1.65, 2.0)]
VARS = ["m", "a", "b", "c", "pp", "pc"]
VN = {"m": "master", "a": "A", "b": "B", "c": "C", "pp": "pp5", "pc": "pc2"}
GROUPS = {"curve-heavy (curve + curvehd)": ("curve", "curvehd"), "BuseyBench (busey + buseyhd)": ("busey", "buseyhd")}
frames = collections.defaultdict(list)   # (v, band) -> rows
hist = {}
for f in glob.glob(os.path.join(RUNS, DEV, "plain", "soak-*-p*.csv")):
    m = re.search(r"soak-(m|a|b|c|pp|pc)-p(\d+)\.csv$", f)
    if not m:
        continue
    v = m.group(1)
    h = collections.Counter()
    for r in csv.DictReader(open(f)):
        if r["pass"] == "0" or r.get("rep", "1") == "0" or int(r["p_cyc"]) or float(r["encode_ms"]) < 0.5:
            continue
        g = int(r["enc_e_cyc"]) / float(r["encode_ms"]) / 1e6
        h[round(g, 1)] += 1
        for b in BANDS:
            if b[0] <= g < b[1]:
                frames[(v, b)].append(r)
    hist[os.path.basename(f)] = dict(sorted(h.items()))
out = {"bands": {}, "hist": hist}
print(f"### {DEV}: warm-frame cycles at a fixed E-core clock (frames binned by measured encode clock, pooled over runs)\n")
for b in BANDS:
    med = {}
    for v in VARS:
        by = collections.defaultdict(list)
        for r in frames.get((v, b), []):
            by[(r["phase"], r["file"], r["zoom"])].append(r)
        med[v] = {k: (statistics.median(int(r["e_cyc"]) for r in rs), statistics.median(int(r["e_instr"]) for r in rs), len(rs),
                      statistics.median(int(r["e_cyc"]) / float(r["wall_ms"]) for r in rs)) for k, rs in by.items()}
    present = [v for v in VARS if med[v]]
    if "m" not in present:
        print(f"band {b}: no master frames\n")
        continue
    print(f"\n**clock {b[0]}-{b[1]} GHz**\n")
    print("| group | variant | keys | frames | instr/pass | vs master | cycles/pass | vs master | IPC |")
    print("|---|---|---|---|---|---|---|---|---|")
    res = {}
    for gname, phs in GROUPS.items():
        keys = set.intersection(*[{k for k in med[v] if k[0] in phs} for v in present]) if present else set()
        if not keys:
            continue
        base = None
        for v in present:
            C = sum(med[v][k][0] for k in keys); I = sum(med[v][k][1] for k in keys); n = sum(med[v][k][2] for k in keys)
            if v == "m":
                base = (I, C)
            res.setdefault(gname, {})[v] = {"instr": I, "cyc": C, "keys": len(keys), "frames": n}
            print(f"| {gname} | {VN[v]} | {len(keys)} | {n} | {I/1e6:.1f} M | {(I/base[0]-1)*100:+.1f} % | {C/1e6:.1f} M | {(C/base[1]-1)*100:+.1f} % | {I/C:.2f} |")
    out["bands"][f"{b[0]}-{b[1]}"] = res
    KEYS = [("curvehd", "c_tiger", "1"), ("curvehd", "c_puzzle-fox", "1"), ("curvehd", "c_mr-settodefault", "1"), ("curve", "c_tiger", "1"), ("curve", "c_tiger", "4")]
    rows = []
    for k in KEYS:
        if not all(k in med[v] for v in present):
            continue
        mI, mC = med["m"][k][1], med["m"][k][0]
        rows.append(f"| {k[0]} {k[1]} z{k[2]} | " + " | ".join(f"{(med[v][k][1]/mI-1)*100:+.1f} / {(med[v][k][0]/mC-1)*100:+.1f}" for v in present if v != "m") + f" | {min(med[v][k][2] for v in present)} |")
        res.setdefault("files", {})[" ".join(k)] = {v: {"instr": med[v][k][1], "cyc": med[v][k][0], "n": med[v][k][2]} for v in present}
    if rows:
        print("\nkey files at this clock, instructions / cycles vs master (%):\n")
        print("| frame | " + " | ".join(VN[v] for v in present if v != "m") + " | min frames per variant |")
        print("|---|" + "---|" * len(present))
        print("\n".join(rows))
json.dump(out, open(os.path.join(RUNS, DEV, "dvfs.json"), "w"), indent=1)
