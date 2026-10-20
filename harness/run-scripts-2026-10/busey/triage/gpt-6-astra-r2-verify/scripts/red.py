import sys, numpy as np
from PIL import Image
L=lambda p: np.asarray(Image.open(p).convert('RGB'),dtype=np.int16)
def red(ours, refs, t=20):
    off=[np.abs(ours-r).max(2)>t for r in refs]
    a=off[0]&off[1]&off[2]
    sp=np.zeros(a.shape,bool)
    for i in range(3):
        for j in range(i+1,3): sp|=np.abs(refs[i]-refs[j]).max(2)>t
    return a, sp
if __name__=='__main__':
    o,c,f,w=sys.argv[1:5]
    a,sp=red(L(o),[L(c),L(f),L(w)])
    print(a.sum(), (a&~sp).sum(), sp.sum())
