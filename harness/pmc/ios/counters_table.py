#!/usr/bin/env python3
"""counters_table.py DIR...: frame-loop counters of counters2.sh (DIR/pmcf-c<i>-<variant>.txt), pooled per variant:
efficiency-core IPC, L1D load and store misses and branch mispredicts a thousand instructions, and the share of the
cycles under the mask path's functions."""
import collections, glob, re, sys
num = r'([\d.]+)'
line_re = re.compile(r'^\s*E(?:-cores, all| (\S+))\s+instr\s+' + num + r' M\s+cycles\s+' + num + r' M.*?L1D ld miss\s+' + num +
                     r' k.*?st miss\s+' + num + r' k.*?mispred\s+' + num + r' k')
funcs = ['fill_through_mask', 'Coverage::resolve', 'upload_fill_masks', 'update_image', 'StagingBelt']
for d in sys.argv[1:]:
    data = collections.defaultdict(lambda: collections.defaultdict(lambda: [0.0] * 5))
    for path in sorted(glob.glob(f'{d}/pmcf-c*.txt')):
        variant = path.rsplit('-', 1)[1][:-4]
        for line in open(path):
            m = line_re.match(line)
            if m:
                for i, x in enumerate(map(float, m.groups()[1:])):
                    data[variant][m.group(1) or 'all'][i] += x
    print(f'{d}: E-cores        IPC  L1D ld/ki  st/ki  mispred/ki | ' + '  '.join(funcs))
    for v, label in (('offpp', 'masks off'), ('pp', 'masks on')):
        if v not in data:
            continue
        ins, cyc, ld, st, mp = data[v]['all']
        shares = '  '.join(f'{100 * data[v][fn][1] / cyc:{len(fn)}.1f}' for fn in funcs)
        print(f'  {label:12s} {ins / cyc:5.2f}  {ld / ins:8.2f}  {st / ins:5.2f}  {mp / ins:9.2f}  | {shares}')
