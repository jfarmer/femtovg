"""zoom.py out.png x0 y0 x1 y1 scale img... (labels from file names)"""
import sys, os, numpy as np
from PIL import Image, ImageDraw
out=sys.argv[1]; x0,y0,x1,y1,s=map(int,sys.argv[2:7]); ps=sys.argv[7:]
w=(x1-x0)*s; h=(y1-y0)*s
c=Image.new('RGB',(len(ps)*(w+4),h+14),'white'); d=ImageDraw.Draw(c)
for i,p in enumerate(ps):
  im=Image.open(p).convert('RGB').crop((x0,y0,x1,y1)).resize((w,h),Image.NEAREST)
  c.paste(im,(i*(w+4),14)); d.text((i*(w+4)+2,1),os.path.basename(p)[:40],fill='black')
c.save(out)
