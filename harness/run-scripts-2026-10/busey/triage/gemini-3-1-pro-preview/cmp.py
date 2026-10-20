import sys, numpy as np
from PIL import Image
L=lambda p: np.asarray(Image.open(p).convert('RGB'),dtype=np.int16)
S='/Users/matt/src/femtovg-wt/runs/busey/triage/gemini-3-1-pro-preview'
def get(name, build='mst2'):
    ours=L(f'{S}/png/{build}_t__{name}_z2.png'); refs=[L(f'{S}/refs/{b}_t__{name}_z2.png') for b in ('chr','ff','wk')]
    off=[np.abs(ours-r).max(axis=2)>20 for r in refs]; a=off[0]&off[1]&off[2]
    sp=np.zeros(a.shape,bool)
    for i in range(3):
        for j in range(i+1,3): sp|=np.abs(refs[i]-refs[j]).max(axis=2)>20
    return ours,refs,a,sp
def region(m,box):
    x0,y0,x1,y1=box; return int(m[y0:y1,x0:x1].sum())
if __name__=='__main__':
    boxes={}
    for arg in sys.argv[1:]:
        if '=' in arg: k,v=arg.split('='); boxes[k]=[int(t) for t in v.split(',')]
    for name in [a for a in sys.argv[1:] if '=' not in a]:
        o,r,a,sp=get(name); ag=a&~sp
        print(f'{name:28s} all3 {a.sum():5d} agreed {ag.sum():5d} spread {sp.sum():6d}', ' '.join(f'{k}:{region(ag,b)}' for k,b in boxes.items()))
