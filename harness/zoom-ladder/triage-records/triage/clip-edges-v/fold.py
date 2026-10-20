import sys, numpy as np
sys.path.insert(0,'.')
from cmp import *
from star import P, inner, key
def wind_frac(z, px, py, ss=64):
    V=np.stack([230+z*(P[:,0]-100),130+z*(P[:,1]-100)],1)
    o=(np.arange(ss)+0.5)/ss
    XX,YY=np.meshgrid(px+o,py+o)
    w=np.zeros(XX.shape,int)
    for i in range(5):
        a=V[i]; b=V[(i+1)%5]
        up=(a[1]<=YY)&(b[1]>YY); dn=(b[1]<=YY)&(a[1]>YY)
        xc=a[0]+(YY-a[1])*(b[0]-a[0])/(b[1]-a[1]+1e-30)
        w+=np.where(up&(xc>XX),1,0)-np.where(dn&(xc>XX),1,0)
    w=np.abs(w)
    return [(w==k).mean() for k in range(3)]
for z in [1.25,1.75]:
    f=fem(key,z); wk=ref('wk',key,z)
    IV=np.stack([230+z*(inner[:,0]-100),130+z*(inner[:,1]-100)],1)
    for q in IV:
        for py in range(int(q[1])-1,int(q[1])+2):
            for px in range(int(q[0])-1,int(q[0])+2):
                a0,a1,a2=wind_frac(z,px,py)
                if a2<0.01 or a1<0.01: continue
                s=a1+2*a2; fold=s%2; fold=2-fold if fold>1 else fold
                print(f'z{z} px({px},{py}) a1={a1:.3f} a2={a2:.3f} exact={255*a1:.0f} fold(a1+2a2)={255*fold:.0f} femtovg={255-f[py,px,0]} wk={255-wk[py,px,0]}')
