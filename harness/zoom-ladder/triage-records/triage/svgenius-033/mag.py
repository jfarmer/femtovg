import sys, numpy as np, os
from PIL import Image
H=os.path.expanduser('~/src/femtovg-wt/runs/zoom')
key,step,fr,out=sys.argv[1:5]
x,y,w,h=map(int,sys.argv[5].split(',')); s=int(sys.argv[6]) if len(sys.argv)>6 else 8
def comp(p):
    a=np.asarray(Image.open(p).convert('RGBA')).astype(np.int32)
    return ((a[...,:3]*a[...,3:4]+255*(255-a[...,3:4]))//255)
ims=[comp(f'{H}/png/zl_zm_svg/{key}/{step}.png')]
names=['fv']
for br in ['chr','ff','wk']:
    p=f'{H}/fresh/refs/{br}_{key}_{fr}.png'
    if os.path.exists(p): ims.append(comp(p)); names.append(br)
extra=sys.argv[7:]  # extra pngs
for p in extra: ims.append(comp(p)); names.append(os.path.basename(p))
crops=[im[y:y+h,x:x+w] for im in ims]
# diff vs chr signed
d=(crops[0].mean(-1)-crops[1].mean(-1))
dv=np.zeros(crops[0].shape,np.int32)+255
pos=d>0; neg=d<0
m=np.clip(np.abs(d)*4,0,255).astype(np.int32)
dv[...,1]-=m; dv[...,2]-=np.where(pos,m,0); dv[...,0]-=np.where(neg,m,0)
dv[...,2]=np.where(neg,255-m,dv[...,2])
crops.append(np.clip(dv,0,255))
row=np.concatenate([np.pad(c,((2,2),(2,2),(0,0)),constant_values=128) for c in crops],1).astype(np.uint8)
Image.fromarray(row).resize((row.shape[1]*s,row.shape[0]*s),Image.NEAREST).save(out)
print(names+['diff fv-chr (red: fv lighter, blue: fv darker)'])
