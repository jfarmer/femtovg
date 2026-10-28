#!/usr/bin/env python3
"""Phone PMU study: tables per device and variant from
  <runs>/<dev>/plain/soak-<v>-p<k>.csv   (thread_selfcounts per frame, MEM_PEAKS footprint; warm frames = rep >= 1, pass >= 1)
  <runs>/<dev>/rec/soak-<v>-<set>-r<k>.csv + agg-<v>-<set>-r<k>.json (Instruments counters-profile aggregate)
  <runs>/points/probe.tsv               (points / vertices per frame per tolerance, Mac anatomy probe)
usage: analyze.py <runs> <dev> [...]   -> markdown on stdout, JSON summary next to the data"""
import csv, json, sys, glob, os, re, statistics, collections

RUNS = sys.argv[1]
VARS = ["m", "a", "b", "c", "pp", "pc"]
VNAME = {"m": "master", "a": "A (tol 1/16)", "b": "B (straddle)", "c": "C (straddle + tol 1/8)",
         "pp": "pp5 (point costs)", "pc": "pc2 (pp5 + C)"}
TOL = {"m": "0.25", "a": "0.0625", "b": "0.25", "c": "0.125", "pp": "0.25", "pc": "0.125"}
VRE = "(m|a|b|c|pp|pc)"
PHASES = ["curve", "curvehd", "busey", "buseyhd"]
FRAMING = {"curve": ("small", ["1", "2", "4"]), "curvehd": ("hd", ["1"]), "busey": ("small", ["1", "2", "4"]), "buseyhd": ("hd", ["1"])}
SETS = {
    "set1": ["Cycles", "Instructions", "INST_SIMD_ALU", "INST_SIMD_LD", "INST_SIMD_ST", "L1D_CACHE_MISS_LD", "L1D_CACHE_MISS_ST", "L1D_CACHE_WRITEBACK", "L1D_TLB_MISS", "MAP_STALL"],
    "set2": ["Cycles", "Instructions", "INST_INT_ALU", "INST_INT_LD", "INST_INT_ST", "L1D_CACHE_MISS_LD", "L1D_CACHE_MISS_ST", "MAP_DISPATCH_BUBBLE", "L1I_CACHE_MISS_DEMAND", "MAP_REWIND"],
    "set3": ["Cycles", "Instructions", "INST_LDST", "INST_BRANCH", "BRANCH_MISPRED_NONSPEC", "L1D_CACHE_MISS_LD", "L1D_CACHE_MISS_ST", "L1D_TLB_MISS", "L2_TLB_MISS_DATA", "MAP_STALL"],
    # A14: Instruments refuses set2 ("INST_INT_ST: conflicting events") although the kpep masks fit
    "set2b": ["Cycles", "Instructions", "INST_INT_ALU", "L1D_CACHE_MISS_LD", "L1D_CACHE_MISS_ST", "MAP_DISPATCH_BUBBLE", "L1I_CACHE_MISS_DEMAND", "MAP_REWIND", "L2_TLB_MISS_INSTRUCTION", "L1D_CACHE_WRITEBACK"],
}

def fnum(x):
    return float(x) if x not in ("", None) else 0.0

def load_points():
    pts = {}
    p = os.path.join(RUNS, "points", "probe.tsv")
    if not os.path.exists(p):
        return pts
    for line in open(p):
        n, fr, z, tol, probe = line.rstrip("\n").split("\t")
        d = {k: int(v) for k, v in (kv.split("=") for kv in probe.split()[1:])}
        pts[(n, fr, z.rstrip("0").rstrip(".") if "." in z else z, tol)] = d
    return pts
POINTS = load_points()

def zkey(z):
    z = str(z)
    return z[:-2] if z.endswith(".0") else z

