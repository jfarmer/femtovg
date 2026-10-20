import sys, json, numpy as np
sys.path.insert(0,'scripts')
from red import L, S, masks
REG=[('irisL',[(352,420,400,458)]),('irisR',[(624,420,672,458)]),
     ('lashes',[(314,394,448,426),(594,394,728,426)]),
     ('brows',[(436,384,470,402),(554,384,588,402)]),
     ('mouth',[(412,628,462,708),(562,628,612,708)]),
     ('sliverR',[(822,405,845,545)]),('sideburns',[(226,375,292,606),(732,385,798,616)]),
     ('ears',[(226,450,262,476),(762,450,798,476)]),('stubble',[(296,546,326,580),(694,546,726,594)])]
def cubic(p0,p1,p2,p3,n=200):
    t=np.linspace(0,1,n)[:,None]; return (1-t)**3*p0+3*(1-t)**2*t*p1+3*(1-t)*t**2*p2+t**3*p3
F=[(512,130),(620,130),(720,200),(758,340),(780,420),(785,500),(775,580),(765,660),(730,750),(680,820),(630,880),(570,910),(512,910),(454,910),(394,880),(344,820),(294,750),(259,660),(249,580),(239,500),(244,420),(266,340),(304,200),(404,130),(512,130)]
F=[np.array(p,float) for p in F]; FACE=np.concatenate([cubic(*F[i:i+4]) for i in range(0,24,3)])
NAMES=[n for n,_ in REG]+['face_edge','rest']
def label(fr, shape, m):
    ox,oy,s=S[fr]; ys,xs=np.nonzero(m); lab=np.full(len(ys),-1)
    u=(xs+0.5-ox)/s; v=(ys+0.5-oy)/s
    for i,(n,boxes) in enumerate(REG):
        for (x0,y0,x1,y1) in boxes:
            k=(u>=x0)&(u<x1)&(v>=y0)&(v<y1)&(lab<0); lab[k]=i
    r=lab<0
    if r.any():
        d=np.sqrt(((FACE[None,:,0]-u[r][:,None])**2+(FACE[None,:,1]-v[r][:,None])**2).min(1))
        ll=np.where(d<3.0,len(REG),len(REG)+1); lab[r]=ll
    return ys,xs,lab
def run(key, fr, build='mst4', rd='refs', pd='png'):
    o=L(f'{pd}/{build}_{key}_{fr}.png'); rf=[L(f'{rd}/{x}_{key}_{fr}.png') for x in ('chr','ff','wk','id')]
    a,g,sp,offid=masks(o,rf)
    ys,xs,lab=label(fr,a.shape,a)
    out={'all3':int(a.sum()),'agreed':int(g.sum()),'&offid':int((a&offid).sum())}
    for i,n in enumerate(NAMES):
        k=lab==i
        if k.any(): out[n]=f'{int(k.sum())}/{int(offid[ys[k],xs[k]].sum())}'
    return out
if __name__=='__main__':
    fr=sys.argv[1]; build=sys.argv[2] if len(sys.argv)>2 else 'mst4'
    keys=sys.argv[3:] or [f['key'] for f in json.load(open('files.json'))]
    for k in keys:
        try: print(f'{k:28s}', json.dumps(run(k,fr,build)))
        except FileNotFoundError as e: pass
