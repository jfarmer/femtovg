#!/usr/bin/env python3
"""A/B of the fbench CSVs: per workload, E-core instructions and cycles summed, min over rounds per file."""
import csv, glob, sys
def load(pat):
    by = {}
    for f in glob.glob(pat):
        for r in csv.DictReader(open(f)):
            k = r['file']; v = (int(r['instr_e']) + int(r['instr_p']), int(r['cycles_e']) + int(r['cycles_p']), r['checksum'])
            by.setdefault(k, []).append(v)
    return {k: (min(x[0] for x in v), min(x[1] for x in v), v[0][2]) for k, v in by.items()}
for name, pa, pb in [('rotated set, 1x', 'ab_rot_base_s1_r*.csv', 'ab_rot_both_s1_r*.csv'),
                     ('rotated set, 2x', 'ab_rot_base_s2_r*.csv', 'ab_rot_both_s2_r*.csv'),
                     ('all filter tests, 1.5x', 'ab_filt_base_r*.csv', 'ab_filt_both_r*.csv')]:
    a, b = load(pa), load(pb)
    ks = sorted(set(a) & set(b))
    ia, ib = sum(a[k][0] for k in ks), sum(b[k][0] for k in ks)
    ca, cb = sum(a[k][1] for k in ks), sum(b[k][1] for k in ks)
    same = sum(a[k][2] == b[k][2] for k in ks)
    print(f'{name:24} files {len(ks):4} (identical output {same:4})  instructions {ia/1e9:8.3f} G -> {ib/1e9:8.3f} G ({(ib/ia-1)*100:+.2f} %)  cycles {ca/1e9:8.3f} G -> {cb/1e9:8.3f} G ({(cb/ca-1)*100:+.2f} %)  IPC {ia/ca:.2f} -> {ib/cb:.2f}')
    moved = sorted(ks, key=lambda k: -abs(b[k][0] - a[k][0]))[:6]
    for k in moved:
        if a[k][0] != b[k][0]:
            print(f'     {k.split("/")[-1][:60]:60} instr {(b[k][0]/a[k][0]-1)*100:+6.2f} %  cycles {(b[k][1]/a[k][1]-1)*100:+6.2f} %')
