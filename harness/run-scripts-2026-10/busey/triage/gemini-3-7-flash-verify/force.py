import numpy as np
from PIL import Image
import model
from model import *
L=lambda p: np.asarray(Image.open(p).convert('RGB'),dtype=np.float64)
BG=np.array([0x15,0x03,0x04],float); FG=np.array([0xf0,0xc0,0x90],float)
def cov(img): d=FG-BG; return ((img-BG)@d)/(d@d)
idr=cov(L('refs/id_t__v00_crescent_z2.png')); chr_=cov(L('refs/chr_t__v00_crescent_z2.png'))
o=cov(L('png/mst2_t__v00_crescent_z2.png'))
FGc=FG; 
def img_of(c): return BG+np.clip(c,0,1)[...,None]*(FG-BG)
wins={'L':np.s_[178:202,160:177],'R':np.s_[178:202,283:300]}
def report(name,c):
    off=np.abs(img_of(c)-img_of(idr)).max(2)>20
    s=f'{name:28s} px>20 vs area {int(off[0:260,31:429].sum()):3d}'
    for w,sl in wins.items(): s+=f' | {w}: ink/area {c[sl].sum()/idr[sl].sum():.2f} px>20 {int(off[sl].sum())}'
    print(s)
report('femtovg master (real)',o)
report('chromium',chr_)
P,C=build(CRES)
# original
E=expand(P,C); report('model',raster(E,460,260)['total'])
# forced miter at the two tips: rerun expand with patched flags
orig=model.expand
def expand_forced(P,C,force_tip_miter=True):
    E=orig(P,C)
    return E
# patch: re-implement by editing flags then rebuilding strip
def rebuild_strip(E, drop_ib_at):
    P=E['P']; n=len(P); d=np.roll(P,-1,0)-P; d=d/np.hypot(d[:,0],d[:,1])[:,None]; dm=E['dm']; fl=[set(f) for f in E['flags']]
    for i in drop_ib_at: fl[i].discard('IB')
    st=[]; lw=1.5; rw=0.5
    for i in range(n):
        p1=P[i]; dl0=orth(d[i-1]); dl1=orth(d[i])
        if 'B' in fl[i] and 'IB' in fl[i]:
            l0=p1+dl0*lw; l1=p1+dl1*lw
            st+=[(l0,0),(p1-dl0*rw,1),(l0,0),(p1-dl0*rw,1),(l1,0),(p1-dl1*rw,1),(l1,0),(p1-dl1*rw,1)]
        else: st+=[(p1+dm[i]*lw,0),(p1-dm[i]*rw,1)]
    st+=[st[0],st[1]]
    E2=dict(E); E2['strip']=st; return E2
tips=[i for i,f in enumerate(E['flags']) if 'B' in f and 'IB' in f]
print('bevel+innerbevel points:',tips,[tuple(np.round(E['P'][i],2)) for i in tips])
report('model, tips mitered',raster(rebuild_strip(E,tips),460,260)['total'])
