"""split_p60.py IN OUT: replaces muse-spark-1-3-contributor's self-crossing hair-band path (line 60) by the five
regions it fills - the top band, the two side lobes (wound against the rest) and the two bottom tips - each its
own <path>, cut at the crossings, same fill. The regions only touch at the four crossing points, so the picture
is the same in every browser."""
import sys, numpy as np
def bez(P,t):
    P=np.array(P,float); t=np.atleast_1d(t)[:,None]
    return (1-t)**3*P[0]+3*(1-t)**2*t*P[1]+3*(1-t)*t*t*P[2]+t**3*P[3]
def split(P,t):
    P=[np.array(p,float) for p in P]
    a=P[0]+(P[1]-P[0])*t; b=P[1]+(P[2]-P[1])*t; c=P[2]+(P[3]-P[2])*t
    d=a+(b-a)*t; e=b+(c-b)*t; f=d+(e-d)*t
    return [P[0],a,d,f],[f,e,c,P[3]]
def sub(P,t0,t1):
    if t0>0: P=split(P,t0)[1]
    if t1<1: P=split(P,(t1-t0)/(1-t0))[0]
    return [np.array(p,float) for p in P]
def rev(P): return P[::-1]
def cross(A,B):
    ts=np.linspace(0,1,20001); a=bez(A,ts); b=bez(B,ts)
    best=None
    for i in range(0,len(ts)-1,1):
        pass
    # coarse: closest pair then refine by Newton on the two parameters
    from itertools import product
    # first proper crossing of the two polylines, away from shared endpoints
    s=t=None
    for i in range(len(a)-1):
        p,r=a[i],a[i+1]-a[i]; q=b[:-1]; w=b[1:]-b[:-1]
        den=r[0]*w[:,1]-r[1]*w[:,0]
        with np.errstate(divide='ignore',invalid='ignore'):
            u=((q[:,0]-p[0])*w[:,1]-(q[:,1]-p[1])*w[:,0])/den
            v=((q[:,0]-p[0])*r[1]-(q[:,1]-p[1])*r[0])/den
        k=np.where((u>=0)&(u<1)&(v>=0)&(v<1))[0]
        k=[kk for kk in k if 0.001<ts[i]<0.999 and 0.001<ts[kk]<0.999]
        if k: s,t=ts[i],ts[k[0]]; break
    for _ in range(50):
        pa=bez(A,s)[0]; pb=bez(B,t)[0]; h=1e-6
        da=(bez(A,s+h)[0]-pa)/h; db=(bez(B,t+h)[0]-pb)/h
        J=np.array([da,-db]).T; r=pa-pb
        ds,dt=np.linalg.solve(J,-r); s+=ds; t+=dt
    return s,t
O=[(250,600),(240,450),(270,200),(512,125)]; RO=[(512,125),(754,200),(784,450),(774,600)]
RIL=[(774,600),(760,550),(750,350),(730,280)]; RIU=[(730,280),(700,200),(620,160),(512,155)]
IU=[(512,155),(404,160),(324,200),(294,280)]; IL=[(294,280),(274,350),(264,550),(250,600)]
sOB,tIU=cross(O,IU); sOA,tIL=cross(O,IL); sROB,tRIU=cross(RO,RIU); sROA,tRIL=cross(RO,RIL)
print('crossings', bez(O,sOB)[0], bez(O,sOA)[0], bez(RO,sROB)[0], bez(RO,sROA)[0], file=sys.stderr)
f=lambda p: f'{p[0]:.4f},{p[1]:.4f}'
def d(curves):
    s='M'+f(curves[0][0])
    for c in curves: s+=' C'+' '.join(f(p) for p in c[1:])
    return s+' Z'
regions={
 'top band': [sub(O,sOB,1), sub(RO,0,sROB), sub(RIU,tRIU,1), sub(IU,0,tIU)],
 'left lobe': [sub(O,sOA,sOB), sub(IU,tIU,1), sub(IL,0,tIL)],
 'left tip': [sub(O,0,sOA), sub(IL,tIL,1)],
 'right lobe': [sub(RO,sROB,sROA), sub(RIL,tRIL,1), sub(RIU,0,tRIU)],
 'right tip': [sub(RO,sROA,1), sub(RIL,0,tRIL)],
}
only=sys.argv[3].split(',') if len(sys.argv)>3 else list(regions)
paths='\n'.join(f'<path d="{d(regions[k])}" fill="#d8c7a5"/><!-- {k} -->' for k in only)
src=open(sys.argv[1]).read()
old=[l for l in src.split('\n') if l.startswith('<path d="M250,600 C240,450 270,200 512,125')][0]
open(sys.argv[2],'w').write(src.replace(old,paths))
