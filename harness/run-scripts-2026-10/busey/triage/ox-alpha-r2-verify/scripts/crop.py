"""crop.py OUT x0 y0 w h scale PNG... : side-by-side nearest-neighbour crops."""
import sys
from PIL import Image
out,x0,y0,w,h,s=sys.argv[1],*map(int,sys.argv[2:7])
ims=[Image.open(p).convert('RGB').crop((x0,y0,x0+w,y0+h)).resize((w*s,h*s),Image.NEAREST) for p in sys.argv[7:]]
W=Image.new('RGB',(len(ims)*(w*s+4),h*s),(255,0,255))
for i,im in enumerate(ims): W.paste(im,(i*(w*s+4),0))
W.save(out)
