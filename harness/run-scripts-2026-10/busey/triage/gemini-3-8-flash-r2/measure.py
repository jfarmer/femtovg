import sys, glob, os, json, numpy as np
from PIL import Image
L=lambda p: np.asarray(Image.open(p).convert('RGB'),dtype=np.int16)
S=os.path.dirname(os.path.abspath(__file__))
REG={'z2':{'lip_corners':[(163,172,200,214),(264,172,302,214)],
           'irises':[(178,88,214,126),(246,86,284,124)]},
     'hd':{'lip_corners':[(790,672,860,745),(1060,672,1130,745)],
           'irises':[(840,440,900,500),(1025,435,1085,495)],
           'nose_crescent':[(925,600,1000,630)]}}
def stats(k, build='mst4', fr='z2', pd=f'{S}/png', rd=f'{S}/refs', refk=None, verbose=False):
    o=L(f'{pd}/{build}_{k}_{fr}.png'); refs=[L(f'{rd}/{x}_{refk or k}_{fr}.png') for x in ('chr','ff','wk')]
    off=[np.abs(o-r).max(2)>20 for r in refs]; all3=off[0]&off[1]&off[2]
    sp=np.zeros(all3.shape,bool)
    for i in range(3):
        for j in range(i+1,3): sp|=np.abs(refs[i]-refs[j]).max(2)>20
    ag=all3&~sp
    r={'all3':int(all3.sum()),'agreed':int(ag.sum()),'spread':int(sp.sum())}
    covered=np.zeros(all3.shape,bool)
    for n,boxes in REG[fr].items():
        m=np.zeros(all3.shape,bool)
        for (x0,y0,x1,y1) in boxes: m[y0:y1,x0:x1]=True
        covered|=m
        r[n]=f"{int((all3&m).sum())}/{int((ag&m).sum())}"
    r['rest']=f"{int((all3&~covered).sum())}/{int((ag&~covered).sum())}"
    if verbose:
        ys,xs=np.nonzero(all3&~covered); print(' rest px:',list(zip(xs.tolist(),ys.tolist()))[:80])
    return r
if __name__=='__main__':
    fr=sys.argv[1]; build=sys.argv[2] if len(sys.argv)>2 else 'mst4'; v='-v' in sys.argv
    keys=[a for a in sys.argv[3:] if a!='-v'] or sorted(os.path.basename(p)[len(build)+1:-len(fr)-5] for p in glob.glob(f'{S}/png/{build}_t__*_{fr}.png'))
    for k in keys: print(f'{k:34s}', stats(k,build,fr,verbose=v))
