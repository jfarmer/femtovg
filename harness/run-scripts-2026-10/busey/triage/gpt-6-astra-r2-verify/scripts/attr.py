import numpy as np, sys, json
sys.path.insert(0,'scripts')
from red import red, L
def uc(fr,x,y):
    if fr=='hd': s=1080/1024; return ((x+.5-420)/s,(y+.5)/s)
    z=int(fr[1:]); s=200/1024
    return (((x+.5-230)/z+230-130)/s, ((y+.5-130)/z+130-30)/s)
out={}
for fr in (sys.argv[1:] or ['z2','hd']):
    o=L(f'png/mst4_v__v00_orig_{fr}.png'); fm=L(f'png/fm_v__v00_orig_{fr}.png')
    refs=[L(f'refs/{b}_v__v00_orig_{fr}.png') for b in ('chr','ff','wk')]; idr=L(f'refs/id_v__v00_orig_{fr}.png')
    ob=L(f'png/mst4_v__v01_butt_{fr}.png'); fmb=L(f'png/fm_v__v01_butt_{fr}.png')
    refsb=[L(f'refs/{b}_v__v01_butt_{fr}.png') for b in ('chr','ff','wk')]; idb=L(f'refs/id_v__v01_butt_{fr}.png')
    a,sp=red(o,refs); af,_=red(fm,refs); ab,_=red(ob,refsb); afb,_=red(fmb,refsb)
    near=np.abs(o-idr).max(2)<=20
    ys,xs=np.nonzero(a); rows=[]
    cls={}
    for y,x in zip(ys,xs):
        c=[]
        if near[y,x]: c.append('nearid')
        if not af[y,x]: c.append('fm_fix')
        if not ab[y,x]: c.append('butt_fix')
        if not afb[y,x]: c.append('fmbutt_fix')
        if sp[y,x]: c.append('spread')
        u=uc(fr,x,y)
        rows.append((int(x),int(y),round(u[0]),round(u[1]),'/'.join(c),o[y,x].tolist(),fm[y,x].tolist(),idr[y,x].tolist(),refs[0][y,x].tolist(),refs[1][y,x].tolist(),refs[2][y,x].tolist()))
    print(fr,'red',a.sum(),'fm red',af.sum(),'fm newly',(af&~a).sum(),'butt red',ab.sum(),'fm+butt red',afb.sum())
    import collections
    print(collections.Counter(r[4] for r in rows))
    for r in rows: print('  ',r)
    out[fr]=rows
json.dump(out,open('attr_%s.json'%'_'.join(out),'w'))
