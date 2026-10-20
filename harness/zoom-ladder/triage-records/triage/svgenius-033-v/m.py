import numpy as np, os
from PIL import Image
H=os.path.expanduser('~/src/femtovg-wt/runs/zoom')
SHOE='svgenius__page_70_像素鞋子图标_40194_icon_17'
MAKE='svgenius__page_275_化妆品装饰_25821_icon_24'
SVG={SHOE:os.path.expanduser('~/src/femtovg-wt/da/corpus/svgenius/hard/page_70_像素鞋子图标_40194_icon_17.svg'),
     MAKE:os.path.expanduser('~/src/femtovg-wt/da/corpus/svgenius/medium/page_275_化妆品装饰_25821_icon_24.svg')}
def load(p):
    a=np.asarray(Image.open(p).convert('RGBA')).astype(float)
    return a[...,:3]*a[...,3:4]/255+255*(1-a[...,3:4]/255)
def nb(a,b,t=8): return int((np.abs(a-b).max(-1)>t).sum())
def ref(br,key,fr):
    p=f'{H}/fresh/refs/{br}_{key}_{fr}.png'
    return load(p) if os.path.exists(p) else None
def ink(a): return (255-a).sum()
