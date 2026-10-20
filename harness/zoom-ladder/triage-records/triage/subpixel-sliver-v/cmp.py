import sys, numpy as np
from PIL import Image
def load(p):
    im = Image.open(p)
    if im.mode == 'RGBA':
        a = np.asarray(im).astype(float)
        # composite on white
        al = a[...,3:4]/255.0
        rgb = a[...,:3]*al + 255*(1-al)
        return rgb
    return np.asarray(im.convert('RGB')).astype(float)
def cmp(a, b, t=8):
    d = np.abs(load(a) - load(b)).max(axis=2)
    return int((d > t).sum()), int(d.max())
if __name__ == '__main__':
    for b in sys.argv[2:]:
        print(b.split('/')[-1], cmp(sys.argv[1], b))
