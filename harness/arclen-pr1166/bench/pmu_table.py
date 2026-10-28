#!/usr/bin/env python3
"""usage: pmu_table.py <set> <workload> agg.json  -> events per 1000 instructions per variant (E-cores, intervals #1.. = warm)."""
import json, sys, re, collections
names = {
 "set1": "cycles instr SIMD_ALU SIMD_LD SIMD_ST L1D_MISS_LD L1D_MISS_ST L1D_WB L1D_TLB_MISS YMAP_STALL",
 "set2": "cycles instr INT_ALU INT_LD INT_ST L1D_MISS_LD L1D_MISS_ST MAP_DISPATCH_BUBBLE L1I_MISS ZMAP_REWIND",
 "set2b": "cycles instr INT_ALU L1D_MISS_LD L1D_MISS_ST MAP_DISPATCH_BUBBLE L1I_MISS ZMAP_REWIND L2_TLB_MISS_I L1D_WB",
 "set3": "cycles instr LDST BRANCH BR_MISPRED L1D_MISS_LD L1D_MISS_ST L1D_TLB_MISS L2_TLB_MISS YMAP_STALL",
}
S, W, path = sys.argv[1:4]
cols = names[S].split()
d = json.load(open(path))["per_interval"]
agg = collections.defaultdict(lambda: None); nint = collections.Counter()
for k, v in d.items():
    m = re.match(r"(.+)/r#(\d+)\|(E|P)$", k)
    if not m or m.group(3) != "E": continue
    wv, rep = m.group(1), int(m.group(2))
    if not wv.startswith(W + "-") or rep == 0: continue
    var = wv[len(W) + 1:]
    agg[var] = v if agg[var] is None else [a + b for a, b in zip(agg[var], v)]
    nint[var] += 1
print(f"{S} {W}: events per 1000 instructions (E-cores, sampled; warm intervals)")
print(f"{'variant':12} {'intervals':>9} {'instr M':>8} {'IPC':>5} " + " ".join(f"{c:>10}" for c in cols[2:]))
base = None
for var in ["plain0.5", "plain0.001", "cached0.001", "incr0.001"]:
    v = agg.get(var)
    if v is None: continue
    ins = v[1]
    print(f"{var:12} {nint[var]:9d} {ins/1e6:8.1f} {ins/v[0]:5.2f} " + " ".join(f"{1000*x/ins:10.2f}" for x in v[2:]))
