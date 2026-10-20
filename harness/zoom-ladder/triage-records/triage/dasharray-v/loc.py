import sys, numpy as np
from PIL import Image
R='/Users/matt/src/femtovg-wt/runs/zoom'
LAD=[1,1.25,1.5,1.75,2,3,4,3,2,1.75,1.5,1.25,1,0.75,0.5,0.33,0.25,0.33,0.5,0.75,1]
FR={1:'z1',1.25:'z125',1.5:'z15',1.75:'z175',2:'z2',3:'z3',4:'z4',0.75:'z075',0.5:'z05',0.33:'z033',0.25:'z025'}
key=sys.argv[1]; zoom=float(sys.argv[2])
step=LAD.index(zoom)
def L(p):
    try: return np.asarray(Image.open(p).convert('RGB'),dtype=np.int16)
    except FileNotFoundError: return None
f=L(f'{R}/png/zl_zm_svg/{key}/{step:02}.png')
dev=lambda v: 230+(v-100)*zoom
devy=lambda v: 130+(v-100)*zoom
# rect corners in device space
rx=[30,50,70,90,110,130,150,170]
cx=[dev(v) for v in rx]; cy=[devy(v) for v in rx]
fx=[dev(0.5),dev(1.5),dev(198.5),dev(199.5)]; fy=[devy(0.5),devy(1.5),devy(198.5),devy(199.5)]
for b in ['chr','ff','wk']:
    o=L(f'{R}/fresh/refs/{b}_{key}_{FR[zoom]}.png')
    if o is None: print(b,'none'); continue
    d=np.abs(f-o).max(2); m=d>8
    ys,xs=np.nonzero(m)
    cls={'rectcorner':0,'framecorner':0,'other':0}
    others=[]
    for y,x in zip(ys,xs):
        nearc = min(abs(x+0.5-v) for v in cx)<1.01 and min(abs(y+0.5-v) for v in cy)<1.01
        nearf = min(abs(x+0.5-v) for v in fx)<1.01 and min(abs(y+0.5-v) for v in fy)<1.01
        if nearc: cls['rectcorner']+=1
        elif nearf: cls['framecorner']+=1
        else: cls['other']+=1; others.append((x,y,tuple(f[y,x]),tuple(o[y,x])))
    print(b, m.sum(), cls, others[:12])
