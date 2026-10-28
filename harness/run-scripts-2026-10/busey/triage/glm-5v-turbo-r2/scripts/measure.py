import sys, os, json, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image
from coords import S as FRS
S='/Users/matt/src/femtovg-wt/runs/busey/triage/glm-5v-turbo-r2'
L=lambda p: np.asarray(Image.open(p).convert('RGB'),dtype=np.int16)
REG=[('brow_tips',[(438,386,468,401),(556,386,586,401)]),
     ('iris',[(352,420,400,458),(624,420,672,458)]),
     ('lash_row',[(316,398,446,434),(578,398,724,434)]),
     ('mouth_up',[(416,626,452,657),(572,626,608,657)]),
     ('mouth_lo',[(440,673,467,706),(557,673,584,706)]),
     ('hair_sliver',[(822,405,845,545),(205,278,234,366),(383,28,470,78)]),
     ('ears',[(228,452,260,474),(764,452,796,474)]),
     ('sideburns',[(228,380,292,606),(732,390,796,616)]),
     ('stubble_tips',[(298,548,324,578),(696,548,724,592)])]
def cubic(p0,p1,p2,p3,n=64):
    t=np.linspace(0,1,n)[:,None]; return (1-t)**3*p0+3*(1-t)**2*t*p1+3*(1-t)*t**2*p2+t**3*p3
F=[(512,130),(620,130),(720,200),(758,340),(780,420),(785,500),(775,580),(765,660),(730,750),(680,820),(630,880),(570,910),(512,910),(454,910),(394,880),(344,820),(294,750),(259,660),(249,580),(239,500),(244,420),(266,340),(304,200),(404,130),(512,130)]
F=[np.array(p,float) for p in F]
FACE=np.concatenate([cubic(*F[i:i+4]) for i in range(0,24,3)])
def face_dist(u,v):
    return np.sqrt(((FACE[None,:,0]-u[:,None])**2+(FACE[None,:,1]-v[:,None])**2).min(1))
def regions(fr, shape):
    ox,oy,s=FRS[fr]; H,W=shape
    yy,xx=np.mgrid[0:H,0:W]; u=(xx+0.5-ox)/s; v=(yy+0.5-oy)/s
    lab=np.full(shape,-1,int)
    for i,(n,boxes) in enumerate(REG):
        for (x0,y0,x1,y1) in boxes:
            m=(u>=x0)&(u<x1)&(v>=y0)&(v<y1)&(lab<0); lab[m]=i
    return lab,u,v
NAMES=[n for n,_ in REG]+['face_edge','rest']
def stats(ours, refs, fr):
    off=[np.abs(ours-r).max(2)>20 for r in refs[:3]]; a=off[0]&off[1]&off[2]
    sp=np.zeros(a.shape,bool)
    for i in range(3):
        for j in range(i+1,3): sp|=np.abs(refs[i]-refs[j]).max(2)>20
    g=a&~sp
    lab,u,v=regions(fr,a.shape)
    ys,xs=np.nonzero(a&(lab<0))
    if len(ys):
        d=face_dist(u[ys,xs],v[ys,xs]); fe=d<3.0
        lab[ys[fe],xs[fe]]=len(REG); lab[ys[~fe],xs[~fe]]=len(REG)+1
    r={'all3':int(a.sum()),'agreed':int(g.sum())}
    if len(refs)>3:
        r['off_id']=int((np.abs(ours-refs[3]).max(2)>20).sum()); r['all3&off_id']=int((a&(np.abs(ours-refs[3]).max(2)>20)).sum())
    for i,n in enumerate(NAMES):
        m=lab==i; c=(int((a&m).sum()),int((g&m).sum()))
        if c[0]: r[n]=f'{c[0]}/{c[1]}'
    return r
def run(key, fr, ours=None, rd=f'{S}/refs', build='mst4'):
    o=L(ours or f'{S}/png/{build}_{key}_{fr}.png'); refs=[L(f'{rd}/{x}_{key}_{fr}.png') for x in ('chr','ff','wk','id')]
    return stats(o,refs,fr)
if __name__=='__main__':
    fr=sys.argv[1]; keys=sys.argv[2:] or [f['key'] for f in json.load(open(f'{S}/files.json'))]
    for k in keys:
        print(f'{k:28s}', json.dumps(run(k,fr)))
