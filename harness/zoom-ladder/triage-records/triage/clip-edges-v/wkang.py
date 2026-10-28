import sys, numpy as np
sys.path.insert(0,'.')
from cmp import *
from disc import disc_cov
key='corpus__wpt-clip-path-reftests__clip-path-variation-28'; X,Y=110,95
yy,xx=np.mgrid[0:260,0:460]+0.5
for z in [1.25,1.5,1.75,2,3,4]:
    cx=230+z*(X-100); cy=130+z*(Y-100); r=25*z
    a=disc_cov(460,260,cx,cy,r,n=256)
    ex=255*(1-a)
    ang=np.degrees(np.arctan2(yy-cy,xx-cx))%90
    line=[]
    for n,im in [('fem',fem(key,z)),('wk',ref('wk',key,z)),('pat',load(f'png/area/{key}/{z}.png'))]:
        d=np.abs(im[...,0]-ex); bad=d>8
        line.append(f"{n} {int(bad.sum())} " + str(np.histogram(ang[bad],bins=[0,15,30,60,75,90])[0].tolist()))
    f=fem(key,z); w=ref('wk',key,z); bad=np.abs(f[...,:3]-w[...,:3]).max(-1)>8
    # classify fem-vs-wk bad px by whose error is larger
    ef=np.abs(f[...,0]-ex); ew=np.abs(w[...,0]-ex)
    print(z,' | '.join(line),'| fem-vs-wk bad',int(bad.sum()),'fem err larger',int((bad&(ef>ew)).sum()),'wk err larger',int((bad&(ew>=ef)).sum()))
