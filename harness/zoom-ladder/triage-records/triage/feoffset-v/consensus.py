import json, numpy as np
from PIL import Image
R='/Users/matt/src/femtovg-wt/runs/zoom/'
FR={0.25:'z025',0.33:'z033',0.5:'z05',0.75:'z075',1.25:'z125',1.5:'z15',1.75:'z175',3:'z3'}
def L(p):
    try: return np.asarray(Image.open(p).convert('RGB')).astype(int)
    except Exception: return None
cl=json.load(open(R+'triage/clusters_compact.json'))['feoffset']
over=[]
for e in cl:
    k=e['key']; worst=0; det=[]
    for b in e['bad']:
        z=b[0]; fr=FR[z]
        fv=L(f"{R}png/zl_zm_svg/{k}/fresh_{fr}.png")
        B={x:L(f"{R}fresh/refs/{x}_{k}_{fr}.png") for x in ('chr','ff','wk')}
        B={x:v for x,v in B.items() if v is not None}
        d=lambda a,c: np.abs(a-c).max(-1)>8
        m=np.ones(fv.shape[:2],bool)
        for v in B.values(): m&=d(fv,v)
        ks=list(B)
        for i in range(len(ks)):
            for j in range(i+1,len(ks)): m&=~d(B[ks[i]],B[ks[j]])
        c=int(m.sum()); det.append((z,c,len(B))); worst=max(worst,c)
    if worst>24: over.append(k)
    print(f"{k[:90]:90s} {worst:4d} {det}")
print(len(over),'entries >24:'); [print(' ',o) for o in over]
