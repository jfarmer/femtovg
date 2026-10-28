import sys, numpy as np
from PIL import Image
R='/Users/matt/src/femtovg-wt/runs/zoom/fresh/refs/'
FR={1:'z1',1.25:'z125',1.5:'z15',1.75:'z175',2:'z2',3:'z3',4:'z4',0.75:'z075',0.5:'z05',0.33:'z033',0.25:'z025'}
ppm,key,z=sys.argv[1],sys.argv[2],float(sys.argv[3])
a=np.asarray(Image.open(ppm).convert('RGB'),dtype=int)
out=[]
for b in ['chr','ff','wk']:
    try: o=np.asarray(Image.open(f'{R}{b}_{key}_{FR[z]}.png').convert('RGB'),dtype=int)
    except FileNotFoundError: out.append(f'{b}=-'); continue
    out.append(f'{b}={(np.abs(a-o).max(2)>8).sum()}')
print(ppm, z, ' '.join(out))
