import sys, numpy as np
from PIL import Image
def ld(p):
    im=Image.open(p).convert('RGB')
    return np.asarray(im).astype(float)
def area(p):
    a=ld(p)[:2080,:3680]; return a.reshape(260,8,460,8,3).mean((1,3))
def cnt(a,b):
    d=np.abs(a-b).max(-1); return int((d>8).sum()), int(round(d.max()))
row=int(sys.argv[2]) if len(sys.argv)>2 else 100
xs=slice(*[int(v) for v in sys.argv[3].split(':')]) if len(sys.argv)>3 else slice(186,194)
for pre in sys.argv[1].split(','):
    A=area(pre+'_area8.png')
    ims={k:ld(f'{pre}_{k}') for k in ['fem.ppm','chr.png','ff.png','wk.png'] if __import__('os').path.exists(f'{pre}_{k}')}
    print(pre.split('/')[-1], ' '.join(f'{k.split(".")[0]}~area {cnt(v,A)}' for k,v in ims.items()), '| chr~fem', cnt(ims['chr.png'],ims['fem.ppm']))
    print('   G row',row, {k.split('.')[0]: v[row,xs,1].astype(int).tolist() for k,v in list(ims.items())}, 'area', np.round(A[row,xs,1]).astype(int).tolist())
