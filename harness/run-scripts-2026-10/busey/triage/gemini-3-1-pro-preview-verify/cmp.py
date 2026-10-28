import sys, numpy as np
from PIL import Image
V='/Users/matt/src/femtovg-wt/runs/busey/triage/gemini-3-1-pro-preview-verify'
L=lambda p: np.asarray(Image.open(p).convert('RGB'),dtype=np.int16)
for name in sys.argv[1:]:
    refs={b:L(f'{V}/refs/{b}_t__{name}_z2.png') for b in ('chr','ff','wk')}
    sp=np.zeros(refs['chr'].shape[:2],bool)
    ks=list(refs)
    for i in range(3):
        for j in range(i+1,3): sp|=np.abs(refs[ks[i]]-refs[ks[j]]).max(2)>20
    for b in ('mst2','vlin','vsrgb'):
        o=L(f'{V}/png/{b}_t__{name}_z2.png')
        off=[np.abs(o-r).max(2)>20 for r in refs.values()]
        a=off[0]&off[1]&off[2]
        print(f'{name:16s} {b:6s} all3 {a.sum():5d} agreed {(a&~sp).sum():5d}  vs chr>20 {off[0].sum():5d} ff {off[1].sum():5d} wk {off[2].sum():5d}  mean signed vs chr {(o-refs["chr"]).mean():+.2f}')
