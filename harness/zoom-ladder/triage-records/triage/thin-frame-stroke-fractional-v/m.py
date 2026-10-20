import sys, numpy as np, itertools
from PIL import Image
d='out'
def L(t,n,z):
    try: return np.asarray(Image.open(f'{d}/{t}_{n}_z{z}.png').convert('RGB'),dtype=int)
    except FileNotFoundError: return None
for n in sys.argv[1].split(','):
  for z in ['1','0.75','0.5','0.33','0.25']:
    ims={t:L(t,n,z) for t in ['fv','chr','ff','wk','area']}
    ims={k:v for k,v in ims.items() if v is not None}
    y0=130-100*float(z); rows=list(range(int(np.floor(y0))-1,int(np.floor(y0))+3))
    s=f'{n} z={z} rows {rows}: '+' '.join(f"{t}={[round(1-v[r,230,0]/255,3) for r in rows]}" for t,v in ims.items())
    print(s)
    pr=[]
    for a,b in itertools.combinations(ims,2):
        pr.append(f'{a}-{b}:{int((np.abs(ims[a]-ims[b]).max(axis=2)>8).sum())}')
    print('   n8', ' '.join(pr))
