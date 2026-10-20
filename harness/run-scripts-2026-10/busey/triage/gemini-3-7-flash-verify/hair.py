import numpy as np, re
from PIL import Image
from model import *
L=lambda p: np.asarray(Image.open(p).convert('RGB'),dtype=np.float64)
BG=np.array([0x15,0x03,0x04],float); FG=np.array([0xf0,0xc0,0x90],float)
def cov(img): d=FG-BG; return ((img-BG)@d)/(d@d)
def img_of(c): return BG+np.clip(c,0,1)[...,None]*(FG-BG)
def parse(d):
    t=[float(v) for v in re.findall(r'-?\d+\.?\d*',d)]
    start=(t[0],t[1]); segs=[]; i=2
    while i+6<=len(t): segs.append(((t[i],t[i+1]),(t[i+2],t[i+3]),(t[i+4],t[i+5]))); i+=6
    return (start,segs)
box=np.s_[0:260,31:429]
for k in ['v10_hairL','v11_hairR','v12_cap','v00_crescent']:
    d=re.search(r'<path d="([^"]+)"',open(f'svg/{k}.svg').read()).group(1)
    P,C=build(parse(d)); E=expand(P,C); R=raster(E,460,260)
    o=cov(L(f'png/mst2_t__{k}_z2.png')); i=cov(L(f'refs/id_t__{k}_z2.png'))
    refs=[L(f'refs/{b}_t__{k}_z2.png') for b in ('chr','ff','wk')]
    oi=L(f'png/mst2_t__{k}_z2.png')
    all3=np.logical_and.reduce([np.abs(oi-r).max(2)>20 for r in refs])
    all3[:, :31]=False; all3[:,429:]=False
    w=R['wind']
    # local mean width
    area=0.5*abs(sum((P[j][0]-P[j-1][0])*(P[j][1]+P[j-1][1]) for j in range(len(P)))); per=sum(np.hypot(*(P[j]-P[j-1])) for j in range(len(P)))
    print(f'{k:14s} mean width {2*area/per:.2f}  model-vs-femtovg max {np.abs(R["total"]-o)[box].max():.3f}  all3 {int(all3.sum())}: at stencil 0 {int((all3&(w==0)).sum())}, at stencil!=0 {int((all3&(w!=0)).sum())};  excess ink (fem-area) over all3 px {float((o-i)[all3].sum()):.1f}, of it from stencil-0 px {float((o-i)[all3&(w==0)].sum()):.1f}')
    ys,xs=np.nonzero(all3); 
    if len(xs): print('   all3 bbox x',xs.min(),xs.max(),'y',ys.min(),ys.max())
