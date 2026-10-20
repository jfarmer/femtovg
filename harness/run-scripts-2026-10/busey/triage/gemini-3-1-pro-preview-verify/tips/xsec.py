import sys, re, numpy as np
sys.path.insert(0,'.')
import sim
from PIL import Image
L=lambda p: np.asarray(Image.open(p).convert('RGB'),dtype=np.float64)
name=sys.argv[1]; S=sim.S
d=re.search(r'<path d="([^"]*)"',open(f'{S}/svg/{name}.svg').read()).group(1).replace(',',' ')
V,kind,dr,tv=sim.capture(d)
f0,fn,s0,sn=dr[0]
st=np.zeros((sim.H,sim.W),int)
for i in range(f0+1,f0+fn-1):
    r=sim.raster_tri(V[f0],V[i],V[i+1])
    if r is None: continue
    (y0,y1,x0,x1),m,area,_=r; st[y0:y1,x0:x1]+=np.where(m,1 if area>0 else -1,0)
A=np.zeros((sim.H,sim.W)); B=np.zeros((sim.H,sim.W)); half=sn//2
for k in range(sn-2):
    a,b,c=V[s0+k],V[s0+k+1],V[s0+k+2]
    r=sim.raster_tri(a,b,c)
    if r is None: continue
    (y0,y1,x0,x1),m,area,(w0,w1,w2)=r
    if area*(1 if k%2==0 else -1)>0: continue
    u=w0*a[2]+w1*b[2]+w2*c[2]; v=w0*a[3]+w1*b[3]+w2*c[3]
    al=np.where(m&(st[y0:y1,x0:x1]==0),np.clip(np.minimum(1,(1-np.abs(u*2-1)))*np.minimum(1,v),0,1),0)
    side = A if (8<=k<half) else B   # strip after the left tip's bevel = first curve; the rest = second curve (and bevels)
    side[y0:y1,x0:x1]=1-(1-side[y0:y1,x0:x1])*(1-al)
area=(255-L(f'{S}/refs/id_t__{name}_z2.png').mean(2))/255
fv=(255-L(f'{S}/png/mst2_t__{name}_z2.png').mean(2))/255
x0,y0=int(sys.argv[2]),int(sys.argv[3])
print('pixel      area   side1  side2  library  (stencil)')
for yy in range(y0-4,y0+5):
    xx=x0
    for xx in range(x0-1,x0+2):
        if area[yy,xx]>0.01 or fv[yy,xx]>0.01:
            print(f'({xx},{yy})  {area[yy,xx]:.2f}   {A[yy,xx]:.2f}   {B[yy,xx]:.2f}   {fv[yy,xx]:.2f}   {st[yy,xx]}')
