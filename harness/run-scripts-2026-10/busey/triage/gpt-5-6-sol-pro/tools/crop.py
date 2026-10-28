#!/usr/bin/env python3
"""crop.py OURS CHR FF WK x0 y0 x1 y1 scale OUT : side-by-side crops + all3 map"""
import sys, numpy as np
from PIL import Image
o,c,f,w = [np.asarray(Image.open(p).convert('RGB'),dtype=np.int16) for p in sys.argv[1:5]]
x0,y0,x1,y1,sc = map(int, sys.argv[5:10]); out=sys.argv[10]
off=[np.abs(o-r).max(2)>20 for r in (c,f,w)]
a=off[0]&off[1]&off[2]
spread=np.zeros(a.shape,bool)
for r1,r2 in ((c,f),(c,w),(f,w)): spread|=np.abs(r1-r2).max(2)>20
m=(o.mean(2)*0.5+64).astype(np.uint8); m=np.stack([m]*3,2)
m[a&~spread]=[255,0,0]; m[a&spread]=[255,160,0]
tiles=[x[y0:y1,x0:x1].astype(np.uint8) for x in (o,c,f,w)]+[m[y0:y1,x0:x1]]
gap=4
H=(y1-y0)*sc; W=(x1-x0)*sc
img=Image.new('RGB',(5*W+4*gap,H),(255,255,255))
for i,t in enumerate(tiles):
    img.paste(Image.fromarray(t).resize((W,H),Image.NEAREST),(i*(W+gap),0))
img.save(out)
print('all3 in crop', int(a[y0:y1,x0:x1].sum()), 'agreed', int((a&~spread)[y0:y1,x0:x1].sum()))
