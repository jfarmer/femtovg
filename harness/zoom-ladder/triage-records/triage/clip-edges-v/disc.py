import numpy as np
def disc_cov(W,H,cx,cy,r,n=512):
    # exact-ish area of disc in each pixel: integrate column chord over n x-samples per pixel
    cov=np.zeros((H,W))
    x0=int(np.floor(cx-r))-1; x1=int(np.ceil(cx+r))+1
    for px in range(max(0,x0),min(W,x1)):
        xs=px+(np.arange(n)+0.5)/n
        h2=r*r-(xs-cx)**2
        m=h2>0
        if not m.any(): continue
        h=np.sqrt(np.where(m,h2,0))
        top=cy-h; bot=cy+h
        y0=int(np.floor(cy-r))-1; y1=int(np.ceil(cy+r))+1
        for py in range(max(0,y0),min(H,y1)):
            seg=np.clip(np.minimum(py+1,bot)-np.maximum(py,top),0,None)*m
            cov[py,px]=seg.mean()
    return cov
