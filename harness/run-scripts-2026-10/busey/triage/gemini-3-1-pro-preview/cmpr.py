import sys
from cmp import get, region
b=sys.argv[1]; boxes={k:[int(t) for t in v.split(',')] for k,v in (a.split('=') for a in sys.argv[2:] if '=' in a)}
for n in [a for a in sys.argv[2:] if '=' not in a]:
    o,r,a,sp=get(n,b); ag=a&~sp
    print(f'{n:22s} all3 {a.sum():4d} agreed {ag.sum():4d}', ' '.join(f'{k}:{region(ag,v)}' for k,v in boxes.items()))
