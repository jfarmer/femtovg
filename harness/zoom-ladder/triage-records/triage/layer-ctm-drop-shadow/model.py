"""Model of the browsers' filter path for this file at a zoom: rasterize each filtered element in a
layer aligned with its user space at the CTM's scale only (Skia decomposeCTM / Firefox filter space /
WebKit filterScale), apply the drop shadow's offset there (bilinear, Skia kLinear) and draw the layer to
the device with the remaining rotate(90) + translation, bilinear. Prints the max/count vs each frame."""
import sys
import numpy as np
from PIL import Image
K="wpt22__19-filter-subregions-and-offcanvas__wpt-2d-layer-ctm-drop-shadow-filter"
R='/Users/matt/src/femtovg-wt/runs/zoom'
z=float(sys.argv[1]); tag=sys.argv[2]; MODE=sys.argv[3] if len(sys.argv)>3 else 'two-step'; CROP='crop' in MODE
s=2*z                                  # CTM scale (fit 1 * scale(2) * zoom)
ox=230+(130+30-230)*z; oy=130+(30+90-130)*z   # device position of the group's user origin
def ov(a0,a1,n,off):                   # 1D overlap of [a0,a1] with pixels [i,i+1], i = -off..n-off-1
    i=np.arange(n)-off
    return np.clip(np.minimum(a1,i+1)-np.maximum(a0,i),0,1)
N=400; OFF=200                         # layer pixels i in [-200,200)
def rect_cov(x0,x1,y0,y1):             # user rect -> layer coverage (layer u = s*x, v = s*y)
    return np.outer(ov(s*y0,s*y1,N,OFF), ov(s*x0,s*x1,N,OFF))   # [v,u]
def bilinear(img,u,v):                 # sample img[v,u] (texel centres at i+0.5 in layer coords)
    fu=u-0.5+OFF; fv=v-0.5+OFF
    u0=np.floor(fu).astype(int); v0=np.floor(fv).astype(int); au=fu-u0; av=fv-v0
    def g(a,b): 
        ok=(a>=0)&(a<N)&(b>=0)&(b<N)
        out=np.zeros(a.shape+img.shape[2:]); out[ok]=img[b[ok],a[ok]]; return out
    if img.ndim==3: au=au[...,None]; av=av[...,None]
    return (g(u0,v0)*(1-au)*(1-av)+g(u0+1,v0)*au*(1-av)+g(u0,v0+1)*(1-au)*av+g(u0+1,v0+1)*au*av)
grey=np.array([128,128,128])/255.
els=[((-30,30,-5,5),(5,-5),np.array([1,0,0.])),((-30,30,-25,-15),(5,-5),np.array([0,128/255.,0])),((-30,30,-45,-35),(2.5,-2.5),np.array([0,0,1.]))]
H,W=260,460
Y,X=np.mgrid[0:H,0:W]
# device pixel centre -> layer coords: device_x = ox - v, device_y = oy + u (rotate(90))
U=(Y+0.5)-oy; V=ox-(X+0.5)
dev=np.ones((H,W,3))
for (x0,x1,y0,y1),(dx,dy),col in els:
    a=rect_cov(x0,x1,y0,y1)
    if MODE.startswith('merged'):
        # Skia: the offset (kLinear) is folded into the layer-to-device draw - one bilinear sample -
        # and the merge draws each child independently (SkDropShadowImageFilter.cpp)
        sh=bilinear(a,U-s*dx,V-s*dy)[...,None]
        dev=col[None,None]*sh+dev*(1-sh)
        src=bilinear(a,U,V)[...,None]
        dev=grey[None,None]*src+dev*(1-src)
    else:
        uu,vv=np.meshgrid(np.arange(N)-OFF+0.5,np.arange(N)-OFF+0.5)
        sh=bilinear(a,uu-s*dx,vv-s*dy)     # shadow: alpha offset by (s*dx, s*dy) layer px, bilinear
        if CROP:
            # the filter region (x/y -50%, 200% of the bbox) crops the result in layer space
            cr=rect_cov(x0-(x1-x0)/2,x1+(x1-x0)/2,y0-(y1-y0)/2,y1+(y1-y0)/2)
            sh=sh*((cr>1e-4).astype(float) if 'roundout' in MODE else cr)
        prem=grey[None,None]*a[...,None]+col[None,None]*(sh*(1-a))[...,None]
        alpha=a+sh*(1-a)
        layer=np.concatenate([prem,alpha[...,None]],-1)
        d=bilinear(layer,U,V)
        dev=d[...,:3]+dev*(1-d[...,3:4])
m=np.round(dev*255)
Image.fromarray(m.astype(np.uint8)).save(f'model_{MODE}_{tag}.png')
for b in ['chr','ff','wk']:
    try: r=np.asarray(Image.open(f'{R}/fresh/refs/{b}_{K}_{tag}.png').convert('RGB')).astype(float)
    except Exception: continue
    d=np.abs(m-r).max(-1)
    print(tag,MODE,b,'model vs browser: max',int(d.max()),' px>8:',int((d>8).sum()),' px>2:',int((d>2).sum()))
f=np.asarray(Image.open(f'{R}/png/zl_zm_svg/{K}/fresh_{tag}.png').convert('RGB')).astype(float)
d=np.abs(m-f).max(-1); print(tag,'fem model vs femtovg: px>8',int((d>8).sum()))
