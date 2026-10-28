import sys, numpy as np
from PIL import Image
L=lambda p: np.asarray(Image.open(p).convert('RGB'),dtype=np.int16)
RB='/Users/matt/src/femtovg-wt/runs/busey/refs'; K='corpus__buseybench__gemini-3-8-flash'
def masks(ours, refs):
    off=[np.abs(ours-r).max(2)>20 for r in refs]; all3=off[0]&off[1]&off[2]
    sp=np.zeros(all3.shape,bool)
    for i in range(3):
        for j in range(i+1,3): sp|=np.abs(refs[i]-refs[j]).max(2)>20
    return all3, all3&~sp, sp, off
def load_refs(key=K, fr='z2', rd=RB):
    return [L(f'{rd}/{x}_{key}_{fr}.png') for x in ('chr','ff','wk')]
if __name__=='__main__':
    fr=sys.argv[1]; ours=L(sys.argv[2]); refs=load_refs(fr=fr) if len(sys.argv)<4 else load_refs(sys.argv[3],fr,sys.argv[4])
    all3,ag,sp,off=masks(ours,refs)
    print('all3',all3.sum(),'agreed',ag.sum(),'spread',sp.sum(),'vs chr/ff/wk',[int(o.sum()) for o in off])
    idr=L(f'{RB}/id_{K}_{fr}.png') if len(sys.argv)<4 else None
    cell=int(sys.argv[5]) if len(sys.argv)>5 else 16
    d={}
    ys,xs=np.nonzero(all3)
    for y,x in zip(ys,xs):
        c=(y//cell,x//cell); d.setdefault(c,[0,0]); d[c][0]+=1; d[c][1]+=int(ag[y,x])
    for c,v in sorted(d.items(),key=lambda kv:-kv[1][0])[:40]:
        print(f'cell x{c[1]*cell}-{c[1]*cell+cell} y{c[0]*cell}-{c[0]*cell+cell}: all3 {v[0]} agreed {v[1]}')
    np.save(f'all3_{fr}.npy',all3); np.save(f'ag_{fr}.npy',ag)
