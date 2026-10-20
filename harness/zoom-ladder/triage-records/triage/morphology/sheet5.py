import numpy as np
from PIL import Image, ImageDraw, ImageFont
R='/Users/matt/src/femtovg-wt/runs/zoom'
font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',13)
L=lambda p: np.asarray(Image.open(p).convert('RGB')).astype(int)
rows=[('horizontal','z075',0.75),('horizontal','z125',1.25),('horizontal','z175',1.75),('vertical','z075',0.75),('vertical','z175',1.75)]
S=6; W=36; H=20
def diffimg(a,b):
    d=np.abs(a-b).max(-1); o=np.full(a.shape,255,np.uint8)
    o[(d>8)&(d<=20)]=[255,160,0]; o[d>20]=[220,30,30]; return o,int((d>8).sum())
tiles=[]
for ax,fr,z in rows:
    key=f'corpus__wpt-femorphology-reftests__morphology-dilate-{ax}-only'
    m=L(f'ladder/mst_{key}_{fr}.ppm'); f=L(f'ladder/fix_{key}_{fr}.ppm'); c=L(f'{R}/fresh/refs/chr_{key}_{fr}.png')
    e=230-50*z; x0=int(e)-6; y0=int(130-50*z)-6
    cut=lambda a: Image.fromarray(a[y0:y0+H,x0:x0+W].astype(np.uint8)).resize((W*S,H*S),Image.NEAREST)
    dm,nm=diffimg(m,c); df,nf=diffimg(f,c)
    tiles.append((f'dilate-{ax}-only  zoom {z:g}  (radius {"15 0" if ax=="horizontal" else "0 15"}; top-left corner, x{S})',
        [('master (usvg 0.48.1)',cut(m)),('master + usvg keeping the zero',cut(f)),('Chromium 131',cut(c)),
         (f'master vs Chromium: {nm} px > 8/255',cut(dm)),(f'patched vs Chromium: {nf} px',cut(df))]))
pad=8; top=36; tw=W*S; th=H*S
img=Image.new('RGB',(5*(tw+pad)+pad,len(tiles)*(th+top+pad)+pad),(40,40,40)); d=ImageDraw.Draw(img)
for r,(cap,ps) in enumerate(tiles):
    y=pad+r*(th+top+pad); d.text((pad,y),cap,fill=(255,255,255),font=font)
    for i,(t,im) in enumerate(ps):
        x=pad+i*(tw+pad); d.text((x,y+17),t,fill=(220,220,220),font=font); img.paste(im,(x,y+top))
img.save('sheet_before_after_chromium.png'); print(img.size)
