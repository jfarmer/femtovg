import sys, numpy as np
from PIL import Image
R='/Users/matt/src/femtovg-wt/runs/busey'
L=lambda p: np.asarray(Image.open(p).convert('RGB'),dtype=np.int16)
for n in ['claude-opus-5-5','claude-sonnet-5-5','gpt-6-1-sol','gpt-6-1-sol-pro','pareto']:
    k='corpus__buseybench__'+n
    for fr in ('z2','hd'):
        o=L(f'{R}/png/mst4_{k}_{fr}.png'); rs=[L(f'{R}/refs/{b}_{k}_{fr}.png') for b in ('chr','ff','wk')]; idr=L(f'{R}/refs/id_{k}_{fr}.png')
        off=[np.abs(o-r).max(2)>20 for r in rs]; a3=off[0]&off[1]&off[2]
        sp=np.zeros(a3.shape,bool)
        for i in range(3):
            for j in range(i+1,3): sp|=np.abs(rs[i]-rs[j]).max(2)>20
        oi=np.abs(o-idr).max(2)>20
        print(n,fr,'all3',a3.sum(),'agree',(a3&~sp).sum(),'all3&offarea',(a3&oi).sum(),'all3&onarea',(a3&~oi).sum())
