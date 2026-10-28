#!/usr/bin/env python3
"""callers.py EXPORT.xml PROCESS PATTERN [CALLER]: for the counters-profile samples whose backtrace holds PATTERN,
the nearest frame above it whose name holds CALLER (default 'femtovg'), with the samples' cycles, instructions and
mispredicts summed per caller and core kind."""
import collections, sys
import xml.etree.ElementTree as ET

path, want, pattern = sys.argv[1:4]
caller = sys.argv[4] if len(sys.argv) > 4 else 'femtovg'
ids, out = {}, collections.defaultdict(lambda: [0, 0, 0, 0])
for _, el in ET.iterparse(path, events=('end',)):
    if el.tag != 'row':
        if el.get('id'):
            ids[el.get('id')] = el
        continue
    get = lambda tag: next(((ids.get(c.get('ref'), c) if c.get('ref') else c) for c in el
                            if (ids.get(c.get('ref'), c) if c.get('ref') else c).tag == tag), None)
    proc, core, pmc, bt = get('process'), get('core'), get('pmc-events'), get('tagged-backtrace')
    if proc is None or pmc is None or bt is None or want not in (proc.get('fmt') or ''):
        continue
    counts = [int(v) for v in (pmc.text or '').split()]
    if len(counts) != 8:
        continue
    names = [(ids.get(f.get('ref'), f) if f.get('ref') else f).get('name') or '' for f in bt]
    hit = next((i for i, n in enumerate(names) if pattern in n), None)
    if hit is None:
        continue
    up = next((n for n in names[hit + 1:] if caller in n and pattern not in n), '?')
    kind = 'E' if core is not None and 'E Core' in (core.get('fmt') or '') else 'P'
    acc = out[(kind, up.split('::h')[0][-110:])]
    acc[0] += counts[4]; acc[1] += counts[3]; acc[2] += counts[0]; acc[3] += 1
for (kind, name), (cyc, ins, mp, n) in sorted(out.items(), key=lambda kv: -kv[1][0])[:15]:
    print(f'{kind} {cyc / 1e6:8.2f} M cyc {ins / 1e6:8.2f} M instr {mp / 1e3:7.1f} k mispred {n:5d} samples  {name}')
