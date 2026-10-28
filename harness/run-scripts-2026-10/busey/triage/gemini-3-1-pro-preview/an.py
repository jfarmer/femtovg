import sys, numpy as np
from PIL import Image
L = lambda p: np.asarray(Image.open(p).convert('RGB'), dtype=np.int16)
R='/Users/matt/src/femtovg-wt/runs/busey'
def masks(ours_p, k, fr='z2', refdir=R+'/refs'):
    ours=L(ours_p); refs=[L(f'{refdir}/{x}_{k}_{fr}.png') for x in ('chr','ff','wk')]
    h=min([ours.shape[0]]+[r.shape[0] for r in refs]); w=min([ours.shape[1]]+[r.shape[1] for r in refs])
    ours=ours[:h,:w]; refs=[r[:h,:w] for r in refs]
    off=[np.abs(ours-r).max(axis=2)>20 for r in refs]
    all3=off[0]&off[1]&off[2]
    spread=np.zeros((h,w),bool)
    for i in range(3):
        for j in range(i+1,3):
            spread|=np.abs(refs[i]-refs[j]).max(axis=2)>20
    return ours, refs, all3, spread
if __name__=='__main__':
    k='corpus__buseybench__gemini-3-1-pro-preview'
    ours,refs,a,s=masks(R+f'/png/mst2_{k}_z2.png',k)
    ag=a&~s
    print('all3',a.sum(),'agreed',ag.sum(),'spread',s.sum())
    # grid histogram 20px cells
    H,W=ag.shape
    cells=[]
    for y in range(0,H,20):
        for x in range(0,W,20):
            n=ag[y:y+20,x:x+20].sum(); m=a[y:y+20,x:x+20].sum()
            if m: cells.append((n,m,x,y))
    cells.sort(reverse=True)
    for c in cells[:40]: print(c)
