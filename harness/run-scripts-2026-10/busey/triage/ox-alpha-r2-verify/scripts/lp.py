import sys, numpy as np
from PIL import Image
L=lambda p: np.asarray(Image.open(p).convert('RGB'),dtype=np.int16)
R='/Users/matt/src/femtovg-wt/runs/busey/refs/'; V='refs/'
def run(name, png, fm, pre, fr):
    m=np.load(png[:-4]+'_all3.npy'); o=L(png); f=L(fm)
    refs={b:L(pre.format(b=b)+f'_{fr}.png') for b in ('chr','ff','wk','id')}
    S=1.0546875 if fr=='hd' else 0.390625
    ox,oy=(420,0) if fr=='hd' else (230-512*0.390625, 130-512*0.390625)
    print('==',name,fr,m.sum())
    for y,x in zip(*np.nonzero(m)):
        sv=((x+0.5-ox)/S,(y+0.5-oy)/S)
        fmr=all(np.abs(f[y,x]-refs[b][y,x]).max()>20 for b in ('chr','ff','wk'))
        print(f'({x},{y}) svg({sv[0]:.1f},{sv[1]:.1f}) fv {tuple(o[y,x])} fm {tuple(f[y,x])}{"*" if fmr else ""} chr {tuple(refs["chr"][y,x])} ff {tuple(refs["ff"][y,x])} wk {tuple(refs["wk"][y,x])} id {tuple(refs["id"][y,x])}')
run('ox orig','png/ox_orig_z2.png','png/ox_orig_fm_z2.png',R+'{b}_corpus__buseybench__ox-alpha','z2')
run('ox nodisp','png/ox_nodisp_hd.png','png/ox_nodisp_fm_hd.png',V+'{b}_v__ox_nodisp','hd')
run('mu orig','png/mu_orig_z2.png','png/mu_orig_fm_z2.png',R+'{b}_corpus__buseybench__muse-spark-1-3-contributor','z2')
run('mu split','png/mu_split_hd.png','png/mu_split_fm_hd.png',V+'{b}_v__mu_split','hd')
