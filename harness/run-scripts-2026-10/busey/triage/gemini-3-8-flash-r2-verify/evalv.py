import sys; sys.path.insert(0, '.')
from boxes import *
names = sys.argv[1:]
for n in names:
    for fr in ('z2', 'hd'):
        R = refs(n, fr); o = ours(n, fr); a, ag, sp = red(o, R)
        print(f'{n:22s} {fr} red {a.sum():4d} agreed {ag.sum():4d} offid {offid(o,R).sum():4d} spread {sp.sum():5d}', counts(a, fr))
