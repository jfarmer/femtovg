import sys; sys.path.insert(0,'.'); sys.path.insert(0,'..')
import numpy as np, model
from lipdecomp import raster2, LIP
from lib import ours, refs, red, offid
fr = sys.argv[1]; name = sys.argv[2] if len(sys.argv) > 2 else 'r10_lip_skin'
if fr == 'hd':
    s = 1080/1024; model.T = lambda x, y: (420 + s*x, s*y); W, H = 1920, 1080
    wins = [np.s_[670:760, 800:860], np.s_[670:760, 1060:1120]]
else:
    W, H = 460, 260; wins = [np.s_[170:215, 165:200], np.s_[170:215, 260:295]]
P, C = model.build(LIP); E = model.expand(P, C)
bg = np.array([0xdf,0x9a,0x78], float); fg = np.array([0xab,0x4f,0x47], float); d = fg-bg
R = refs(name, fr); cid = ((R['id'].astype(float)-bg)@d)/(d@d); o = ours(name, fr)
for nm, kw in [('master', {}), ('inverted loop not covered', dict(interior_only=True)), ('inner half removed', dict(half_band=True)), ('both', dict(interior_only=True, half_band=True))]:
    M = raster2(E, W, H, **kw); t = M['total']
    img = (bg + (fg-bg)*t[..., None])
    dd = max(np.abs(img[w] - o[w]).max() for w in wins)
    img2 = o.copy()
    for w in wins: img2[w] = np.rint(img[w]).astype(np.int16)
    a, _, _ = red(img2, R); oi = offid(img2, R)
    ink = sum(t[w].sum() for w in wins); inkid = sum(cid[w].sum() for w in wins)
    print(f'{fr} {nm:26s} max|model-femtovg| {dd:6.2f}  red {int(a.sum()):4d} offid {int(oi.sum()):4d} tip ink {ink/inkid:.2f}')
M = raster2(E, W, H); a, _, _ = red(o, R); ys, xs = np.nonzero(a)
print('red by wind', dict(zip(*[x.tolist() for x in np.unique(M['wind'][ys, xs], return_counts=True)])), 'main', M['main'], 'opposite-wind px', int(((M['wind'] != 0) & (M['wind'] != M['main'])).sum()))
