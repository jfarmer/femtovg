import sys, glob, os, json, numpy as np
from PIL import Image
L=lambda p: np.asarray(Image.open(p).convert('RGB'),dtype=np.int16)
S=os.path.dirname(os.path.abspath(__file__))
REG={'lip_corners':[(155,165,190,205),(280,165,315,205)],
     'hair_tips':[(130,40,180,100),(290,40,340,100),(300,0,345,30)],
     'irises':[(170,90,215,135),(250,90,295,135)]}
def stats(k, pd=f'{S}/png', rd=f'{S}/refs', build='mst2', fr='z2'):
    o=L(f'{pd}/{build}_{k}_{fr}.png'); refs=[L(f'{rd}/{x}_{k}_{fr}.png') for x in ('chr','ff','wk')]
    off=[np.abs(o-r).max(2)>20 for r in refs]; all3=off[0]&off[1]&off[2]
    sp=np.zeros(all3.shape,bool)
    for i in range(3):
        for j in range(i+1,3): sp|=np.abs(refs[i]-refs[j]).max(2)>20
    ag=all3&~sp
    r={'all3':int(all3.sum()),'agreed':int(ag.sum()),'spread':int(sp.sum()),'vs_chr':int(off[0].sum())}
    covered=np.zeros(all3.shape,bool)
    for n,boxes in REG.items():
        m=np.zeros(all3.shape,bool)
        for (x0,y0,x1,y1) in boxes: m[y0:y1,x0:x1]=True
        covered|=m
        r[n]=f"{int((all3&m).sum())}/{int((ag&m).sum())}"
    r['rest']=f"{int((all3&~covered).sum())}/{int((ag&~covered).sum())}"
    return r
if __name__=='__main__':
    keys=sys.argv[1:] or sorted(os.path.basename(p)[5:-7] for p in glob.glob(f'{S}/png/mst2_*_z2.png'))
    for k in keys: print(f'{k:34s}', stats(k))
    print('corpus', stats('corpus__buseybench__gemini-3-7-flash', pd='/Users/matt/src/femtovg-wt/runs/busey/png', rd='/Users/matt/src/femtovg-wt/runs/busey/refs'))
