import numpy as np
from PIL import Image, ImageDraw, ImageFont
REF='/Users/matt/src/femtovg-wt/runs/zoom/fresh/refs'
P='wpt22__21-degenerate-paths-dashes-and-joins__'
font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',15)
L=lambda p: np.asarray(Image.open(p).convert('RGB'),dtype=np.int16)
rows=[
 ('resvg-dasharray-0-n-square-caps-ref (no dashes: 12 rects + frame), zoom 1.25: rect corners on half pixels',
  'exp/e_resvg-dasharray-0-n-square-caps-ref_1.25.png','exp/mask_resvg-dasharray-0-n-square-caps-ref_1.25.png',
  f'{REF}/chr_{P}resvg-dasharray-0-n-square-caps-ref_z125.png','every fill through the exact-area mask', (137,37,36,18), 13, 'Chromium 131 (Firefox, WebKit the same here)'),
 ('resvg-dasharray-n-0-solid (stroke-dasharray="40 0"), zoom 0.33: seams where dashes abut at x.4 / x.6',
  'exp/e_resvg-dasharray-n-0-solid_0.33.png','exp/merge_resvg-dasharray-n-0-solid_0.33.png',
  f'{REF}/wk_{P}resvg-dasharray-n-0-solid_z033.png','zero-gap dashes merged into one subpath', (200,100,60,40), 8, 'WebKit (macOS 27.2), the nearest browser here'),
]
tiles=[]
for title,a,b,c,exp,(x,y,w,h),s,rname in rows:
    A,B,C=L(a),L(b),L(c)
    def diff(X):
        d=np.abs(X-C).max(2); img=np.stack([np.clip(d*4,0,255)]*3,-1).astype(np.int16); img[d>8]=[230,30,30]; return img,f'{int((d[y:y+h,x:x+w]>8).sum())} px here, {int((d>8).sum())} in the frame'
    dA,nA=diff(A); dB,nB=diff(B)
    rs=rname.split(' ')[0]
    cols=[('femtovg master 06243b80',A),(f'experiment: {exp}',B),(rname,C),(f'> 8/255, master vs {rs}: {nA}',dA),(f'> 8/255, experiment vs {rs}: {nB}',dB)]
    tiles.append((title,cols,(x,y,w,h),s))
pad,top,lab=10,28,22
W=max(len(c)*(t[2][2]*t[3]+pad)+pad for _,c,t2,s in tiles for t in [(0,0,t2,s)])
H=sum(top+lab+t2[3]*s+pad for _,_,t2,s in tiles)
sheet=Image.new('RGB',(W,H),(40,40,40)); dr=ImageDraw.Draw(sheet); yy=0
for title,cols,(x,y,w,h),s in tiles:
    dr.text((pad,yy+6),title,fill=(255,255,255),font=font); yy+=top
    for i,(t,a) in enumerate(cols):
        im=Image.fromarray(np.clip(a[y:y+h,x:x+w],0,255).astype(np.uint8)).resize((w*s,h*s),Image.NEAREST)
        xx=pad+i*(w*s+pad)
        dr.text((xx,yy),t,fill=(220,220,220),font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',12))
        sheet.paste(im,(xx,yy+lab))
    yy+=lab+h*s+pad
sheet.save('sheet_dasharray.png'); print(sheet.size)
