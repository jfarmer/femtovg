import sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
H=os.path.expanduser('~')
Z=H+'/src/femtovg-wt/runs/zoom/'
key=sys.argv[1]; out=sys.argv[2]; steps=[int(s) for s in sys.argv[3].split(',')]
fixdir=sys.argv[4]; label=sys.argv[5] if len(sys.argv)>5 else key
LADDER=[1,1.25,1.5,1.75,2,3,4,3,2,1.75,1.5,1.25,1,0.75,0.5,0.33,0.25,0.33,0.5,0.75,1]
FR={1:'z1',1.25:'z125',1.5:'z15',1.75:'z175',2:'z2',3:'z3',4:'z4',0.75:'z075',0.5:'z05',0.33:'z033',0.25:'z025'}
font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',14)
def L(p): return np.asarray(Image.open(p).convert('RGB'),dtype=np.int16)
def diff(a,b):
  d=np.abs(a-b).max(axis=2); img=np.stack([np.clip(d*4,0,255)]*3,-1); img[d>8]=[230,30,30]; return img,int((d>8).sum())
frames=[]
for s in steps:
  z=LADDER[s]
  before=L(Z+'png/zl_zm_svg/%s/%02d.png'%(key,s)); after=L('%s/%02d.png'%(fixdir,s))
  chr_=L(Z+'fresh/refs/chr_%s_%s.png'%(key,FR[z]))
  db,nb=diff(before,chr_); da,na=diff(after,chr_)
  tiles=[('before (master 06243b80)',before),('after (cull by stroke reach)',after),('Chromium 131',chr_),
         ('before vs Chromium: %d px > 8/255'%nb,db),('after vs Chromium: %d px > 8/255'%na,da)]
  w,h=460,260; pad,top=8,44
  C=Image.new('RGB',(len(tiles)*(w+pad)+pad,h+top+pad),(40,40,40)); D=ImageDraw.Draw(C)
  D.text((pad,4),'%s   zoom %g (step %d of 21)'%(label,z,s+1),fill=(255,255,255),font=font)
  for i,(t,a) in enumerate(tiles):
    x=pad+i*(w+pad); D.text((x,24),t,fill=(220,220,220),font=font)
    C.paste(Image.fromarray(np.clip(a,0,255).astype(np.uint8)),(x,top))
  frames.append(C)
frames[0].save(out+'.gif',save_all=True,append_images=frames[1:],duration=900,loop=0)
frames[0].save(out+'.webp',save_all=True,append_images=frames[1:],duration=900,loop=0,lossless=True)
# static sheet: all steps stacked
S=Image.new('RGB',(frames[0].width,sum(f.height for f in frames)),(40,40,40)); y=0
for f in frames: S.paste(f,(0,y)); y+=f.height
S.save(out+'_sheet.png')
print(out, len(frames))
