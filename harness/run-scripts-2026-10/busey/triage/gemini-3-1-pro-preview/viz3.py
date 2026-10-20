import sys, numpy as np
from PIL import Image
from cmp import get
name=sys.argv[1]; b=sys.argv[2]; out=sys.argv[3]; box=[int(v) for v in sys.argv[4].split(',')]; sc=int(sys.argv[5])
o,r,a,sp=get(name,b); ag=a&~sp
x0,y0,x1,y1=box
ov=(o*0.35+160*0.65).astype(np.uint8); ov[a]=[255,170,0]; ov[ag]=[255,0,0]
tiles=[t[y0:y1,x0:x1].astype(np.uint8) for t in (o,r[0],r[2],ov)]
im=np.concatenate([np.pad(t,((0,4),(0,4),(0,0)),constant_values=255) for t in tiles],axis=1)
Image.fromarray(im).resize((im.shape[1]*sc,im.shape[0]*sc),Image.NEAREST).save(out)
H,W=ag.shape
cells=[]
for y in range(0,H,20):
    for x in range(0,W,20):
        n=ag[y:y+20,x:x+20].sum()
        if n: cells.append((int(n),x,y))
print(sorted(cells,reverse=True)[:25])
