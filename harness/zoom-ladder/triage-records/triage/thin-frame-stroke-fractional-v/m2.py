import sys, numpy as np, itertools
from PIL import Image
def L(t,n,z):
    try: return np.asarray(Image.open(f'out/{t}_{n}_z{z}.png').convert('RGB'),dtype=int)
    except FileNotFoundError: return None
for n in sys.argv[1].split(','):
  for z in sys.argv[2].split(','):
    ims={t:L(t,n,z) for t in ['fv','von','chr','ff','wk','area']}; ims={k:v for k,v in ims.items() if v is not None}
    col=ims['area'][:,230,0]; rows=np.where(col<250)[0]
    rows=sorted(set(r for r0 in rows for r in (r0-1,r0,r0+1)))
    print(f'{n} z{z} col 230 rows {rows}')
    for t,v in ims.items(): print(f'   {t:5}', [round(1-v[r,230,0]/255,3) for r in rows])
    print('   n8', ' '.join(f'{a}-{b}:{int((np.abs(ims[a]-ims[b]).max(axis=2)>8).sum())}' for a,b in itertools.combinations(ims,2)))
