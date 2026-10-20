"""caps_ink.py: m2_round / m2_butt: ink (sum of coverage, px^2) of each 10-unit stroke vs the analytic area, per renderer."""
import math, numpy as np
from PIL import Image
L=lambda p: np.asarray(Image.open(p).convert('L'),dtype=np.float64)/255
widths=[0.6,0.9,1.2,1.5,2.0,2.5,3.0,4.5,6.0]
def ncap(hw, tol=0.125):
    return max(2, math.ceil(math.pi/(2*math.acos(hw/(hw+tol)))))
for fr,z in (('z1',1.0),('z2',2.0)):
    s=z  # px per unit at these framings: 200-unit file in the 200 px box
    # frame = 230 + z*(130 + X - 230)
    fx=lambda X: 230+z*(X-100); fy=lambda Y: 130+z*(Y-100)
    for cap in ('round','butt'):
        ims={r:L(p) for r,p in [('femtovg',f'png/mst4_t__m2_{cap}_{fr}.png')]+[(b,f'refs/{b}_t__m2_{cap}_{fr}.png') for b in ('chr','ff','wk','id')]}
        print(f'== {fr} {cap} caps: ink per stroke (px^2), mean of the four angles; analytic = w*L' + (' + pi*w^2/4' if cap=='round' else ''))
        print(f'  {"w(px)":>6} {"ncap":>4} {"exact":>7} ' + ' '.join(f'{r:>8}' for r in ims) + '   femtovg/id')
        for r,w in enumerate(widths):
            wd=w*s; y=12+r*20.3; inks={k:[] for k in ims}
            for k,a in enumerate((0,30,60,90)):
                x=20+k*45.37; dx,dy=10*math.cos(math.radians(a)),-10*math.sin(math.radians(a))
                x0,x1=sorted((fx(x),fx(x+dx))); y0,y1=sorted((fy(y+5),fy(y+5+dy)))
                m=int(wd)+4
                X0,X1,Y0,Y1=int(x0)-m,int(x1)+m+1,int(y0)-m,int(y1)+m+1
                if X0<0 or Y0<0 or X1>460 or Y1>260: continue
                for kk,im in ims.items(): inks[kk].append(im[Y0:Y1,X0:X1].sum())
            if not inks['id']: continue
            exact=wd*10*s+(math.pi*wd*wd/4 if cap=='round' else 0)
            mean={k:np.mean(v) for k,v in inks.items()}
            print(f'  {wd:6.2f} {ncap(max(wd,1)/2):4d} {exact:7.2f} ' + ' '.join(f'{mean[k]:8.2f}' for k in ims) + f'   {mean["femtovg"]/mean["id"]:.3f}')
