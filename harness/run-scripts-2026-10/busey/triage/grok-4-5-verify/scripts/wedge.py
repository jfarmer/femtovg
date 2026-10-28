import numpy as np
from PIL import Image
import importlib.util,sys
S=0.390625
L=lambda p: np.asarray(Image.open(p).convert('L'),dtype=np.float64)/255
names={'fem':'png/mst2_t__wedge_z2.png','chr':'refs/chr_t__wedge_z2.png','ff':'refs/ff_t__wedge_z2.png','wk':'refs/wk_t__wedge_z2.png'}
im={k:L(v) for k,v in names.items()}
def model(w):
    xs=np.linspace(-3,w+3,60001); dx=xs[1]-xs[0]
    a=np.clip(1-np.abs(xs-0.5),0,1); b=np.clip(1-np.abs(xs-(w-0.5)),0,1)
    lo,hi=min(0.5,w-0.5),max(0.5,w-0.5)
    c=np.where((xs>lo)&(xs<hi),1.0,1-(1-a)*(1-b)); return c.sum()*dx
xt=30+1000*S
for half,v in [(10,300),(14,560)]:
    y=-70+v*S; y0,y1=int(y-12),int(y+13)
    print(f'half={half} tip x={xt:.2f}  (width/px of length = {2*half/700:.4f})')
    print(' col  dtip  w_true model  fem   chr   ff    wk')
    tot={k:0 for k in names}; totm=0; tottrue=0
    for x in range(int(xt)-60,int(xt)+4):
        dc=xt-(x+0.5); wt=max(dc,0)*2*half/700
        r={k:im[k][y0:y1,x].sum() for k in names}
        m=model(wt) if dc>0 else 0
        for k in names: tot[k]+=r[k]
        totm+=m; tottrue+=wt
        if x%3==0 or dc<3: print(f'{x:4d} {dc:6.2f} {wt:.3f}  {m:.3f} '+' '.join(f'{r[k]:.3f}' for k in names))
    print(' totals over 64 cols: true %.2f model %.2f '%(tottrue,totm)+' '.join(f'{k} {tot[k]:.2f}' for k in names))
