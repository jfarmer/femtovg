"""sheet.py out.png x0 y0 x1 y1 scale ours chr ff wk [id]: femtovg | chromium | firefox | webkit | area | error map"""
import sys, numpy as np
from PIL import Image, ImageDraw
out=sys.argv[1]; x0,y0,x1,y1,s=map(int,sys.argv[2:7]); paths=sys.argv[7:]
L=lambda p: np.asarray(Image.open(p).convert('RGB'),dtype=np.int16)
ims=[L(p) for p in paths]; o=ims[0]; refs=ims[1:4]
off=[np.abs(o-r).max(2)>20 for r in refs]; all3=off[0]&off[1]&off[2]
sp=np.zeros(all3.shape,bool)
for i in range(3):
  for j in range(i+1,3): sp|=np.abs(refs[i]-refs[j]).max(2)>20
g=(0.3*o[...,0]+0.59*o[...,1]+0.11*o[...,2]); em=np.stack([g*0.5+100]*3,-1)
em[all3&sp]=[255,170,0]; em[all3&~sp]=[230,0,0]
names=['femtovg','chromium','firefox','webkit','area'][:len(ims)]+['err']
tiles=[im[y0:y1,x0:x1] for im in ims]+[em[y0:y1,x0:x1]]
w=(x1-x0)*s; h=(y1-y0)*s
c=Image.new('RGB',(len(tiles)*(w+4),h+14),'white'); d=ImageDraw.Draw(c)
for i,(t,n) in enumerate(zip(tiles,names)):
  c.paste(Image.fromarray(np.clip(t,0,255).astype(np.uint8)).resize((w,h),Image.NEAREST),(i*(w+4),14)); d.text((i*(w+4)+2,1),n,fill='black')
c.save(out); print('all3',int(all3[y0:y1,x0:x1].sum()),'agreed',int((all3&~sp)[y0:y1,x0:x1].sum()))
