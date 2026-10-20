import numpy as np
from PIL import Image
S=0.390625
L=lambda p: np.asarray(Image.open(p).convert('L'),dtype=np.float64)/255
names={'fem':'png/mst2_t__tongues_z2.png','off':'png/mst2_off_t__tongues_z2.png','chr':'refs/chr_t__tongues_z2.png','ff':'refs/ff_t__tongues_z2.png','wk':'refs/wk_t__tongues_z2.png'}
im={k:L(v) for k,v in names.items()}
ws=[0.2,0.4,0.6,0.8,1.0,1.25,1.5,2.0,3.0]
def model(w):
    # nanovg-style concave fringe: stencil of 0.5px inset, tent strips 1.5 in..0.5 out, src-over, cover where stencil!=0
    xs=np.linspace(-3,w+3,200001); dx=xs[1]-xs[0]
    a=np.clip(1-np.abs(xs-0.5),0,1); b=np.clip(1-np.abs(xs-(w-0.5)),0,1)
    lo,hi=min(0.5,w-0.5),max(0.5,w-0.5)
    st=(xs>lo)&(xs<hi)
    fr=1-(1-a)*(1-b)
    c=np.where(st,1.0,fr)
    return c.sum()*dx
print('w    model  fem   off   chr   ff    wk')
for i,w in enumerate(ws):
    v=210+i*70; y=-70+v*S
    y0,y1=int(y-8),int(y+9)
    x0,x1=int(30+160*S),int(30+400*S)
    row=[np.median(im[k][y0:y1,x0:x1].sum(axis=0)) for k in names]
    print(f'{w:<4} {model(w):.3f} '+' '.join(f'{r:.3f}' for r in row))
