import sys, numpy as np
from PIL import Image
L=lambda p: np.asarray(Image.open(p).convert('RGB'),dtype=np.int16)
k=sys.argv[2] if len(sys.argv)>2 else 'corpus__buseybench__gemini-3-7-flash'; fr=sys.argv[1] if len(sys.argv)>1 else 'z2'
pd=sys.argv[3] if len(sys.argv)>3 else 'png'; rd=sys.argv[4] if len(sys.argv)>4 else 'refs'
ours=L(f'{pd}/mst2_{k}_{fr}.png'); refs=[L(f'{rd}/{x}_{k}_{fr}.png') for x in ('chr','ff','wk')]
off=[np.abs(ours-r).max(2)>20 for r in refs]
all3=off[0]&off[1]&off[2]
spread=np.zeros(all3.shape,bool)
for i in range(3):
  for j in range(i+1,3): spread|=np.abs(refs[i]-refs[j]).max(2)>20
ag=all3&~spread
print('all3',all3.sum(),'agreed',ag.sum(),'spread',spread.sum(), 'vs chr', off[0].sum())
# simple flood-fill labelling with 8px dilation
H,W=ag.shape
ys,xs=np.nonzero(all3)
pts=list(zip(ys,xs)); seen=set(); groups=[]
P=set(pts)
for p in pts:
  if p in seen: continue
  st=[p]; seen.add(p); g=[]
  while st:
    y,x=st.pop(); g.append((y,x))
    for q in P:
      pass
    break
# cheaper: grid cluster
cell=int(sys.argv[5]) if len(sys.argv)>5 else 16
d={}
for y,x in zip(ys,xs):
  c=(y//cell,x//cell); d.setdefault(c,[0,0]); d[c][0]+=1; d[c][1]+=int(ag[y,x])
for c,v in sorted(d.items(),key=lambda kv:-kv[1][0])[:40]:
  print(f'cell x{c[1]*cell}-{c[1]*cell+cell} y{c[0]*cell}-{c[0]*cell+cell}: all3 {v[0]} agreed {v[1]}')
np.save(f'triage/gemini-3-7-flash/all3_{fr}.npy',all3); np.save(f'triage/gemini-3-7-flash/ag_{fr}.npy',ag)
