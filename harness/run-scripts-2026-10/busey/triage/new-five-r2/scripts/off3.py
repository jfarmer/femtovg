"""off3.py [names...] [fr=z2] [pd=DIR] [rd=DIR] [build=mst4] [cell=16] : off-all-three pixels, clusters"""
import sys, os, numpy as np
from PIL import Image
L=lambda p: np.asarray(Image.open(p).convert('RGB'),dtype=np.int16)
a=dict(x.split('=',1) for x in sys.argv[1:] if '=' in x)
names=[x for x in sys.argv[1:] if '=' not in x]
fr=a.get('fr','z2'); pd=a.get('pd','/Users/matt/src/femtovg-wt/runs/busey/png'); rd=a.get('rd','/Users/matt/src/femtovg-wt/runs/busey/refs')
b=a.get('build','mst4'); cell=int(a.get('cell',16)); pre=a.get('pre','corpus__buseybench__')
def masks(k):
    o=L(f'{pd}/{b}_{k}_{fr}.png'); refs=[L(f'{rd}/{x}_{k}_{fr}.png') for x in ('chr','ff','wk')]
    off=[np.abs(o-r).max(2)>20 for r in refs]; all3=off[0]&off[1]&off[2]
    sp=np.zeros(all3.shape,bool)
    for i in range(3):
        for j in range(i+1,3): sp|=np.abs(refs[i]-refs[j]).max(2)>20
    idp=f'{rd}/id_{k}_{fr}.png'
    offid=np.abs(o-L(idp)).max(2)>20 if os.path.exists(idp) else None
    return o,refs,all3,sp,offid
if __name__=='__main__':
  for n in names:
    k=pre+n
    o,refs,all3,sp,offid=masks(k)
    ag=all3&~sp
    print(f'== {n} {fr}: all3 {all3.sum()} agreed {ag.sum()} spread {sp.sum()} offid {None if offid is None else offid.sum()} all3&offid {None if offid is None else (all3&offid).sum()}')
    ys,xs=np.nonzero(all3); d={}
    for y,x in zip(ys,xs):
        c=(y//cell,x//cell); d.setdefault(c,[0,0,0]); d[c][0]+=1; d[c][1]+=int(ag[y,x]); d[c][2]+=int(offid[y,x]) if offid is not None else 0
    for c,v in sorted(d.items(),key=lambda kv:-kv[1][0])[:int(a.get('top',25))]:
        print(f'  x{c[1]*cell}-{c[1]*cell+cell} y{c[0]*cell}-{c[0]*cell+cell}: all3 {v[0]} agreed {v[1]} offid {v[2]}')
