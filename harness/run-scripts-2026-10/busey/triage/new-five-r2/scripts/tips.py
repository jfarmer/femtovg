"""tips.py key fr [build=mst4] u,v ... : per point (svg coords): ink in a window around it (luminance-weighted coverage vs bg), femtovg vs chr/ff/wk/area, and px>20 off area / off all three"""
import sys, numpy as np
from PIL import Image
S='/Users/matt/src/femtovg-wt/runs/busey/triage/new-five-r2'
sys.path.insert(0,f'{S}/scripts'); from locate import S as FS
a=dict(x.split('=',1) for x in sys.argv[1:] if '=' in x); p=[x for x in sys.argv[1:] if '=' not in x]
k,fr=p[0],p[1]; b=a.get('build','mst4'); rad=float(a.get('rad',3)); pd=a.get('pd',f'{S}/png')
L=lambda q: np.asarray(Image.open(q).convert('RGB'),dtype=np.float64)
o=L(f'{pd}/{b}_{k}_{fr}.png'); R={x:L(f'{S}/refs/{x}_{k}_{fr}.png') for x in ('chr','ff','wk','id')}
bg=np.array([float(c) for c in a['bg'].split(',')]) if 'bg' in a else None; fg=np.array([float(c) for c in a['fg'].split(',')]) if 'fg' in a else None
def cov(im):
    # coverage estimate by projecting onto fg-bg
    d=fg-bg; return ((im-bg)@d)/(d@d)
ox,oy,s=FS[fr]
for pt in p[2:]:
    u,v=map(float,pt.split(',')); x,y=ox+u*s,oy+v*s
    x0,x1,y0,y1=int(x-rad),int(np.ceil(x+rad)),int(y-rad),int(np.ceil(y+rad))
    win=lambda im: im[y0:y1,x0:x1]
    off=[np.abs(win(o)-win(R[q])).max(2)>20 for q in ('chr','ff','wk')]
    all3=(off[0]&off[1]&off[2]).sum(); oid=(np.abs(win(o)-win(R['id'])).max(2)>20).sum()
    line=f'({u:g},{v:g}) all3 {all3} offarea {oid}'
    if bg is not None:
        ink={n:cov(win(im)).sum() for n,im in [('fv',o)]+list(R.items())}
        line+=' ink '+' '.join(f'{n} {ink[n]:.2f}' for n in ink)+f"  fv/area {ink['fv']/ink['id']:.2f} chr/area {ink['chr']/ink['id']:.2f}"
    print(line)
