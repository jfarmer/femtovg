# score.py IMG ZOOMTAG : pixels beyond 8/255 against chr, ff, wk and the exact area, and max diffs
import sys, os, numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from exact import exact
K="wpt22__07-zero-area-collinear-fills__fill-path-subpixel-sliver-control"
base=os.path.expanduser("~/src/femtovg-wt/runs/zoom")
Z={"z1":1,"z125":1.25,"z15":1.5,"z175":1.75,"z2":2,"z3":3,"z4":4,"z075":0.75,"z05":0.5,"z033":0.33,"z025":0.25}
def load(p): return np.asarray(Image.open(p).convert("RGB")).astype(float)
def score(img, zt):
    out={}
    for b in ["chr","ff","wk"]:
        p=f"{base}/fresh/refs/{b}_{K}_{zt}.png"
        if os.path.exists(p):
            r=load(p); d=np.abs(img-r).max(axis=2); out[b]=(int((d>8).sum()), int(d.max()))
    e=255-exact(Z[zt])*255; d=np.abs(img[:,:,0]-e); out["exact"]=(int((d>8).sum()), int(d.max()))
    return out
if __name__=="__main__":
    print(sys.argv[1], score(load(sys.argv[1]), sys.argv[2]))
