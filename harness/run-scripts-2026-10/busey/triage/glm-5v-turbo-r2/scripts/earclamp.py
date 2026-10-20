import sys; sys.path.insert(0,'scripts')
import numpy as np, femsim2 as f2, femsim as fs
def ear(dx,dy):
    s=lambda *p: tuple(v+(dx if i%2==0 else dy) for i,v in enumerate(p))
    return [('M',*s(252,465)),('C',*s(218,465,218,535,252,535)),('C',*s(278,535,285,500,272,478)),('C',*s(260,460,242,465,252,465))]
def inside(poly, px, py):
    # even-odd crossing test, vectorized over points
    x0,y0=poly[:,0],poly[:,1]; x1,y1=np.roll(x0,-1),np.roll(y0,-1)
    c=np.zeros(px.shape,bool)
    for a,b,cc,d in zip(x0,y0,x1,y1):
        m=((b>py)!=(d>py)); xi=a+(py-b)*(cc-a)/(d-b+1e-30); c^=m&(px<xi)
    return c
def exact(segs, n=8):
    pts=[]; t=np.linspace(0,1,300)[1:]
    for sg in segs:
        if sg[0]=='M': pts.append(fs.dev(sg[1],sg[2]))
        else:
            p0=np.array(pts[-1]); c1=np.array(fs.dev(*sg[1:3])); c2=np.array(fs.dev(*sg[3:5])); p3=np.array(fs.dev(*sg[5:7]))
            for tt in t: u=1-tt; pts.append(tuple(u**3*p0+3*u*u*tt*c1+3*u*tt*tt*c2+tt**3*p3))
    poly=np.array(pts); img=np.zeros((fs.H,fs.W)); g=(np.arange(n)+0.5)/n
    ys,xs=np.mgrid[100:140,105:150]
    acc=np.zeros(xs.shape)
    for a in g:
        for b in g: acc+=inside(poly,xs+a,ys+b)
    img[100:140,105:150]=acc/(n*n); return img
src=open('scripts/femsim2.py').read().replace('if r2 > 1e-6: dm[i] *= min(1/r2, 600.0)','if r2 > 1e-6: dm[i] *= min(1/r2, 600.0, CLAMP/np.sqrt(r2))')
ns={'__name__':'femsim2c'}; exec(compile(src,'femsim2c','exec'),ns); ns['CLAMP']=2.4
thr=20/216; B=(slice(100,140),slice(105,150))
for dx,dy in ((0,0),(0.64,0),(0,0.64),(1.28,0.96),(0.32,1.6)):
    e=ear(dx,dy); ex=exact(e); row=[]
    for name,fn in (('master',lambda: f2.render([e],test='both')),('either',lambda: f2.render([e],test='either')),('clamp2.4',lambda: ns['render']([e],test='both'))):
        img=fn(); row.append(f'{name}: ink {img[B].sum():6.2f} off>20 {int((np.abs(img[B]-ex[B])>thr).sum()):2d}')
    print(f'shift({dx},{dy}) exact {ex[B].sum():6.2f} | '+' | '.join(row))
