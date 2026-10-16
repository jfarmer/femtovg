#!/usr/bin/env python3
"""pmc_agg.py EXPORT.xml [process-substring] [function-pattern|...] : totals of a CPU Counters `counters-profile`
export (the femtovg-events template: BRANCH_MISPRED_NONSPEC, L1D_CACHE_MISS_LD, L1I_CACHE_MISS_DEMAND, Instructions,
Cycles, INST_BRANCH, L1D_CACHE_MISS_ST, L1D_TLB_MISS, sampled every millisecond with the user backtrace) per core type
for the processes whose name contains the substring, and per function for the samples whose backtrace holds one of the
patterns (inclusive: a sample's counts go to every matching frame once). ONLY=pattern|... keeps only the
samples whose backtrace holds one of those, in every table: a frame loop's work without the start-up. Prints counts and the derived rates:
L1D load misses per 1,000 instructions, branch mispredicts per 1,000 branches, instructions per cycle."""
import collections, sys
import xml.etree.ElementTree as ET

EVENTS = ['mispred', 'l1d_ld', 'l1i', 'instr', 'cycles', 'branch', 'l1d_st', 'l1d_tlb']
path = sys.argv[1]
want = sys.argv[2] if len(sys.argv) > 2 else ''
patterns = sys.argv[3].split('|') if len(sys.argv) > 3 else []

ids = {}
by_core = collections.defaultdict(lambda: [0] * len(EVENTS))
by_func = collections.defaultdict(lambda: collections.defaultdict(lambda: [0] * len(EVENTS)))
by_leaf = collections.defaultdict(lambda: collections.defaultdict(lambda: [0] * len(EVENTS)))
for _, el in ET.iterparse(path, events=('end',)):
    if el.tag != 'row':
        if el.get('id'):
            ids[el.get('id')] = el
        continue
    def get(tag):
        for c in el:
            c = ids.get(c.get('ref'), c) if c.get('ref') else c
            if c.tag == tag:
                return c
        return None
    proc, core, pmc, bt = get('process'), get('core'), get('pmc-events'), get('tagged-backtrace')
    if proc is None or pmc is None or want not in (proc.get('fmt') or ''):
        continue
    counts = [int(v) for v in (pmc.text or '').split()]
    if len(counts) != len(EVENTS):
        continue
    kind = 'E' if core is not None and 'E Core' in (core.get('fmt') or '') else 'P'
    only = __import__('os').environ.get('ONLY')
    if only:
        names = [(ids.get(f.get('ref'), f) if f.get('ref') else f).get('name') or '' for f in (bt if bt is not None else [])]
        if not any(part in n for n in names for part in only.split('|')):
            continue
    tot = by_core[kind]
    for i, v in enumerate(counts):
        tot[i] += v
    if bt is not None:
        frames = [ids.get(f.get('ref'), f) if f.get('ref') else f for f in bt]
        focus = __import__('os').environ.get('FOCUS')
        if focus and not any(part in (f.get('name') or '') for f in frames for part in focus.split('|')):
            frames = []
        leaf = (frames[0].get('name') or '?') if frames else '?'
        leaf = leaf.split('::h')[0][-70:]
        agg = by_leaf[kind][leaf]
        for i, v in enumerate(counts):
            agg[i] += v
    if patterns and bt is not None:
        names = set()
        for f in bt:
            f = ids.get(f.get('ref'), f) if f.get('ref') else f
            names.add(f.get('name') or '')
        for p in patterns:
            if any(p in n for n in names):
                agg = by_func[kind][p]
                for i, v in enumerate(counts):
                    agg[i] += v


def show(label, c):
    d = dict(zip(EVENTS, c))
    ipc = d['instr'] / d['cycles'] if d['cycles'] else 0
    l1 = 1000 * d['l1d_ld'] / d['instr'] if d['instr'] else 0
    st = 1000 * d['l1d_st'] / d['instr'] if d['instr'] else 0
    mp = 1000 * d['mispred'] / d['branch'] if d['branch'] else 0
    print(f"{label:28s} instr {d['instr']/1e6:9.2f} M  cycles {d['cycles']/1e6:9.2f} M  IPC {ipc:4.2f}  "
          f"L1D ld miss {d['l1d_ld']/1e3:8.1f} k ({l1:5.2f}/ki)  st miss {d['l1d_st']/1e3:7.1f} k ({st:4.2f}/ki)  "
          f"mispred {d['mispred']/1e3:7.1f} k ({mp:5.2f}/kbr)  TLB {d['l1d_tlb']/1e3:6.1f} k  L1I {d['l1i']/1e3:6.1f} k")


LEAVES = int(__import__('os').environ.get('LEAVES', '0'))
for kind in sorted(by_core):
    show(f'{kind}-cores, all', by_core[kind])
    for p, c in sorted(by_func[kind].items()):
        show(f'  {kind} {p[:24]}', c)
    if LEAVES and kind == 'E':
        total = by_core[kind][EVENTS.index('cycles')] or 1
        for leaf, c in sorted(by_leaf[kind].items(), key=lambda kv: -kv[1][EVENTS.index('cycles')])[:LEAVES]:
            d = dict(zip(EVENTS, c))
            print(f"    self {100 * d['cycles'] / total:5.1f} % cycles  instr {d['instr']/1e6:8.1f} M  mispred {d['mispred']/1e3:7.1f} k  L1D ld {d['l1d_ld']/1e3:6.1f} k  {leaf}")
