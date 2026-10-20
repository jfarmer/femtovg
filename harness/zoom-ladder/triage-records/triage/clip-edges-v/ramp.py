import sys, numpy as np
sys.path.insert(0,'.')
from cmp import *
from disc import disc_cov
key=sys.argv[1]; X=float(sys.argv[2]); Y=float(sys.argv[3]); RR=float(sys.argv[4])
yy,xx=np.mgrid[0:260,0:460]+0.5
for z in [0.5,1,1.5,2,3,4]:
    cx=230+z*(X-100); cy=130+z*(Y-100); r=RR*z
    d=np.hypot(xx-cx,yy-cy)-r
    ramp=np.clip(0.5-d,0,1)
    a=disc_cov(460,260,cx,cy,r)
    f=fem(key,z)[...,0]
    fa=1-f/255
    m=(np.abs(d)<2)
    pr=np.abs(255*(1-ramp)-f)
    ex=np.abs(255*(1-a)-f)
    ang=np.degrees(np.arctan2(yy-cy,xx-cx))%90
    bad=(ex>8)
    print(z,'fem vs ramp max',round(pr[m].max(),2),'mean',round(pr[m].mean(),3),'| fem vs exact max',round(ex.max(),1),'n>8',int(bad.sum()),'| angle-mod-90 of bad px:',np.histogram(ang[bad],bins=[0,15,30,60,75,90])[0])
