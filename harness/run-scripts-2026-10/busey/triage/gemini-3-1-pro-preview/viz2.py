import sys, numpy as np
from PIL import Image
from cmp import get
name=sys.argv[1]; out=sys.argv[2]; box=[int(v) for v in sys.argv[3].split(',')]; sc=int(sys.argv[4])
o,r,a,sp=get(name); ag=a&~sp
x0,y0,x1,y1=box
ov=(o*0.35+160*0.65).astype(np.uint8); ov[a]=[255,170,0]; ov[ag]=[255,0,0]
tiles=[t[y0:y1,x0:x1].astype(np.uint8) for t in (o,r[0],r[1],r[2],ov)]
im=np.concatenate([np.pad(t,((0,4),(0,4),(0,0)),constant_values=255) for t in tiles],axis=1)
Image.fromarray(im).resize((im.shape[1]*sc,im.shape[0]*sc),Image.NEAREST).save(out)
