import sys,glob,numpy as np
from PIL import Image
fs=sorted(glob.glob(sys.argv[1]))
im=[np.asarray(Image.open(f).convert('RGB')).astype(int) for f in fs]
moves=[]
for i in range(1,len(im)):
    d=np.abs(im[i]-im[i-1]).max(axis=2); moves.append((int((d>0).sum()),int((d>8).sum()),int(d.max())))
last=im[-1]
settle=None
for i in range(len(im)):
    if all((im[j]==last).all() for j in range(i,len(im))): settle=i;break
print("frames",len(im),"settles at",settle)
print("moves (diff,n8,max) per step:",moves[:6],"...",moves[max(0,settle-3) if settle else 0:(settle or 0)+1])
