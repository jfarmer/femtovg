import sys, numpy as np
from PIL import Image
L=lambda p: np.asarray(Image.open(p).convert('RGB'),dtype=np.int16)
R='/Users/matt/src/femtovg-wt/runs/busey'
K='corpus__buseybench__glm-5v-turbo'
def masks(ours, refs):
    off=[np.abs(ours-r).max(2)>20 for r in refs]; all3=off[0]&off[1]&off[2]
    sp=np.zeros(all3.shape,bool)
    for i in range(3):
        for j in range(i+1,3): sp|=np.abs(refs[i]-refs[j]).max(2)>20
    return all3, all3&~sp, sp
def load(fr, ours=None, refdir=f'{R}/refs', key=K):
    o=L(ours or f'{R}/png/mst4_{K}_{fr}.png'); refs=[L(f'{refdir}/{x}_{key}_{fr}.png') for x in ('chr','ff','wk')]
    return o, refs
if __name__=='__main__':
    fr=sys.argv[1]; cell=int(sys.argv[2]) if len(sys.argv)>2 else 16
    o,refs=load(fr); a,g,sp=masks(o,refs)
    idl=L(f'{R}/refs/id_{K}_{fr}.png')
    offid=np.abs(o-idl).max(2)>20
    print(fr,'all3',a.sum(),'agreed',g.sum(),'spread',sp.sum(),'frame',a.size, f'{100*a.mean():.4f}% {100*g.mean():.4f}%', 'all3&offid', (a&offid).sum())
    ys,xs=np.nonzero(a); d={}
    for y,x in zip(ys,xs):
        c=(y//cell,x//cell); d.setdefault(c,[0,0,0]); d[c][0]+=1; d[c][1]+=int(g[y,x]); d[c][2]+=int(offid[y,x])
    for c,v in sorted(d.items(),key=lambda kv:-kv[1][0])[:40]:
        print(f'  x{c[1]*cell}-{c[1]*cell+cell} y{c[0]*cell}-{c[0]*cell+cell}: all3 {v[0]} agreed {v[1]} offid {v[2]}')
    np.save(f'all3_{fr}.npy',a); np.save(f'ag_{fr}.npy',g)
