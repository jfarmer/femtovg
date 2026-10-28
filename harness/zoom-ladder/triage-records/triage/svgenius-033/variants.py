import numpy as np, os, sys
from PIL import Image
H=os.path.expanduser('~/src/femtovg-wt/runs/zoom')
K={'shoe':"svgenius__page_70_像素鞋子图标_40194_icon_17",'makeup':"svgenius__page_275_化妆品装饰_25821_icon_24"}
def c(p):
    a=np.asarray(Image.open(p).convert('RGBA')).astype(float); return (a[...,:3]*a[...,3:4]+255*(255-a[...,3:4]))/255
def n(a,b): return int((np.abs(a-b).max(-1)>8).sum())
def ink(a): return (255-a.mean(-1)).sum()
for f in ['shoe','makeup']:
  for zz in sys.argv[1:]:
    refs={br:c(f'{H}/fresh/refs/{br}_{K[f]}_z{zz}.png') for br in ['chr','ff','wk'] if os.path.exists(f'{H}/fresh/refs/{br}_{K[f]}_z{zz}.png')}
    A=c(f'area_{f}_{zz}.png')
    for v in ['base','gate','force']:
        im=c(f'p_{f}_{zz}_{v}.png')
        r={br:n(im,b) for br,b in refs.items()}
        print(f'{f:7s} z{zz:4s} {v:6s}', ' '.join(f'{br}={x:4d}' for br,x in r.items()), f'best={min(r.values()):4d} area={n(im,A):4d} ink/area={ink(im)/ink(A):.3f}')
