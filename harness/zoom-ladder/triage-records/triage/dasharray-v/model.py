import sys, numpy as np
from PIL import Image
R='/Users/matt/src/femtovg-wt/runs/zoom'
LAD=[1,1.25,1.5,1.75,2,3,4,3,2,1.75,1.5,1.25,1,0.75,0.5,0.33,0.25,0.33,0.5,0.75,1]
FR={1:'z1',1.25:'z125',1.5:'z15',1.75:'z175',2:'z2',3:'z3',4:'z4',0.75:'z075',0.5:'z05',0.33:'z033',0.25:'z025'}
key='wpt22__21-degenerate-paths-dashes-and-joins__resvg-dasharray-0-n-square-caps-ref'
rects=[(30,30),(70,30),(110,30),(150,30),(150,70),(150,110),(150,150),(110,150),(70,150),(30,150),(30,110),(30,70)]
def L(p):
    try: return np.asarray(Image.open(p).convert('RGB'),dtype=np.float64)
    except FileNotFoundError: return None
for zoom in [1.25,1.75,0.75,0.33,0.25]:
    f=L(f'{R}/png/zl_zm_svg/{key}/{LAD.index(zoom):02}.png')
    refs={b:L(f'{R}/fresh/refs/{b}_{key}_{FR[zoom]}.png') for b in ['chr','wk']}
    X=np.arange(460)+0.5; Y=np.arange(260)+0.5
    mn=np.zeros((260,460)); ar=np.zeros((260,460))
    for (x,y) in rects:
        x0=230+(x-100)*zoom; x1=230+(x+20-100)*zoom; y0=130+(y-100)*zoom; y1=130+(y+20-100)*zoom
        ax=np.clip(np.minimum(X-x0+0.5, x1-X+0.5),0,1)  # pixel-centre ramp == exact per-axis overlap for 20z>=1
        ay=np.clip(np.minimum(Y-y0+0.5, y1-Y+0.5),0,1)
        mn=np.maximum(mn, np.minimum(ax[None,:],ay[:,None]))
        ar=np.maximum(ar, ax[None,:]*ay[:,None])
    # restrict to the rect region (away from frame)
    m=(ar>0)|(mn>0)
    cf=1-f[...,0]/255
    errmin=np.abs(cf-mn)[m]; errar=np.abs(cf-ar)[m]
    out=f'z={zoom}: femtovg vs min-model max {errmin.max()*255:.1f}/255, vs area-model max {errar.max()*255:.1f}/255;'
    for b,o in refs.items():
        if o is None: continue
        co=1-o[...,0]/255
        out+=f' {b} vs area max {np.abs(co-ar)[m].max()*255:.1f}, vs min {np.abs(co-mn)[m].max()*255:.1f};'
    # count pixels where min and area differ by >8/255
    out+=f' model-predicted fails(>8): {(np.abs(mn-ar)*255>8).sum()}'
    print(out)
