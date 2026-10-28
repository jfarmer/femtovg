import sys, numpy as np
sys.path.insert(0,'.')
from cmp import *
key='corpus__clip-probes__evenodd-clip-thin-ring'
yy,xx=np.mgrid[0:260,0:460]+0.5
extra=dict(a.split('=') for a in sys.argv[1:])
for z in [1.5,2,3]:
    cx=230; cy=130-20*z; ro=40*5/3*z; ri=39.5*5/3*z
    rr=np.hypot(xx-cx,yy-cy); th=np.degrees(np.arctan2(yy-cy,xx-cx))%90
    band=(rr>ri-3)&(rr<ro+3)
    imgs={'fem':fem(key,z)}
    for b in ('chr','ff','wk'): imgs[b]=ref(b,key,z)
    for k,p in extra.items():
        imgs[k]=load(p.replace('Z',TAG[z]))
    bins=[0,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90]
    print('zoom',z,'expected mean r',round((ro+ri)/2,3),'angle bins', bins[:-1])
    for n,im in imgs.items():
        if im is None: continue
        a=1-im[...,0]/255.0
        # restrict to visible frame region (top may be cut)
        row=[]
        for i in range(len(bins)-1):
            m=band&(th>=bins[i])&(th<bins[i+1])
            w=a[m]; 
            row.append((w*rr[m]).sum()/w.sum()-(ro+ri)/2)
        ink=[]
        print(f'{n:>5}', ' '.join(f'{v:+.3f}' for v in row))