def frame_stats(path, cold=False):
    """Per (phase, file, zoom): medians over passes >= 1 of the counters of the warm
    frames (rep >= 1: the same content redrawn; cold=True takes the rep-0 frames,
    drawn right after another file); and per-frame memory maxima."""
    rows = list(csv.DictReader(open(path)))
    by = collections.defaultdict(list)
    for r in rows:
        if r["pass"] == "0":
            continue
        rep = r.get("rep", "1")
        if (rep == "0") != cold:
            continue
        by[(r["phase"], r["file"], zkey(r["zoom"]))].append(r)
    med = {}
    for k, rs in by.items():
        med[k] = {c: statistics.median(fnum(r[c]) for r in rs) for c in
                  ("e_instr", "e_cyc", "p_instr", "p_cyc", "enc_e_instr", "enc_e_cyc", "wall_ms", "encode_ms", "task_instr", "task_cyc", "task_pinstr",
                   "peak_footprint", "peak_graphics", "footprint_after", "transient_bytes")}
        med[k]["peak_max"] = max(fnum(r["peak_footprint"]) for r in rs)
        # The least disturbed frame: interrupts, preemption and cache pollution from
        # other work only ever add instructions / cycles to a frame.
        med[k]["min_instr"] = min(fnum(r["e_instr"]) + fnum(r["p_instr"]) for r in rs)
        med[k]["min_cyc"] = min(fnum(r["e_cyc"]) + fnum(r["p_cyc"]) for r in rs)
        med[k]["n"] = len(rs)
    life = max((fnum(r["lifetime_max"]) for r in rows), default=0)
    return med, life, len(rows)

def phase_sum(med, phase, col):
    return sum(v[col] for k, v in med.items() if k[0] == phase)

def points_per_pass(phase, v, col="points"):
    fr, zs = FRAMING[phase]
    pre = "c_" if phase.startswith("curve") else "b_"
    tot = 0
    for (n, f, z, tol), d in POINTS.items():
        if n.startswith(pre) and f == fr and z in zs and tol == TOL[v]:
            tot += d[col]
    return tot

def meta_thermal(path):
    if not os.path.exists(path):
        return "?"
    states = re.findall(r"thermal=(\w+)", open(path).read())
    return "/".join(sorted(set(states), key=states.index)) if states else "?"

def pct(a, b):
    return (a / b - 1) * 100 if b else float("nan")

