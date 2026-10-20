import numpy as np, math, sys
def cubic(p0,p1,p2,p3,n=200):
    t=np.linspace(0,1,n)[:,None]; p0,p1,p2,p3=map(np.array,(p0,p1,p2,p3))
    return (1-t)**3*p0+3*(1-t)**2*t*p1+3*(1-t)*t**2*p2+t**3*p3
def quad(p0,p1,p2,n=200):
    t=np.linspace(0,1,n)[:,None]; p0,p1,p2=map(np.array,(p0,p1,p2))
    return (1-t)**2*p0+2*(1-t)*t*p1+t**2*p2
def meanw(poly):
    x,y=poly[:,0],poly[:,1]; a=0.5*abs(np.sum(x*np.roll(y,-1)-np.roll(x,-1)*y)); per=np.sum(np.hypot(np.diff(x,append=x[0]),np.diff(y,append=y[0])))
    return a, per, 2*a/per
shapes={
 'lower_lip_546':[cubic((370,650),(400,720),(460,755),(512,756)),cubic((512,756),(564,755),(624,720),(654,650)),cubic((654,650),(635,705),(575,742),(512,743)),cubic((512,743),(449,742),(389,705),(370,650))],
 'upper_lip_448':[cubic((370,645),(410,615),(480,620),(512,625)),cubic((512,625),(544,620),(614,615),(654,645)),cubic((654,645),(625,635),(550,632),(512,635)),cubic((512,635),(474,632),(399,635),(370,645))],
 'nose_416':[quad((490,590),(512,605),(534,590)),quad((534,590),(512,598),(490,590))],
 'chin_219':[cubic((460,785),(475,825),(500,835),(512,835)),cubic((512,835),(524,835),(549,825),(564,785)),cubic((564,785),(539,795),(485,795),(460,785))],
 'sideburn_649':[cubic((330,460),(320,500),(330,540),(340,560)),cubic((340,560),(345,540),(340,500),(345,460))],
 'sideburn_652':[cubic((675,460),(685,500),(675,540),(665,560)),cubic((665,560),(660,540),(665,500),(660,460))],
}
for n,segs in shapes.items():
    poly=np.concatenate(segs)
    a,per,w=meanw(poly)
    print(f'{n:16s} area {a:8.1f} perim {per:7.1f} meanw svg {w:5.2f}  z2 {w*200/1024*2:5.2f}px  hd {w*1080/1024:5.2f}px')
# tip angle and sub-pixel run of the lower lip at its left cusp
o=cubic((370,650),(400,720),(460,755),(512,756),4000); i=cubic((370,650),(389,705),(449,742),(512,743),4000)
d0=o[1]-o[0]; d1=i[1]-i[0]
print('lower lip tip angle deg', math.degrees(abs(math.atan2(d0[1],d0[0])-math.atan2(d1[1],d1[0]))))
# width along the outer curve: distance from each outer point to the inner polyline
for sc,name in ((200/1024*2,'z2'),(1080/1024,'hd')):
    run=None
    for k in range(1,4000,5):
        dist=np.min(np.hypot(*(i-o[k]).T))*sc
        if dist>=1.0: run=np.hypot(*(o[k]-o[0]))*sc; break
    run15=None
    for k in range(1,4000,5):
        dist=np.min(np.hypot(*(i-o[k]).T))*sc
        if dist>=1.5: run15=np.hypot(*(o[k]-o[0]))*sc; break
    print(f'{name}: lower-lip tip narrower than 1 px for {run:.1f} px from the cusp, narrower than 1.5 px for {run15:.1f} px')
o=quad((490,590),(512,605),(534,590),4000); i=quad((490,590),(512,598),(534,590),4000)
d0=o[1]-o[0]; d1=i[1]-i[0]; print('nose tip angle', math.degrees(abs(math.atan2(d0[1],d0[0])-math.atan2(d1[1],d1[0]))))
for sc,name in ((200/1024*2,'z2'),(1080/1024,'hd')):
    for thr in (1.0,1.5):
        for k in range(1,4000,5):
            if np.min(np.hypot(*(i-o[k]).T))*sc>=thr: print(f' nose {name}: <{thr}px for {np.hypot(*(o[k]-o[0]))*sc:.1f}px'); break
