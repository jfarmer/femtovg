import numpy as np, sys
def clip(poly, k, v, keep_ge):
    out=[]
    n=len(poly)
    for i in range(n):
        a=poly[i]; b=poly[(i+1)%n]
        ina = a[k]>=v if keep_ge else a[k]<=v
        inb = b[k]>=v if keep_ge else b[k]<=v
        if ina: out.append(a)
        if ina!=inb:
            t=(v-a[k])/(b[k]-a[k])
            out.append((a[0]+t*(b[0]-a[0]), a[1]+t*(b[1]-a[1])))
    return out
def parea(p):
    s=0
    for i in range(len(p)):
        x0,y0=p[i]; x1,y1=p[(i+1)%len(p)]
        s+=x0*y1-x1*y0
    return abs(s)/2
def coverage(tri, W=460, H=260):
    cov=np.zeros((H,W))
    xs=[p[0] for p in tri]; ys=[p[1] for p in tri]
    for y in range(max(0,int(np.floor(min(ys)))), min(H,int(np.ceil(max(ys))))):
        for x in range(max(0,int(np.floor(min(xs)))), min(W,int(np.ceil(max(xs))))):
            p=tri
            p=clip(p,0,x,True)
            if p: p=clip(p,0,x+1,False)
            if p: p=clip(p,1,y,True)
            if p: p=clip(p,1,y+1,False)
            if len(p)>=3: cov[y,x]=parea(p)
    return cov
def tri_at(z):
    # svg (20,100),(180,100),(100,101) in a 200 box at (130,30), fit 1, zoom about (230,130)
    pts=[(20,100),(180,100),(100,101)]
    return [(230+z*(130+x-230), 130+z*(30+y-130)) for x,y in pts]
def image(z):
    a=coverage(tri_at(z))
    g=np.array([0,128,0.]); w=np.array([255,255,255.])
    return w*(1-a[...,None]) + g*a[...,None], a
if __name__=='__main__':
    from PIL import Image
    for z in map(float, sys.argv[1:]):
        img,a=image(z)
        np.save(f'exp/area_cov_z{z:g}.npy', a)
        Image.fromarray(np.round(img).astype(np.uint8)).save(f'exp/myarea_z{z:g}.png')
        print(z, tri_at(z), a.sum())
