#!/usr/bin/env python3
"""transpose_table.py: frame-loop counters (pmcf-t<core><file>-<i>-<variant>.txt) of the masks off, the masks as
before and the masks kept transposed, pooled per file, core kind and variant: IPC, L1D load and store misses and
branch mispredicts a thousand instructions, and the share of the cycles under the mask path's functions."""
import collections, glob, re
num = r'([\d.]+)'
line_re = re.compile(r'^\s*([EP])(?:-cores, all| (\S+))\s+instr\s+' + num + r' M\s+cycles\s+' + num + r' M.*?L1D ld miss\s+' + num +
                     r' k.*?st miss\s+' + num + r' k.*?mispred\s+' + num + r' k')
data = collections.defaultdict(lambda: collections.defaultdict(lambda: [0.0] * 5))
for path in sorted(glob.glob('pmcf-t[ep]*.txt')):
    tag = path[len('pmcf-t'):-4]
    core, rest = tag[0].upper(), tag[1:]
    f, _, v = rest.split('-', 2)
    for line in open(path):
        m = line_re.match(line)
        if not m or m.group(1) != core:
            continue
        name = m.group(2) or 'all'
        for i, x in enumerate(map(float, m.groups()[2:])):
            data[(f, core, v)][name][i] += x
names = {'tfrvs_off': 'masks off', 'tfrvs': 'masks, as before', 'tfrvt': 'masks, transposed'}
funcs = ['fill_through_mask', 'Coverage::resolve', 'upload_fill_masks', 'update_image']
for f in sorted({k[0] for k in data}):
    for core in 'EP':
        print(f'{f} on {core}-cores:        IPC  L1D ld/ki  st/ki  mispred/ki | ' + '  '.join(funcs))
        for v in names:
            if (f, core, v) not in data:
                continue
            d = data[(f, core, v)]
            ins, cyc, ld, st, mp = d['all']
            shares = '  '.join(f'{100 * d[fn][1] / cyc:{len(fn)}.1f}' for fn in funcs)
            print(f'  {names[v]:18s} {ins / cyc:4.2f}  {ld / ins:8.2f}  {st / ins:5.2f}  {mp / ins:9.2f}  | {shares}')
