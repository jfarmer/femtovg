"""Write svg/mu_split.svg: line 60 of muse replaced by its five non-self-crossing regions (my own construction)."""
import numpy as np
segs=[((250,600),(240,450),(270,200),(512,125)),((512,125),(754,200),(784,450),(774,600)),
((774,600),(760,550),(750,350),(730,280)),((730,280),(700,200),(620,160),(512,155)),
((512,155),(404,160),(324,200),(294,280)),((294,280),(274,350),(264,550),(250,600))]
segs=[np.array(s,float) for s in segs]
def ev(s,t):
    t=np.asarray(t)[...,None]; return (1-t)**3*s[0]+3*(1-t)**2*t*s[1]+3*(1-t)*t**2*s[2]+t**3*s[3]
def cross(a,b,excl=False):
    # minimize distance between curves a(t), b(u) with grid + Newton refinement
    T=np.linspace(0,1,2001); A=ev(a,T); B=ev(b,T)
    d=np.linalg.norm(A[:,None]-B[None],axis=2)
    res=[]
    # local minima below 0.5
    for i,j in zip(*np.where(d<0.6)):
        if excl and (T[i]<0.05 or T[j]>0.95 or T[j]<0.05 and T[i]>0.95): continue
        if excl and (min(T[i],T[j])<0.05 or max(T[i],T[j])>0.95): continue
        res.append((d[i,j],T[i],T[j]))
    res.sort()
    t,u=res[0][1],res[0][2]
    for _ in range(50):
        h=1e-7
        F=ev(a,t)-ev(b,u)
        Ja=(ev(a,t+h)-ev(a,t-h))/(2*h); Jb=-(ev(b,u+h)-ev(b,u-h))/(2*h)
        J=np.c_[Ja,Jb]; dt=np.linalg.solve(J,-F); t+=dt[0]; u+=dt[1]
    return t,u,ev(a,t)
def split(s,t):
    a,b,c,d=s
    ab=a+(b-a)*t; bc=b+(c-b)*t; cd=c+(d-c)*t; abc=ab+(bc-ab)*t; bcd=bc+(cd-bc)*t; m=abc+(bcd-abc)*t
    return np.array([a,ab,abc,m]),np.array([m,bcd,cd,d])
def sub(s,t0,t1):
    _,r=split(s,t0); 
    if t1>=1: return r
    l,_=split(r,(t1-t0)/(1-t0)); return l
tA0,tA4,A=cross(segs[0],segs[4]); tB0,tB5,B=cross(segs[0],segs[5],True)
tA1,tA3,A2=cross(segs[1],segs[3]); tB1,tB2,B2=cross(segs[1],segs[2],True)
print('A',A,tA0,tA4,'B',B,tB0,tB5,'A2',A2,'B2',B2)
fmt=lambda p:f'{p[0]:.4f},{p[1]:.4f}'
def C(s): return f' C{fmt(s[1])} {fmt(s[2])} {fmt(s[3])}'
def rev(s): return s[::-1]
paths=[]
# top band: A -> seg0[tA0,1] -> seg1[0,tA1] -> seg3[tA3,1] -> seg4[0,tA4]
paths.append('M'+fmt(A)+C(sub(segs[0],tA0,1))+C(sub(segs[1],0,tA1))+C(sub(segs[3],tA3,1))+C(sub(segs[4],0,tA4))+' Z')
# left lobe: B -> seg0[tB0,tA0] -> seg4[tA4,1] -> seg5[0,tB5]
paths.append('M'+fmt(B)+C(sub(segs[0],tB0,tA0))+C(sub(segs[4],tA4,1))+C(sub(segs[5],0,tB5))+' Z')
# left tip: (250,600) -> seg0[0,tB0] -> seg5[tB5,1]
paths.append('M250,600'+C(sub(segs[0],0,tB0))+C(sub(segs[5],tB5,1))+' Z')
# right lobe: A2 -> seg1[tA1,tB1] -> seg2[tB2,1] -> seg3[0,tA3]
paths.append('M'+fmt(A2)+C(sub(segs[1],tA1,tB1))+C(sub(segs[2],tB2,1))+C(sub(segs[3],0,tA3))+' Z')
# right tip: B2 -> seg1[tB1,1] -> seg2[0,tB2]
paths.append('M'+fmt(B2)+C(sub(segs[1],tB1,1))+C(sub(segs[2],0,tB2))+' Z')
lines=open('svg/mu_orig.svg').read().split('\n')
assert lines[59].startswith('<path d="M250,600 C240,450')
lines[59]='\n'.join(f'<path d="{d}" fill="#d8c7a5"/>' for d in paths)
open('svg/mu_split.svg','w').write('\n'.join(lines))
# also a minimal: background + path 59 + path 60 / split
hdr='\n'.join(lines[:2])
