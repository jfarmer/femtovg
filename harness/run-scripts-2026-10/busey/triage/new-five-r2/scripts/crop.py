"""crop.py out.png name fr x0 y0 x1 y1 scale [pd=] [rd=] [build=] [key=]  -> femtovg|chr|ff|wk|id|err"""
import sys, numpy as np
from PIL import Image, ImageDraw
a=dict(x.split('=',1) for x in sys.argv[1:] if '=' in x); p=[x for x in sys.argv[1:] if '=' not in x]
out,name,fr=p[0],p[1],p[2]; x0,y0,x1,y1,s=map(int,p[3:8])
pd=a.get('pd','/Users/matt/src/femtovg-wt/runs/busey/png'); rd=a.get('rd','/Users/matt/src/femtovg-wt/runs/busey/refs'); b=a.get('build','mst4')
k=a.get('key','corpus__buseybench__'+name)
L=lambda p: np.asarray(Image.open(p).convert('RGB'),dtype=np.int16)
o=L(f'{pd}/{b}_{k}_{fr}.png'); refs=[L(f'{rd}/{x}_{k}_{fr}.png') for x in ('chr','ff','wk')]
try: idr=L(f'{rd}/id_{k}_{fr}.png')
except Exception: idr=refs[0]*0
off=[np.abs(o-r).max(2)>20 for r in refs]; all3=off[0]&off[1]&off[2]
sp=np.zeros(all3.shape,bool)
for i in range(3):
  for j in range(i+1,3): sp|=np.abs(refs[i]-refs[j]).max(2)>20
g=(0.3*o[...,0]+0.59*o[...,1]+0.11*o[...,2]); em=np.stack([g*0.5+100]*3,-1)
em[all3&sp]=[255,170,0]; em[all3&~sp]=[230,0,0]
tiles=[o,*refs,idr,em]; names=['femtovg','chromium','firefox','webkit','area8x','err']
tiles=[t[y0:y1,x0:x1] for t in tiles]
w=(x1-x0)*s; h=(y1-y0)*s
cv=Image.new('RGB',(3*(w+4),2*(h+14)),'white'); d=ImageDraw.Draw(cv)
for i,(t,n) in enumerate(zip(tiles,names)):
  X=(i%3)*(w+4); Y=(i//3)*(h+14)
  cv.paste(Image.fromarray(np.clip(t,0,255).astype(np.uint8)).resize((w,h),Image.NEAREST),(X,Y+14)); d.text((X+2,Y+1),n,fill='black')
cv.save(out)
print('all3',int(all3[y0:y1,x0:x1].sum()),'agreed',int((all3&~sp)[y0:y1,x0:x1].sum()))
