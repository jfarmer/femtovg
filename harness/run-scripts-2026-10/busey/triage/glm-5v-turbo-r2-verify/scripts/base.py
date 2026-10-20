import sys; sys.path.insert(0,'scripts')
from red import *
for fr in ['z2','hd']:
    o=L(f'png/g00_{fr}.png'); rf=refs(fr); a,g,sp,offid=masks(o,rf)
    print(fr,'all3',a.sum(),'agreed',g.sum(),'all3&offid',(a&offid).sum(), 'frame', a.size)
    cs=comps(a, 4 if fr=='z2' else 6)
    cs.sort(key=lambda c:-len(c))
    for c in cs:
        ys=[p[0] for p in c]; xs=[p[1] for p in c]
        u0,v0=to_svg(fr,min(xs),min(ys)); u1,v1=to_svg(fr,max(xs),max(ys))
        ag=sum(g[p] for p in c); oi=sum(offid[p] for p in c)
        print(f'  n={len(c):3d} ag={ag:3d} offid={oi:3d} frame x{min(xs)}-{max(xs)} y{min(ys)}-{max(ys)}  svg ({u0:.0f},{v0:.0f})-({u1:.0f},{v1:.0f})')
