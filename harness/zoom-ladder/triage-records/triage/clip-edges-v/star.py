import sys, numpy as np
sys.path.insert(0,'.')
from cmp import *
key='wpt22__20-clippath-unions-and-masks__resvg-clippath-multiple-children'
P=np.array([(100,15),(150,175),(20,75),(180,75),(50,175)],float)
inner=[]
# inner vertices: intersections of the star's edges
def inter(p1,p2,p3,p4):
    d=(p2-p1); e=(p4-p3); den=d[0]*e[1]-d[1]*e[0]
    if abs(den)<1e-12: return None
    t=((p3-p1)[0]*e[1]-(p3-p1)[1]*e[0])/den; u=((p3-p1)[0]*d[1]-(p3-p1)[1]*d[0])/den
    if 1e-9<t<1-1e-9 and 1e-9<u<1-1e-9: return p1+t*d
E=[(P[i],P[(i+1)%5]) for i in range(5)]
for i in range(5):
    for j in range(i+1,5):
        q=inter(*E[i],*E[j])
        if q is not None: inner.append(q)
inner=np.array(inner)
def evenodd_cov(z,ss=32):
    V=np.stack([230+z*(P[:,0]-100),130+z*(P[:,1]-100)],1)
    x0,y0=np.floor(V.min(0)).astype(int)-1; x1,y1=np.ceil(V.max(0)).astype(int)+1
    x0=max(x0,0); y0=max(y0,0); x1=min(x1,460); y1=min(y1,260)
    cov=np.zeros((260,460))
    o=(np.arange(ss)+0.5)/ss
    gx,gy=np.meshgrid(np.arange(x0,x1)[:,None]+o[None,:], np.arange(y0,y1)[:,None]+o[None,:])
    gx=gx.reshape(-1); gy=gy.reshape(-1)
    # proper grid
    X=(np.arange(x0,x1)[:,None]+o[None,:]).reshape(-1); Y=(np.arange(y0,y1)[:,None]+o[None,:]).reshape(-1)
    XX,YY=np.meshgrid(X,Y)
    wind=np.zeros(XX.shape,int)
    for i in range(5):
        a=V[i]; b=V[(i+1)%5]
        up=(a[1]<=YY)&(b[1]>YY); dn=(b[1]<=YY)&(a[1]>YY)
        xc=a[0]+(YY-a[1])*(b[0]-a[0])/(b[1]-a[1]+1e-30)
        wind+=np.where(up&(xc>XX),1,0)-np.where(dn&(xc>XX),1,0)
    inside=(wind%2==1)
    # union circle r=10 at (100,100)
    cxy=(230,130); r=10*z
    inside|=((XX-cxy[0])**2+(YY-cxy[1])**2<r*r)
    c=inside.reshape(y1-y0,ss,x1-x0,ss).mean((1,3))
    cov[y0:y1,x0:x1]=c
    return cov,(x0,y0,x1,y1),V,np.stack([230+z*(inner[:,0]-100),130+z*(inner[:,1]-100)],1)
if __name__=='__main__':
  for z in [1,1.25,1.5,1.75,2,3,4]:
    a,(x0,y0,x1,y1),V,IV=evenodd_cov(z)
    ex=255*(1-a)
    roi=np.zeros((260,460),bool); roi[y0+2:y1-2,x0+2:x1-2]=True
    # exclude the frame stroke region: frame at svg x=1..199 -> keep away
    fx0=230+z*(1-100)+2; fx1=230+z*(199-100)-2; fy0=130+z*(1-100)+2; fy1=130+z*(199-100)-2
    yy,xx=np.mgrid[0:260,0:460]
    roi&=(xx>fx0)&(xx<fx1)&(yy>fy0)&(yy<fy1)
    near=np.zeros((260,460),bool)
    for q in IV: near|=(np.hypot(xx+0.5-q[0],yy+0.5-q[1])<2.5)
    out=[]
    for n,im in [('mst',fem(key,z)),('nc',load(f'png/r16/starnc/{z}.png')),('chr',ref('chr',key,z)),('wk',ref('wk',key,z))]:
        d=np.abs(im[...,0]-ex)*roi
        out.append(f'{n}:{int((d>8).sum())}({d.max():.0f}) atvtx:{int(((d>8)&near).sum())}(max {d[near].max():.0f})')
    f=fem(key,z); w=ref('wk',key,z); nc=load(f'png/r16/starnc/{z}.png')
    bad=(np.abs(f[...,:3]-w[...,:3]).max(-1)>8); badnc=(np.abs(nc[...,:3]-w[...,:3]).max(-1)>8)
    print(z,' '.join(out),'| mst-vs-wk',int(bad.sum()),'in roi',int((bad&roi).sum()),'at inner vtx',int((bad&near).sum()),'| nc-vs-wk',int(badnc.sum()),'at vtx',int((badnc&near).sum()))
