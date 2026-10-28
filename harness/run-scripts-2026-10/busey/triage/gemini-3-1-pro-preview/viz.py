import sys, numpy as np
from PIL import Image
sys.path.insert(0,'.')
from an import masks, R
k='corpus__buseybench__gemini-3-1-pro-preview'
ours_p=sys.argv[1] if len(sys.argv)>1 else R+f'/png/mst2_{k}_z2.png'
out=sys.argv[2] if len(sys.argv)>2 else 'viz.png'
box=[int(v) for v in sys.argv[3].split(',')] if len(sys.argv)>3 else [0,0,460,260]
sc=int(sys.argv[4]) if len(sys.argv)>4 else 2
ours,refs,a,s=masks(ours_p,k)
ag=a&~s
x0,y0,x1,y1=box
def crop(im): return im[y0:y1,x0:x1]
ov=(ours*0.35+160*0.65).astype(np.uint8)
ov[a]=[255,170,0]; ov[ag]=[255,0,0]
tiles=[crop(ours).astype(np.uint8),crop(refs[0]).astype(np.uint8),crop(refs[2]).astype(np.uint8),crop(ov)]
im=np.concatenate([np.pad(t,((0,4),(0,4),(0,0)),constant_values=255) for t in tiles],axis=1)
Image.fromarray(im).resize((im.shape[1]*sc,im.shape[0]*sc),Image.NEAREST).save(out)
print(a.sum(),ag.sum(), crop(ag).sum())
