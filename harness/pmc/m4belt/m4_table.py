#!/usr/bin/env python3
"""m4_table.py: the M4 efficiency-core counters of rec.sh's recordings (pmc-<file>-<i>-<variant>.txt), pooled per file
and variant: IPC, L1D load and store misses a thousand instructions, mispredicts a thousand branches, and the share of
the E-core cycles under each function. Sampled totals vary between recordings, so only rates and shares are compared."""
import collections, glob, re

num = r'([\d.]+)'
line_re = re.compile(r'^\s*(E-cores, all|E \S+)\s+instr\s+' + num + r' M\s+cycles\s+' + num + r' M.*?L1D ld miss\s+' + num +
                     r' k.*?st miss\s+' + num + r' k.*?mispred\s+' + num + r' k \(\s*' + num + r'/kbr\)')
data = collections.defaultdict(lambda: collections.defaultdict(lambda: [0.0] * 6))
for path in sorted(glob.glob('pmc-*.txt')):
    _, f, _, v = path[:-4].split('-', 3)
    for line in open(path):
        m = line_re.match(line)
        if not m:
            continue
        name = m.group(1).replace('E ', '') if m.group(1) != 'E-cores, all' else 'all'
        instr, cyc, ld, st, mp, mprate = map(float, m.groups()[1:])
        branches = 1000 * mp / mprate if mprate else 0
        acc = data[(f, v)][name]
        for i, x in enumerate((instr, cyc, ld, st, mp, branches)):
            acc[i] += x

order = ['tfmt_off', 'tfmc', 'tfmb', 'tfmt']
names = {'tfmt_off': 'masks off', 'tfmc': '#408', 'tfmb': '+ belt', 'tfmt': '+ image staging'}
funcs = ['fill_through_mask', 'write_texture', 'StagingBelt', 'update_image', 'submit', 'flush']
for f in sorted({f for f, _ in data}):
    print(f'{f}: E-cores   IPC   L1D ld/ki  st/ki  mispred/kbr  mispred/ki | share of E cycles: ' + '  '.join(funcs))
    for v in order:
        if (f, v) not in data:
            continue
        a = data[(f, v)]['all']
        shares = '  '.join(f'{100 * data[(f, v)][fn][1] / a[1]:{len(fn)}.1f}' for fn in funcs)
        print(f'  {names[v]:16s} {a[0] / a[1]:4.2f}  {a[2] / a[0]:8.2f}  {a[3] / a[0]:5.2f}  {1000 * a[4] / a[5]:10.2f}  {a[4] / a[0]:10.2f}  | {shares}')
