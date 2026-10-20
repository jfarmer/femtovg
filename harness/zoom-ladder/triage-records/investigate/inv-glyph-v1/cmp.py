import numpy as np, sys, os
from PIL import Image
def L(p): return np.asarray(Image.open(p)).astype(int)
def d(a,b):
    x=np.abs(a-b).max(2); return int((x>0).sum()), int(x.max())
cases=['s0.625_tx167','s0.625_tx167.25','s0.625_tx167.5','s0.625_tx167.75','s0.625_ty5.5','s1_tx100','s1_tx100.5']
vars_=['base','bp','bm','res7,7','res33,5','res100,3','res7,7bp','res33,5bp','res100,3bp']
print('%-18s'%'case', ' '.join('%-22s'%v for v in vars_))
for c in cases:
    row=[]
    for v in vars_:
        f=L(f'{v}/fresh_{c}.ppm')
        a=d(f,L(f'{v}/ladS0.5_{c}.ppm')); b=d(f,L(f'{v}/ladOther_{c}.ppm'))
        row.append('S%d/%d O%d/%d'%(a+b))
    print('%-18s'%c,' '.join('%-22s'%r for r in row))
print()
print('fresh vs base fresh (cell moved by pre-reservation, no history):')
for c in cases:
    f=L(f'base/fresh_{c}.ppm')
    print('%-18s'%c, ' '.join('%s:%d/%d'%((v,)+d(f,L(f'{v}/fresh_{c}.ppm'))) for v in ['res7,7','res33,5','res100,3']))
print()
print('bias variants vs base at integral translation (should be identical if bias only matters at ties):')
for c in ['s0.625_tx167','s1_tx100']:
    for k in ['fresh','ladS0.5','ladOther']:
        f=L(f'base/{k}_{c}.ppm')
        print(c,k,'bp',d(f,L(f'bp/{k}_{c}.ppm')),'bm',d(f,L(f'bm/{k}_{c}.ppm')))
