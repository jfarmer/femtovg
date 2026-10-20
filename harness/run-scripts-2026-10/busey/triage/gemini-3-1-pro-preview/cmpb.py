import sys, numpy as np
from cmp import get
names=[a for a in sys.argv[1:] if '=' not in a and not a.startswith('b:')]
builds=[a[2:] for a in sys.argv[1:] if a.startswith('b:')] or ['mst2']
for n in names:
    row=[]
    for b in builds:
        o,r,a,sp=get(n,b); ag=a&~sp
        row.append(f'{b}: all3 {a.sum():4d} agreed {ag.sum():4d}')
    print(f'{n:22s}', ' | '.join(row))
