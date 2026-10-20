import sys, numpy as np
from PIL import Image
S='/Users/matt/src/femtovg-wt/runs/busey/triage/gemini-3-7-flash-verify'
L=lambda p: np.asarray(Image.open(p).convert('RGB'),dtype=np.float64)
BG=np.array([0x15,0x03,0x04],float); FG=np.array([0xf0,0xc0,0x90],float)
def cov(img):  # coverage from luminance-ish projection on fg-bg
    d=FG-BG; return np.clip(((img-BG)@d)/(d@d),0,1.5)
def tx(x,y): return 30+0.390625*x, -70+0.390625*y
def run(k, wins):
    o=L(f'{S}/png/mst2_{k}_z2.png'); R={n:L(f'{S}/refs/{n}_{k}_z2.png') for n in ('chr','ff','wk','id')}
    off=[np.abs(o-R[n]).max(2)>20 for n in ('chr','ff','wk')]; all3=off[0]&off[1]&off[2]
    offid=np.abs(o-R['id']).max(2)>20
    out=f'{k:20s} all3={int(all3.sum()):4d} vs_id={int(offid.sum()):4d}'
    for name,(x0,y0,x1,y1) in wins.items():
        sl=np.s_[y0:y1,x0:x1]
        c={n:cov(R[n])[sl].sum() for n in R}; co=cov(o)[sl].sum()
        out+=f' | {name}: all3 {int(all3[sl].sum())} ink fem/id {co/c["id"]:.2f} chr {c["chr"]/c["id"]:.2f} ff {c["ff"]/c["id"]:.2f} wk {c["wk"]/c["id"]:.2f}'
    print(out)
if __name__=='__main__':
    lx,ly=tx(345,645); rx,ry=tx(679,645)
    print('left tip dev',lx,ly,'right tip',rx,ry)
    for k in sys.argv[1:]:
        run(k,{'L':(int(lx)-4,int(ly)-4,int(lx)+12,int(ly)+20),'R':(int(rx)-12,int(ry)-4,int(rx)+4,int(ry)+20)})
