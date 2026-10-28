import numpy as np
from PIL import Image
V='/Users/matt/src/femtovg-wt/runs/busey/triage/gpt-5-6-terra-pro-verify'
L=lambda p: np.asarray(Image.open(p).convert('RGB'),dtype=np.float64)
srcs={'fv_single':(f'{V}/r/sol_white_s.png',f'{V}/r/sol_black_s.png'),
      'fv_merge':(f'{V}/r/sol_white_m.png',f'{V}/r/sol_black_m.png')}
for b,nm in (('chr','chromium'),('ff','firefox'),('wk','webkit')):
    srcs[nm]=(f'{V}/refs/{b}_t__sol_white_z2.png',f'{V}/refs/{b}_t__sol_black_z2.png')
# mask: pixels where shadow alone shows: in the black-bg chromium frame, R channel ~0 (no face) and white frame has A in [0.3,0.75]
cw,cb=[L(p) for p in srcs['chromium']]
A_c=1-cw[...,0]/255
mask=(cb[...,0]<=1)&(A_c>0.3)&(A_c<0.75)
print('pixels',mask.sum())
for nm,(w,bk) in srcs.items():
    w,bk=L(w),L(bk)
    A=1-w[...,0]/255
    G=bk[...,1][mask]/A[mask]; B=bk[...,2][mask]/A[mask]
    # consistency: white frame G = 255(1-A)+C*A
    Gw=(w[...,1][mask]-255*(1-A[mask]))/A[mask]
    print(f'{nm:10s} A mean {A[mask].mean():.3f}  C from black bg G,B = {np.median(G):5.1f},{np.median(B):5.1f}   C_g from white bg {np.median(Gw):5.1f}')
