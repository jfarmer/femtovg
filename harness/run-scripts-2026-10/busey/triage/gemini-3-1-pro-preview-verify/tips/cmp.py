import sys, numpy as np
from PIL import Image
S='/Users/matt/src/femtovg-wt/runs/busey/triage/gemini-3-1-pro-preview-verify/tips'
L=lambda p: np.asarray(Image.open(p).convert('RGB'),dtype=np.float64)
def dev(u,v): return 30+0.390625*u, -70+0.390625*v
def ink(im): return (255-im.mean(2))/255.0   # black on white: coverage
def run(name, build='mst2', tips=((280,725),(744,725)), r=14, png=None):
    o=L(png or f'{S}/png/{build}_t__{name}_z2.png')
    refs={b:L(f'{S}/refs/{b}_t__{name}_z2.png') for b in ('chr','ff','wk','id')}
    off=[np.abs(o-refs[b]).max(2)>20 for b in ('chr','ff','wk')]
    a=off[0]&off[1]&off[2]
    out=[f'{name:14s} {build:8s} agreed>20 {a.sum():4d} (vs area {(np.abs(o-refs["id"]).max(2)>20).sum():4d})']
    for (u,v) in tips:
        x,y=dev(u,v); x0,x1=int(x-r),int(x+r); y0,y1=int(y-r),int(y+r)
        box=(slice(max(y0,0),y1),slice(max(x0,0),x1))
        s=' '.join(f'{b}={ink(refs[b])[box].sum():5.1f}' for b in ('chr','ff','wk','id'))
        out.append(f'   tip({u},{v}) box px agreed {a[box].sum():3d}  ink fv={ink(o)[box].sum():5.1f} {s}')
    print('\n'.join(out))
if __name__=='__main__':
    b=sys.argv[1]
    for n in sys.argv[2:]:
        tips=((290,720),(734,720)) if n.startswith('inner') else ((280,725),(744,725))
        run(n,b,tips)
