import numpy as np, sys
from PIL import Image
sys.path.insert(0,'scripts')
from red import red, L
R='/Users/matt/src/femtovg-wt/runs/busey/refs/%s_corpus__buseybench__gpt-6-astra_%s.png'
# determinism
for b,fr in [('chr','z2'),('chr','hd'),('wk','z2')]:
    a=L(f'o0/refs/{b}_v__v00_orig_{fr}.png'); c=L(R%(b,fr)); print('unpatched fresh vs corpus',b,fr,(a!=c).any(2).sum())
for fr in ['z2','hd']:
    o=L(f'png/mst4_v__v00_orig_{fr}.png')
    old=[L(R%(b,fr)) for b in ('chr','ff','wk')]
    new=[L(f'refs/{b}_v__v00_orig_{fr}.png') for b in ('chr','ff','wk')]
    ido=L(R%('id',fr)); idn=L(f'refs/id_v__v00_orig_{fr}.png')
    a0,s0=red(o,old); a1,s1=red(o,new)
    gone=a0&~a1; new_red=a1&~a0
    nearn=np.abs(o-idn).max(2)<=20; nearo=np.abs(o-ido).max(2)<=20
    print(fr,'red old',a0.sum(),'agreed',(a0&~s0).sum(),'red new',a1.sum(),'agreed',(a1&~s1).sum(),'gone',gone.sum(),'newly red',new_red.sum())
    print('   gone px: femtovg within 20 of capped id',(gone&nearn).sum(),'of butt id',(gone&nearo).sum())
    print('   chr-only off: old',(np.abs(o-old[0]).max(2)>20).sum(),'new',(np.abs(o-new[0]).max(2)>20).sum())
    print('   spread old',s0.mean()*100,'new',s1.mean()*100,' all3% old',a0.mean()*100,'new',a1.mean()*100,(a1&~s1).mean()*100)
    np.save(f'a_old_{fr}.npy',a0); np.save(f'a_new_{fr}.npy',a1)
