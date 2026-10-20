import json, os, numpy as np
from PIL import Image
H=os.path.expanduser('~'); R=f'{H}/src/femtovg-wt/runs/zoom'
d=json.load(open(f'{R}/triage/clusters_compact.json'))['thin-frame-stroke-fractional']
fr={1:'z1',1.25:'z125',1.5:'z15',1.75:'z175',2:'z2',3:'z3',4:'z4',0.75:'z075',0.5:'z05',0.33:'z033',0.25:'z025'}
def band(z):
    yy,xx=np.mgrid[0:260,0:460]+0.5
    X=lambda x:230+(x-230)*z; Y=lambda y:130+(y-130)*z
    l,r,t,b=X(131),X(329),Y(31),Y(229)
    m=np.zeros((260,460),bool); e=1.6
    inx=(xx>=l-e)&(xx<=r+e); iny=(yy>=t-e)&(yy<=b+e)
    m|=(np.abs(yy-t)<=e)&inx; m|=(np.abs(yy-b)<=e)&inx; m|=(np.abs(xx-l)<=e)&iny; m|=(np.abs(xx-r)<=e)&iny
    return m
def ld(p):
    return np.asarray(Image.open(p).convert('RGB'),dtype=int) if os.path.exists(p) else None
def n8(a,b,m): 
    if a is None or b is None: return None
    dd=(np.abs(a-b).max(axis=2)>8); return int((dd&m).sum()), int((dd&~m).sum())
for e in d:
    k=e['key']
    for bz in e['bad']:
        z=bz[0]; f=fr[z]
        fv=ld(f'{R}/png/zl_zm_svg/{k}/fresh_{f}.png') if z!=1 else ld(f'{R}/png/zl_zm_svg/{k}/00.png')
        refs={t:ld(f'{R}/fresh/refs/{t}_{k}_{f}.png') for t in ['chr','ff','wk']}
        m=band(z)
        out=[f'{t}:{n8(fv,v,m)}' for t,v in refs.items()]
        out+= [f'wk-chr:{n8(refs["wk"],refs["chr"],m)}', f'wk-ff:{n8(refs["wk"],refs["ff"],m)}', f'chr-ff:{n8(refs["chr"],refs["ff"],m)}']
        print(f'{k[-45:]:45} z{z:<5}', '(band,rest)', ' '.join(out))
