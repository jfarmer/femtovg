"""px.py FR ours [x0 y0 x1 y1]: per red pixel: frame xy, svg xy, ours, chr, ff, wk, id"""
import sys, numpy as np
from PIL import Image
fr=sys.argv[1]; ours=sys.argv[2]
R='/Users/matt/src/femtovg-wt/runs/busey/refs'; K=sys.argv[7] if len(sys.argv)>7 else 'corpus__buseybench__gpt-6-astra'
RD=sys.argv[8] if len(sys.argv)>8 else R
L=lambda p: np.asarray(Image.open(p).convert('RGB'),dtype=np.int16)
o=L(ours); refs=[L(f'{RD}/{x}_{K}_{fr}.png') for x in ('chr','ff','wk','id')]
off=[np.abs(o-r).max(2)>20 for r in refs[:3]]; all3=off[0]&off[1]&off[2]
box=list(map(int,sys.argv[3:7])) if len(sys.argv)>6 else [0,0,o.shape[1],o.shape[0]]
def svg(x,y):
    if fr=='hd': return ((x+.5-420)/1.0546875,(y+.5)/1.0546875)
    z=float(fr[1:]); s=200/1024; # frame = 230 + z*(130 + s*X - 230)
    return (((x+.5-230)/z+100)/s, ((y+.5-130)/z+100)/s)
ys,xs=np.nonzero(all3[box[1]:box[3],box[0]:box[2]])
for y,x in sorted(zip(ys+box[1],xs+box[0]),key=lambda p:(p[1],p[0])):
    sx,sy=svg(x,y)
    print(f'{x:4d},{y:4d} svg({sx:6.1f},{sy:6.1f}) o{tuple(o[y,x])} c{tuple(refs[0][y,x])} f{tuple(refs[1][y,x])} w{tuple(refs[2][y,x])} id{tuple(refs[3][y,x])}')
