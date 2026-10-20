import sys, numpy as np
from PIL import Image
Z=[1,1.25,1.5,1.75,2,3,4,3,2,1.75,1.5,1.25,1,0.75,0.5,0.33,0.25,0.33,0.5,0.75,1]
TAG={1:'z1',1.25:'z125',1.5:'z15',1.75:'z175',2:'z2',3:'z3',4:'z4',0.75:'z075',0.5:'z05',0.33:'z033',0.25:'z025'}
R='/Users/matt/src/femtovg-wt/runs/zoom/'
def load(p):
    try: return np.asarray(Image.open(p).convert('RGBA')).astype(np.int32)
    except FileNotFoundError: return None
def fem(key,z):
    return load(R+f'png/zl_zm_svg/{key}/{Z.index(z):02d}.png')
def ref(b,key,z):
    return load(R+f'fresh/refs/{b}_{key}_{TAG[z]}.png')
def beyond(a,b,t=8):
    if a is None or b is None: return None
    return int((np.abs(a[...,:3]-b[...,:3]).max(-1)>t).sum())
if __name__=='__main__':
    key=sys.argv[1]
    for z in sorted(TAG):
        f=fem(key,z); r={b:ref(b,key,z) for b in ('chr','ff','wk')}
        print(z, {b:beyond(f,r[b]) for b in r}, 'chr-ff',beyond(r['chr'],r['ff']), 'chr-wk',beyond(r['chr'],r['wk']), 'ff-wk', beyond(r['ff'],r['wk']))
