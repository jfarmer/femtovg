import sys, numpy as np
sys.path.insert(0,'.')
from cmp import *
from disc import disc_cov
key=sys.argv[1] if len(sys.argv)>1 else 'corpus__wpt-clip-path-reftests__clip-path-variation-28'
X,Y=110,95
yy,xx=np.mgrid[0:260,0:460]+0.5
for z in [1.25,1.5,1.75,2]:
    cx=230+z*(X-100); cy=130+z*(Y-100); r=25*z
    a=disc_cov(460,260,cx,cy,r,n=256)
    d=np.hypot(xx-cx,yy-cy)-r
    ang=np.degrees(np.arctan2(yy-cy,xx-cx))%90
    f=1-fem(key,z)[...,0]/255; w=1-ref('wk',key,z)[...,0]/255
    ef=(f-a)*255; ew=(w-a)*255
    bad=np.abs(fem(key,z)[...,:3]-ref('wk',key,z)[...,:3]).max(-1)>8
    same=bad&(np.sign(ef)==np.sign(ew))&(np.abs(ef)>2)&(np.abs(ew)>2)
    opp=bad&(np.sign(ef)!=np.sign(ew))&(np.abs(ef)>2)&(np.abs(ew)>2)
    print(z,'fem-vs-wk bad',int(bad.sum()),'diag(30-60)',int((bad&(ang>30)&(ang<60)).sum()),'both err same sign',int(same.sum()),'opposite',int(opp.sum()),
          'only fem err>2',int((bad&(np.abs(ew)<=2)).sum()),'only wk err>2',int((bad&(np.abs(ef)<=2)).sum()))
    # WK error vs distance profile on diagonals
    m=(ang>35)&(ang<55)&(np.abs(d)<1)
    for lo in np.arange(-1,1,0.25):
        mm=m&(d>=lo)&(d<lo+0.25)
        if mm.sum(): print('   d %+.2f..%+.2f  fem %+5.1f  wk %+5.1f  n=%d'%(lo,lo+.25,ef[mm].mean(),ew[mm].mean(),mm.sum()))