def analyze(dev):
    out = []
    P = os.path.join(RUNS, dev)
    plain = collections.defaultdict(list)
    for f in sorted(glob.glob(os.path.join(P, "plain", "soak-*-p*.csv"))):
        m = re.search(r"soak-" + VRE + r"-p(\d+)\.csv$", f)
        if m:
            med, life, n = frame_stats(f)
            cold = frame_stats(f, cold=True)[0]
            plain[m.group(1)].append({"tag": os.path.basename(f), "med": med, "cold": cold, "life": life, "n": n,
                                      "thermal": meta_thermal(f.replace("soak-", "meta-").replace(".csv", ".txt"))})
    summary = {"device": dev, "plain": {}, "rec": {}}
    sysinfo = sorted(glob.glob(os.path.join(P, "plain", "sysinfo-*.txt")))
    if sysinfo:
        info = dict(l.strip().split("=", 1) for l in open(sysinfo[0]) if "=" in l and not l.startswith("probe"))
        summary["sysinfo"] = info
        out.append(f"### {dev}: {info.get('hw.machine')} iOS {info.get('kern.osproductversion')} ({info.get('kern.osversion')})\n")
        out.append("| perf level | name | cores | L1I | L1D | L2 (shared by) |\n|---|---|---|---|---|---|")
        for lv in (0, 1):
            g = lambda k: info.get(f"hw.perflevel{lv}.{k}", "n/a")
            kb = lambda k: f"{int(g(k)) // 1024} KiB" if g(k).isdigit() else g(k)
            out.append(f"| {lv} | {g('name')} | {g('physicalcpu')} | {kb('l1icachesize')} | {kb('l1dcachesize')} | {kb('l2cachesize')} ({g('cpusperl2')} cores) |")
        out.append(f"\ncache line {info.get('hw.cachelinesize')} B, page {info.get('hw.pagesize')} B, RAM {int(info.get('hw.memsize', 0)) / 2**30:.1f} GiB\n")
    if plain:
        out.append(f"#### {dev}: render-thread counts per pass (thread_selfcounts, E-cores; median frame of passes 1..n, summed over files x zooms)\n")
        out.append("| phase | variant | instructions/pass | vs master | cycles/pass | vs master | IPC | P-core share | encode share | wall ms/pass | runs spread (instr / cyc) | thermal |")
        out.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
        for ph in PHASES:
            base = None
            for v in VARS:
                if v not in plain:
                    continue
                runs = plain[v]
                ins = [phase_sum(r["med"], ph, "e_instr") + phase_sum(r["med"], ph, "p_instr") for r in runs]
                cyc = [phase_sum(r["med"], ph, "e_cyc") + phase_sum(r["med"], ph, "p_cyc") for r in runs]
                pin = [phase_sum(r["med"], ph, "p_instr") for r in runs]
                enc = [phase_sum(r["med"], ph, "enc_e_instr") for r in runs]
                wall = [phase_sum(r["med"], ph, "wall_ms") for r in runs]
                if not ins or ins[0] == 0:
                    continue
                I, C = statistics.mean(ins), statistics.mean(cyc)
                if v == "m":
                    base = (I, C)
                sp_i = (max(ins) - min(ins)) / I * 100 if len(ins) > 1 else float("nan")
                sp_c = (max(cyc) - min(cyc)) / C * 100 if len(cyc) > 1 else float("nan")
                th = ",".join(r["thermal"] for r in runs)
                out.append(f"| {ph} | {VNAME[v]} | {I/1e6:.1f} M | {pct(I, base[0]) if base else 0:+.1f} % | {C/1e6:.1f} M | {pct(C, base[1]) if base else 0:+.1f} % | {I/C:.2f} | {sum(pin)/sum(ins)*100:.1f} % | {sum(enc)/sum(ins)*100:.0f} % | {statistics.mean(wall):.0f} | {sp_i:.1f} / {sp_c:.1f} % | {th} |")
                mins = [phase_sum(r["med"], ph, "min_instr") for r in runs]
                minc = [phase_sum(r["med"], ph, "min_cyc") for r in runs]
                summary["plain"].setdefault(v, {})[ph] = {"instr": I, "cyc": C, "runs_instr": ins, "runs_cyc": cyc, "wall": statistics.mean(wall),
                                                          "min_instr": statistics.mean(mins), "min_cyc": statistics.mean(minc), "runs_min_instr": mins, "runs_min_cyc": minc}
        # cold frames: drawn right after another file (pipelines the previous frame did not use were evicted)
        out.append(f"\n#### {dev}: cold frames (rep 0: the first frame of a file, drawn right after another file; pipelines and shaders the previous frame did not use were dropped) vs warm frames (rep >= 1)\n")
        out.append("| phase | variant | warm instr/pass | cold instr/pass | cold - warm | cold vs master cold | warm cycles/pass | cold cycles/pass | cold cycles vs master cold |")
        out.append("|---|---|---|---|---|---|---|---|---|")
        for ph in PHASES:
            cbase = None
            for v in VARS:
                runs = plain.get(v)
                if not runs:
                    continue
                w = statistics.mean(phase_sum(r["med"], ph, "e_instr") + phase_sum(r["med"], ph, "p_instr") for r in runs)
                c = statistics.mean(phase_sum(r["cold"], ph, "e_instr") + phase_sum(r["cold"], ph, "p_instr") for r in runs)
                wc = statistics.mean(phase_sum(r["med"], ph, "e_cyc") + phase_sum(r["med"], ph, "p_cyc") for r in runs)
                cc = statistics.mean(phase_sum(r["cold"], ph, "e_cyc") + phase_sum(r["cold"], ph, "p_cyc") for r in runs)
                if not w:
                    continue
                if v == "m":
                    cbase = (c, cc)
                summary["plain"].setdefault(v, {}).setdefault(ph, {}).update({"cold_instr": c, "cold_cyc": cc})
                out.append(f"| {ph} | {VNAME[v]} | {w/1e6:.1f} M | {c/1e6:.1f} M | {pct(c, w):+.0f} % | {pct(c, cbase[0]) if cbase else 0:+.1f} % | {wc/1e6:.1f} M | {cc/1e6:.1f} M | {pct(cc, cbase[1]) if cbase else 0:+.1f} % |")
        # key files
        keys = [("curvehd", "c_tiger", "1"), ("curvehd", "c_puzzle-fox", "1"), ("curvehd", "c_mr-settodefault", "1"),
                ("curvehd", "c_duckduckgo", "1"), ("curvehd", "c_nyt-crossplay", "1"), ("curve", "c_tiger", "1"), ("curve", "c_tiger", "4")]
        svg = sorted({k[1] for r in plain.get("m", []) for k in r["med"] if k[1].startswith("c_svg")})
        out.append(f"\n#### {dev}: per frame, key files (instructions on the render thread, median frame, mean of the runs)\n")
        others = [v for v in VARS[1:] if v in plain]
        out.append("| frame | points m / a / c | master instr | " + " | ".join(VNAME[v].split(" ")[0] for v in others) + " | master cycles | " + " | ".join(VNAME[v].split(" ")[0] for v in others) + " |")
        out.append("|---|---|---|" + "---|" * (2 * len(others) + 1))
        def frame_val(v, key, col):
            vals = [r["med"][key]["e_" + col] + r["med"][key]["p_" + col] for r in plain.get(v, []) if key in r["med"]]
            return statistics.mean(vals) if vals else float("nan")
        rows_k = keys + [("curvehd", "svgenius x%d" % len(svg), "1"), ("curve", "svgenius x%d" % len(svg), "1")]
        for key in rows_k:
            ph, f, z = key
            def val(v, col):
                if f.startswith("svgenius"):
                    return sum(frame_val(v, (ph, n, z), col) for n in svg)
                return frame_val(v, key, col)
            fr = FRAMING[ph][0]
            def pts(v):
                names = svg if f.startswith("svgenius") else [f]
                return sum(POINTS.get((n, fr, z, TOL[v]), {}).get("points", 0) for n in names)
            mi, mc = val("m", "instr"), val("m", "cyc")
            cells_i = " | ".join(f"{pct(val(v, 'instr'), mi):+.1f} %" for v in others)
            cells_c = " | ".join(f"{pct(val(v, 'cyc'), mc):+.1f} %" for v in others)
            out.append(f"| {ph} {f} z{z} | {pts('m')} / {pts('a')} / {pts('c')} | {mi/1e6:.2f} M | {cells_i} | {mc/1e6:.2f} M | {cells_c} |")
        # per-point
        if POINTS and "m" in plain:
            out.append(f"\n#### {dev}: cost per flattened point (points per pass from the anatomy probe)\n")
            out.append("| phase | variant | points/pass | vertices/pass | extra points vs master | extra instr per extra point | extra cycles per extra point |")
            out.append("|---|---|---|---|---|---|---|")
            for ph in ("curve", "curvehd", "busey", "buseyhd"):
                if ph not in summary["plain"].get("m", {}):
                    continue
                pm = points_per_pass(ph, "m")
                for v in VARS:
                    if v not in summary["plain"] or ph not in summary["plain"][v]:
                        continue
                    pv = points_per_pass(ph, v); vv = points_per_pass(ph, v, "flush_verts")
                    dI = summary["plain"][v][ph]["instr"] - summary["plain"]["m"][ph]["instr"]
                    dC = summary["plain"][v][ph]["cyc"] - summary["plain"]["m"][ph]["cyc"]
                    dp = pv - pm
                    if v == "m":
                        per_i = per_c = "-"
                    else:
                        per_i = f"{dI/dp:.0f}" if dp else (f"same points; {dI/pm:+.0f} per point" if pm else "")
                        per_c = f"{dC/dp:.0f}" if dp else (f"same points; {dC/pm:+.0f} per point" if pm else "")
                    out.append(f"| {ph} | {VNAME[v]} | {pv} | {vv} | {dp:+d} ({pct(pv, pm):+.1f} %) | {per_i} | {per_c} |")
                    summary["plain"][v][ph]["points"] = pv
        # memory
        out.append(f"\n#### {dev}: memory (phys_footprint sampled every 0.2 ms; BuseyBench portraits)\n")
        out.append("| variant | busey peak (max frame) | busey peak (median of per-frame peaks) | buseyhd peak (max frame) | graphics part at hd peak | lifetime max of the run | footprint after last frame |")
        out.append("|---|---|---|---|---|---|---|")
        for v in VARS:
            if v not in plain:
                continue
            vals = []
            for r in plain[v]:
                b = [x for k, x in r["med"].items() if k[0] == "busey"]
                h = [x for k, x in r["med"].items() if k[0] == "buseyhd"]
                if not b and not h:
                    continue
                pk = max((x["peak_max"] for x in b), default=0)
                pmed = statistics.median([x["peak_footprint"] for x in b]) if b else 0
                hk = max(h, key=lambda x: x["peak_max"]) if h else None
                vals.append((pk, pmed, hk["peak_max"] if hk else 0, hk["peak_graphics"] if hk else 0, r["life"],
                             max((x["footprint_after"] for x in b + h), default=0)))
            if vals:
                M = lambda i: max(x[i] for x in vals) / 2**20
                out.append(f"| {VNAME[v]} | {M(0):.1f} MiB | {statistics.mean(x[1] for x in vals)/2**20:.1f} MiB | {M(2):.1f} MiB | {M(3):.1f} MiB | {M(4):.1f} MiB | {M(5):.1f} MiB |")
                summary["plain"].setdefault(v, {})["mem"] = vals
    # recordings
    recs = collections.defaultdict(lambda: collections.defaultdict(list))
    for f in sorted(glob.glob(os.path.join(P, "rec", "agg-*.json"))):
        m = re.search(r"agg-" + VRE + r"-(set\w+)-r(\d+)\.json$", f)
        if not m:
            continue
        v, s = m.group(1), m.group(2)
        d = json.load(open(f))
        csvp = f.replace("agg-", "soak-").replace(".json", ".csv")
        med = frame_stats(csvp)[0] if os.path.exists(csvp) else {}
        rows = list(csv.DictReader(open(csvp))) if os.path.exists(csvp) else []
        recs[v][s].append({"agg": d, "rows": rows, "med": med, "tag": os.path.basename(f),
                           "thermal": meta_thermal(csvp.replace("soak-", "meta-").replace(".csv", ".txt"))})
    if recs:
        out.append(f"\n#### {dev}: event mix of the render thread on the E-cores (Instruments counters-profile samples; per 1000 instructions unless noted)\n")
        def phase_vec(run, s, phases):
            tot = None
            for k, vec in run["agg"]["per_interval"].items():
                name, kind = k.rsplit("|", 1)
                if kind != "E" or name.split("/")[0] not in phases or name.endswith("#0") or "/r0#" in name:
                    continue
                tot = list(vec) if tot is None else [a + b for a, b in zip(tot, vec)]
            return tot
        groups = {"curve (460x260, z1/2/4)": ["curve"], "curvehd (1080p)": ["curvehd"], "busey (both framings)": ["busey", "buseyhd"]}
        for gname, phs in groups.items():
            out.append(f"\n**{gname}**\n")
            out.append("| variant | coverage | IPC | SIMD share (ALU+LD+ST) | int ALU share | load/store share | branch share | L1D ld miss | L1D st miss | L1D writeback | L1D TLB miss | L2 TLB miss | L1I miss | branch mispred | MAP stall % cyc | dispatch bubble % cyc |")
            out.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
            for v in VARS:
                if v not in recs:
                    continue
                ev = collections.defaultdict(list)  # name -> per-run ratios per instruction
                cov = []; ipc = []
                for s, runs in recs[v].items():
                    names = SETS[s]
                    for run in runs:
                        vec = phase_vec(run, s, phs)
                        if not vec or vec[1] == 0:
                            continue
                        I = vec[1]
                        for n, x in zip(names[2:], vec[2:]):
                            ev[n].append(x / I)
                        ev["_cyc"].append(vec[0] / I)
                        ipc.append(I / vec[0])
                        sel = sum(fnum(r["e_instr"]) + fnum(r["p_instr"]) for r in run["rows"] if r["phase"] in phs and r["pass"] != "0" and r.get("rep", "1") != "0")
                        if sel:
                            cov.append(I / sel)
                if not ev:
                    continue
                g = lambda n: statistics.mean(ev[n]) if ev.get(n) else float("nan")
                simd = g("INST_SIMD_ALU") + g("INST_SIMD_LD") + g("INST_SIMD_ST")
                cpi = g("_cyc")
                out.append(f"| {VNAME[v]} | {statistics.mean(cov)*100 if cov else float('nan'):.0f} % | {statistics.mean(ipc):.2f} | {simd*100:.1f} % ({g('INST_SIMD_ALU')*100:.1f}/{g('INST_SIMD_LD')*100:.1f}/{g('INST_SIMD_ST')*100:.1f}) | {g('INST_INT_ALU')*100:.1f} % | {g('INST_LDST')*100:.1f} % | {g('INST_BRANCH')*100:.1f} % | {g('L1D_CACHE_MISS_LD')*1000:.2f} | {g('L1D_CACHE_MISS_ST')*1000:.2f} | {g('L1D_CACHE_WRITEBACK')*1000:.2f} | {g('L1D_TLB_MISS')*1000:.3f} | {g('L2_TLB_MISS_DATA')*1000:.3f} | {g('L1I_CACHE_MISS_DEMAND')*1000:.2f} | {g('BRANCH_MISPRED_NONSPEC')*1000:.2f} | {g('MAP_STALL')/cpi*100:.1f} % | {g('MAP_DISPATCH_BUBBLE')/cpi*100:.1f} % |")
                summary["rec"].setdefault(v, {})[gname] = {n: statistics.mean(x) for n, x in ev.items()} | {"coverage": cov, "ipc": ipc,
                    "spread": {n: (max(x) - min(x)) / statistics.mean(x) * 100 if len(x) > 1 and statistics.mean(x) else None for n, x in ev.items()}}
        # misses per extra point
        if "m" in summary["rec"] and summary["plain"]:
            out.append(f"\n#### {dev}: L1D misses and SIMD instructions per frame pass, and per extra point (ratios x thread_selfcounts instructions)\n")
            out.append("| phase | variant | L1D ld misses/pass | L1D st misses/pass | SIMD instr/pass | extra L1D ld misses per extra point | extra SIMD per extra point | extra non-SIMD per extra point |")
            out.append("|---|---|---|---|---|---|---|---|")
            for ph, gname in (("curve", "curve (460x260, z1/2/4)"), ("curvehd", "curvehd (1080p)")):
                base = None
                for v in VARS:
                    try:
                        I = summary["plain"][v][ph]["instr"]; r = summary["rec"][v][gname]
                    except KeyError:
                        continue
                    ld = r.get("L1D_CACHE_MISS_LD", 0) * I; st = r.get("L1D_CACHE_MISS_ST", 0) * I
                    simd = (r.get("INST_SIMD_ALU", 0) + r.get("INST_SIMD_LD", 0) + r.get("INST_SIMD_ST", 0)) * I
                    pts = summary["plain"][v][ph].get("points", 0)
                    if v == "m":
                        base = (ld, st, simd, I, pts)
                    dp = pts - base[4] if base else 0
                    cell = lambda d: f"{d/dp:.1f}" if dp else ""
                    out.append(f"| {ph} | {VNAME[v]} | {ld/1e3:.0f} k | {st/1e3:.0f} k | {simd/1e6:.2f} M | {cell(ld-base[0]) if base else ''} | {cell(simd-base[2]) if base else ''} | {cell((I-simd)-(base[3]-base[2])) if base else ''} |")
    json.dump(summary, open(os.path.join(P, "summary.json"), "w"), indent=1, default=str)
    return "\n".join(out)

for dev in sys.argv[2:]:
    print(analyze(dev))
    print()
