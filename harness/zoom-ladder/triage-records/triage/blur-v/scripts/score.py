import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from model import *
from PIL import Image
H='/Users/matt/src/femtovg-wt/runs/zoom'
tag=sys.argv[1]
files=[('wpt-fegaussianblur-reftests','blur-variation-4-4-15'),('wpt-fegaussianblur-reftests','blur-variation-6-4-11'),('wpt-layer-blur-reftests','2d.layer.anisotropic-blur.isotropic'),('wpt-fegaussianblur-reftests','blur-variation-6-2-17'),('wpt-fegaussianblur-reftests','blur-variation-3-3-14'),('wpt-fegaussianblur-reftests','blur-variation-5-3-22')]
zs={'0.5':('z05','14'),'0.75':('z075','13'),'0.33':('z033','15'),'0.25':('z025','16')}
def L(p): return np.asarray(Image.open(p).convert('RGB')).astype(float)
for d,n in files:
    key=f'corpus__{d}__{n}'; row=[]
    for z,(fr,st) in zs.items():
        im=L(f'out/{tag}.{n}.{z}.ppm'); lad=L(f'{H}/png/zl_zm_svg/{key}/{st}.png')
        r=['lad%d'%cmp(im,lad)[0]]
        for b in ('chr','ff'):
            p=f'{H}/fresh/refs/{b}_{key}_{fr}.png'
            if os.path.exists(p): r.append('%s%d(%d)'%((b,)+cmp(im,L(p))))
        row.append(z+':'+','.join(r))
    print('%-38s'%n,' '.join(row))
im=L(f'out/{tag}.bigblur.3.ppm'); key='corpus__probes__bigblur'
print('bigblur z3', 'lad', cmp(im,L(f'{H}/png/zl_zm_svg/{key}/05.png')), 'chr', cmp(im,L(f'{H}/fresh/refs/chr_{key}_z3.png')), 'ff', cmp(im,L(f'{H}/fresh/refs/ff_{key}_z3.png')))
