import sys, numpy as np
sys.path.insert(0,'scripts')
from red import L, masks, to_svg
from measure import label, NAMES
key, fr, build = sys.argv[1], sys.argv[2], (sys.argv[3] if len(sys.argv)>3 else 'mst4')
want=sys.argv[4:] 
o=L(f'png/{build}_{key}_{fr}.png'); rf=[L(f'refs/{x}_{key}_{fr}.png') for x in ('chr','ff','wk','id')]
a,g,sp,offid=masks(o,rf); ys,xs,lab=label(fr,a.shape,a)
for y,x,l in zip(ys,xs,lab):
    if want and NAMES[l] not in want: continue
    u,v=to_svg(fr,x,y)
    print(f'{NAMES[l]:10s} f({x},{y}) svg({u:.1f},{v:.1f}) fem {o[y,x].tolist()} chr {rf[0][y,x].tolist()} ff {rf[1][y,x].tolist()} wk {rf[2][y,x].tolist()} id {rf[3][y,x].tolist()} ag={int(g[y,x])}')
