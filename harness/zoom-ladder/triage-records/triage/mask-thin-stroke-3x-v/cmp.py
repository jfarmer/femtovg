import sys, numpy as np
from PIL import Image
def load(p):
    im = Image.open(p).convert('RGBA')
    a = np.asarray(im).astype(np.int32)
    # composite on white
    rgb = a[...,:3]; al = a[...,3:4]
    return (rgb*al + 255*(255-al)) // 255 if (al<255).any() else rgb
def cnt(a,b,th=8):
    d = np.abs(a-b).max(axis=2)
    return int((d>th).sum()), d
if __name__=='__main__':
    a=load(sys.argv[1]); b=load(sys.argv[2])
    n,d=cnt(a,b); print(n, int(d.max()))
