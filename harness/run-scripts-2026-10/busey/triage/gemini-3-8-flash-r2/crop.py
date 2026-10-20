import sys, numpy as np
from PIL import Image, ImageDraw
# crop.py out.png x0 y0 x1 y1 scale fr ours [chr ff wk [id]]
out=sys.argv[1]; x0,y0,x1,y1,s=map(int,sys.argv[2:7]); fr=sys.argv[7]
k='corpus__buseybench__gemini-3-8-flash'; RB='/Users/matt/src/femtovg-wt/runs/busey/refs'
paths=sys.argv[8:]
if len(paths)==1: paths=paths+[f'{RB}/{x}_{k}_{fr}.png' for x in ('chr','ff','wk','id')]
L=lambda p: np.asarray(Image.open(p).convert('RGB'),dtype=np.int16)
ims=[L(p) for p in paths]
o=ims[0]; refs=ims[1:4]
off=[np.abs(o-r).max(2)>20 for r in refs]; all3=off[0]&off[1]&off[2]
spread=np.zeros(all3.shape,bool)
for i in range(3):
  for j in range(i+1,3): spread|=np.abs(refs[i]-refs[j]).max(2)>20
g=(0.3*o[...,0]+0.59*o[...,1]+0.11*o[...,2]); em=np.stack([g*0.5+100]*3,-1)
em[all3&spread]=[255,170,0]; em[all3&~spread]=[230,0,0]
names=['femtovg','chromium','firefox','webkit','area'][:len(ims)]+['err']
tiles=[im[y0:y1,x0:x1] for im in ims]+[em[y0:y1,x0:x1]]
w=(x1-x0)*s; h=(y1-y0)*s
canvas=Image.new('RGB',(len(tiles)*(w+4),h+14),'white'); d=ImageDraw.Draw(canvas)
for i,(t,n) in enumerate(zip(tiles,names)):
  canvas.paste(Image.fromarray(np.clip(t,0,255).astype(np.uint8)).resize((w,h),Image.NEAREST),(i*(w+4),14)); d.text((i*(w+4)+2,1),n,fill='black')
canvas.save(out)
print('all3',all3[y0:y1,x0:x1].sum(),'agreed',(all3&~spread)[y0:y1,x0:x1].sum())
