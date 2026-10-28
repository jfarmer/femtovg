import sys, numpy as np
from PIL import Image
from cmp import get, L, S
a,b=sys.argv[1],sys.argv[2]; out=sys.argv[3]; box=[int(v) for v in sys.argv[4].split(',')]; sc=int(sys.argv[5])
oa,ra,aa,spa=get(a); ob,rb,ab,spb=get(b)
x0,y0,x1,y1=box
def vis(d):
    d=d.mean(axis=2)[y0:y1,x0:x1]
    im=np.full(d.shape+(3,),128,np.int16)
    im[...,0]=np.clip(128+d*2,0,255); im[...,1]=128; im[...,2]=np.clip(128-d*2,0,255)
    return im.astype(np.uint8)
tiles=[vis(oa-ob),vis(ra[0]-rb[0]),vis(ra[1]-rb[1]),vis(ra[2]-rb[2])]
agm=(aa&~spa)[y0:y1,x0:x1]
t=np.stack([agm*255]*3,-1).astype(np.uint8); tiles.append(t)
im=np.concatenate([np.pad(t,((0,4),(0,4),(0,0)),constant_values=255) for t in tiles],axis=1)
Image.fromarray(im).resize((im.shape[1]*sc,im.shape[0]*sc),Image.NEAREST).save(out)
