import sys, numpy as np
from PIL import Image
R='/Users/matt/src/femtovg-wt/runs/zoom/'
def load(p):
    try: return np.asarray(Image.open(p).convert('RGBA')).astype(int)
    except FileNotFoundError: return None
def frames(key, fr):
    fv = load(f'{R}png/zl_zm_svg/{key}/fresh_{fr}.png') if fr!='z1' else load(f'{R}png/zl_zm_svg/{key}/00.png')
    out={'fv':fv}
    for b in ('chr','ff','wk'):
        out[b]=load(f'{R}fresh/refs/{b}_{key}_{fr}.png')
        out[b+'_ref']=load(f'{R}fresh/refs/{b}_{key}-ref_{fr}.png')
    return out
def bad(a,b):
    d=np.abs(a[...,:3]-b[...,:3]).max(-1)
    return d>8, d
if __name__=='__main__':
    key=sys.argv[1]; fr=sys.argv[2]
    F=frames(key,fr)
    names=[k for k in F if F[k] is not None]
    print('have',names)
    for a in names:
        for b in names:
            if a<b:
                m,d=bad(F[a],F[b])
                ys,xs=np.nonzero(m)
                bb=(xs.min(),ys.min(),xs.max(),ys.max()) if len(xs) else None
                print(f'{a:8s} vs {b:8s}: {m.sum():5d} bbox={bb}')

def rows(key, fr, y, x0, x1, ch=1, names=('fv','chr','ff','wk')):
    F=frames(key,fr)
    for n in names:
        if F[n] is None: continue
        print(f'{n:5s}', ' '.join(f'{v:3d}' for v in F[n][y,x0:x1,ch]))
def cols(key, fr, x, y0, y1, ch=1, names=('fv','chr','ff','wk')):
    F=frames(key,fr)
    for n in names:
        if F[n] is None: continue
        print(f'{n:5s}', ' '.join(f'{v:3d}' for v in F[n][y0:y1,x,ch]))

def show(key, fr, area, y=None, x=None, rng=(0,0), ch=1):
    F=frames(key,fr); F['area']=load(area) if area else None
    for n in ('fv','chr','ff','wk','area'):
        if F.get(n) is None: continue
        v = F[n][y, rng[0]:rng[1], ch] if y is not None else F[n][rng[0]:rng[1], x, ch]
        print(f'{n:5s}', ' '.join(f'{int(t):3d}' for t in v))
