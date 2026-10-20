# before | after (4096-texel LUT prototype) | Chromium | before vs Chromium | after vs Chromium, one row per zoom.
import sys, numpy as np
from PIL import Image, ImageDraw, ImageFont
R='/Users/matt/src/femtovg-wt/runs/zoom/'; T=R+'triage/gradient-hard-stops/'
key, out, crop, scale = sys.argv[1], sys.argv[2], [int(v) for v in sys.argv[3].split(',')], int(sys.argv[4])
fr = sys.argv[5].split(',')
label = sys.argv[6] if len(sys.argv) > 6 else key
step={'z1':0,'z125':1,'z15':2,'z175':3,'z2':4,'z3':5,'z4':6,'z075':13,'z05':14,'z033':15,'z025':16}
zv={'z1':1,'z125':1.25,'z15':1.5,'z175':1.75,'z2':2,'z3':3,'z4':4,'z075':.75,'z05':.5,'z033':.33,'z025':.25}
font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',14)
L=lambda p: np.asarray(Image.open(p).convert('RGB')).astype(int)
def cut(a):
    x,y,w,h=crop; im=Image.fromarray(np.clip(a[y:y+h,x:x+w],0,255).astype(np.uint8))
    return im.resize((w*scale,h*scale),Image.NEAREST)
def diff(a,b):
    d=np.abs(a-b).max(axis=2); img=np.stack([np.clip(d*4,0,255)]*3,-1); img[d>8]=[230,30,30]; return img,int((d>8).sum())
frames=[]
for f in fr:
    before=L(f'{R}png/zl_zm_svg/{key}/{step[f]:02d}.png'); after=L(f'{T}out/p4096_{key}_{f}.png'); chr_=L(f'{R}fresh/refs/chr_{key}_{f}.png')
    db,nb=diff(before,chr_); da,na=diff(after,chr_)
    tiles=[('femtovg master (256-texel LUT)',before),('prototype: 4096-texel LUT',after),('Chromium 131',chr_),
           (f'> 8/255 master vs Chromium: {nb} px',db),(f'> 8/255 prototype vs Chromium: {na} px',da)]
    ims=[(t,cut(a)) for t,a in tiles]; w,h=ims[0][1].size; pad,top=8,40
    c=Image.new('RGB',(len(ims)*(w+pad)+pad,h+top+pad),(40,40,40)); dr=ImageDraw.Draw(c)
    dr.text((pad,4),f'{label}   zoom {zv[f]:g}   (whole frame counts; crop x={crop[0]}..{crop[0]+crop[2]} y={crop[1]}..{crop[1]+crop[3]})',fill=(255,255,255),font=font)
    for i,(t,im) in enumerate(ims):
        x=pad+i*(w+pad); dr.text((x,22),t,fill=(220,220,220),font=font); c.paste(im,(x,top))
    frames.append(c)
frames[0].save(out+'.gif',save_all=True,append_images=frames[1:],duration=1100,loop=0,optimize=True)
frames[0].save(out+'.webp',save_all=True,append_images=frames[1:],duration=1100,loop=0,lossless=True,method=4)
sheet=Image.new('RGB',(frames[0].width,sum(fm.height for fm in frames)),(40,40,40)); y=0
for fm in frames: sheet.paste(fm,(0,y)); y+=fm.height
sheet.save(out+'_sheet.png'); print(out, sheet.size)
