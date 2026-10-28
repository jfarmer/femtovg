import numpy as np
def bez(P,t):
  P=np.array(P,float); t=np.asarray(t)[:,None]
  return (1-t)**3*P[0]+3*(1-t)**2*t*P[1]+3*(1-t)*t*t*P[2]+t**3*P[3]
segs=[[(250,600),(240,450),(270,200),(512,125)],[(512,125),(754,200),(784,450),(774,600)],[(774,600),(760,550),(750,350),(730,280)],[(730,280),(700,200),(620,160),(512,155)],[(512,155),(404,160),(324,200),(294,280)],[(294,280),(274,350),(264,550),(250,600)]]
ts=np.linspace(0,1,4001)
poly=np.concatenate([bez(s,ts)[:-1] for s in segs])
# signed area (shoelace)
x,y=poly[:,0],poly[:,1]
print('signed area', 0.5*np.sum(x*np.roll(y,-1)-np.roll(x,-1)*y))
# intersections between segment 0 and segs 4,5
from itertools import product
def inter(A,B):
  out=[]
  for i in range(len(A)-1):
    p,r=A[i],A[i+1]-A[i]
    q=B[:-1]; s=B[1:]-B[:-1]
    den=r[0]*s[:,1]-r[1]*s[:,0]
    with np.errstate(divide='ignore',invalid='ignore'):
      t=((q[:,0]-p[0])*s[:,1]-(q[:,1]-p[1])*s[:,0])/den
      u=((q[:,0]-p[0])*r[1]-(q[:,1]-p[1])*r[0])/den
    k=np.where((t>=0)&(t<1)&(u>=0)&(u<1))[0]
    for kk in k: out.append(tuple(np.round(p+t[kk]*r,2)))
  return out
b0=bez(segs[0],ts)
for j in (4,5):
  print('outer-left x seg',j, inter(b0,bez(segs[j],ts)))
# winding number at sample points
def wind(pt):
  w=0
  for i in range(len(poly)):
    a=poly[i]-pt; b=poly[(i+1)%len(poly)]-pt
    if a[1]<=0<b[1] and a[0]*b[1]-a[1]*b[0]>0: w+=1
    elif b[1]<=0<a[1] and a[0]*b[1]-a[1]*b[0]<0: w-=1
  return w
for pt in [(316,256),(330,256),(300,256),(512,140),(285,450),(250,500),(272,450)]:
  print(pt, wind(np.array(pt,float)))
