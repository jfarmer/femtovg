import numpy as np
from PIL import Image
try:
    from scipy.ndimage import gaussian_filter, shift
except ImportError:
    gaussian_filter=None
L=lambda p: np.asarray(Image.open(p).convert('RGB'),dtype=np.float64)
B=np.array([0x1e,0x2b,0x38],float); Lc=np.array([252,238,179],float)
def lin(v):
    v=v/255; return np.where(v<=0.04045,v/12.92,((v+0.055)/1.055)**2.4)
def srgb(c):
    c=np.clip(c,0,1); return 255*np.where(c<=0.0031308,c*12.92,1.055*c**(1/2.4)-0.055)
res={}
for b,src in [('chr','refs/chr'),('ff','refs/ff'),('wk','refs/wk'),('fem','png/mst2')]:
    f=L(f'{src}_t__v_cov0_z2.png')[...,0]/255
    sh=L(f'{src}_t__v_shadow_z2.png')
    a_s=np.clip(1-sh[...,2]/B[2],0,1)  # from the blue channel
    # analytic shadow from coverage, for a check
    if gaussian_filter is not None:
        s=0.390625*2/2  # placeholder
    al=f+(1-f)*a_s
    srgbm=f[...,None]*Lc+((1-f)*(1-a_s))[...,None]*B
    with np.errstate(invalid='ignore',divide='ignore'):
        c=np.where(al[...,None]>0, f[...,None]*lin(Lc)/al[...,None],0)
    linm=al[...,None]*srgb(c)+(1-al)[...,None]*B
    # 8-bit linear intermediate: quantise premultiplied linear color + alpha to 8 bits
    pl=np.round(f[...,None]*lin(Lc)*255)/255; a8=np.round(al*255)/255
    with np.errstate(invalid='ignore',divide='ignore'):
        c8=np.where(a8[...,None]>0,pl/a8[...,None],0)
    linm8=a8[...,None]*srgb(c8)+(1-a8)[...,None]*B
    res[b]=(f,a_s,srgbm,linm,linm8)
np.save('model_res.npy',np.array([0]))
meas={'chr':L('refs/chr_t__v_lin_z2.png'),'ff':L('refs/ff_t__v_lin_z2.png'),'wk':L('refs/wk_t__v_lin_z2.png'),
      'fem_single':L('png/mst2_t__v_lin_z2.png'),'fem_r4a':L('png/r4a_lin_v_lin.png'),
      'chr_srgbcif':L('refs/chr_t__v_srgb_z2.png'),'ff_srgbcif':L('refs/ff_t__v_srgb_z2.png'),'wk_srgbcif':L('refs/wk_t__v_srgb_z2.png')}
# mask: edge pixels (partial coverage) with real shadow beneath
for who,mkey in [('chr','chr'),('ff','ff'),('wk','wk'),('fem','fem_single'),('fem','fem_r4a'),('chr','chr_srgbcif'),('ff','ff_srgbcif'),('wk','wk_srgbcif')]:
    f,a_s,sm,lm,lm8=res[who]; m=meas[mkey]
    msk=(f>0.1)&(f<0.9)&(a_s>0.15)
    e=lambda x: np.abs(x-m)[msk].mean()
    print(f'{mkey:12s} inputs from {who:3s} n={msk.sum():4d}  MAE vs sRGB-merge model {e(sm):5.2f}  vs linear-merge model {e(lm):5.2f}  (8-bit lin {e(lm8):5.2f})')
