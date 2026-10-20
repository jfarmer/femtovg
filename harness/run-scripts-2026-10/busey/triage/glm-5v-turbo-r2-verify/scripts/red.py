import sys, numpy as np
from PIL import Image
L=lambda p: np.asarray(Image.open(p).convert('RGB'),dtype=np.int16)
R='/Users/matt/src/femtovg-wt/runs/busey'; K='corpus__buseybench__glm-5v-turbo'
S={'z2':(30.0,-70.0,0.390625),'hd':(420.0,0.0,1080/1024),'z1':(130.0,30.0,200/1024)}
def to_svg(fr,x,y):
    ox,oy,s=S[fr]; return ((x+0.5-ox)/s,(y+0.5-oy)/s)
def refs(fr, key=K, rd=f'{R}/refs'):
    return [L(f'{rd}/{x}_{key}_{fr}.png') for x in ('chr','ff','wk','id')]
def masks(o, rf):
    off=[np.abs(o-r).max(2)>20 for r in rf[:3]]; a=off[0]&off[1]&off[2]
    sp=np.zeros(a.shape,bool)
    for i in range(3):
        for j in range(i+1,3): sp|=np.abs(rf[i]-rf[j]).max(2)>20
    offid=np.abs(o-rf[3]).max(2)>20
    return a, a&~sp, sp, offid
def comps(m, rad=3):
    # cluster by flood fill within chebyshev distance rad
    ys,xs=np.nonzero(m); pts=list(zip(ys,xs)); lab={}; c=0
    S2=set(pts)
    for p in pts:
        if p in lab: continue
        st=[p]; lab[p]=c
        while st:
            y,x=st.pop()
            for dy in range(-rad,rad+1):
                for dx in range(-rad,rad+1):
                    q=(y+dy,x+dx)
                    if q in S2 and q not in lab: lab[q]=c; st.append(q)
        c+=1
    out={}
    for p,l in lab.items(): out.setdefault(l,[]).append(p)
    return list(out.values())
