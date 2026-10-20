import sys; sys.path.insert(0,'.'); sys.path.insert(0,'..')
import numpy as np
from model import build, expand
from lib import ours, refs, red, offid, L
def raster2(E, W, H, interior_only=False, half_band=False, add='product'):
    ys, xs = np.mgrid[0:H, 0:W]; px = xs + 0.5; py = ys + 0.5
    def bary(a, b, c):
        den = (b[1]-c[1])*(a[0]-c[0]) + (c[0]-b[0])*(a[1]-c[1])
        if abs(den) < 1e-12: return None, None
        l1 = ((b[1]-c[1])*(px-c[0]) + (c[0]-b[0])*(py-c[1]))/den
        l2 = ((c[1]-a[1])*(px-c[0]) + (a[0]-c[0])*(py-c[1]))/den
        l3 = 1-l1-l2
        return (l1 >= 0)&(l2 >= 0)&(l3 >= 0), (l1, l2, l3, den)
    wind = np.zeros((H, W), int); f = E['fill']; hub = f[0]
    for k in range(1, len(f)-1):
        ins, info = bary(hub, f[k], f[k+1])
        if ins is None: continue
        wind[ins] += 1 if info[3] > 0 else -1
    vals, cnts = np.unique(wind[wind != 0], return_counts=True)
    main = vals[np.argmax(cnts)]
    stencil0 = (wind == 0) | ((wind != main) if interior_only else False)
    trans = np.ones((H, W)); mx = np.zeros((H, W))
    st = E['strip']
    for k in range(len(st)-2):
        a, b, c = st[k], st[k+1], st[k+2]
        ins, info = bary(a[0], b[0], c[0])
        if ins is None: continue
        l1, l2, l3, _ = info
        u = l1*a[1] + l2*b[1] + l3*c[1]
        cov = np.clip(1-np.abs(2*u-1), 0, 1)
        if half_band: cov = np.where(u < 0.5, 0.0, cov)  # inner half (u<0.5: deeper than 0.5 px inside) removed
        m = ins & stencil0
        trans[m] *= (1-cov[m]); mx[m] = np.maximum(mx[m], cov[m])
    fr = (1-trans) if add == 'product' else mx
    cover = (~stencil0).astype(float)
    return dict(total=1-(1-cover)*(1-fr), wind=wind, main=main)
LIP = ((370,650),[((400,720),(460,755),(512,756)),((564,755),(624,720),(654,650)),((635,705),(575,742),(512,743)),((449,742),(389,705),(370,650))])
if __name__ == '__main__':
    P, C = build(LIP); E = expand(P, C)
    bg = np.array([0xdf,0x9a,0x78], float); fg = np.array([0xab,0x4f,0x47], float); d = fg-bg
    R = refs('r10_lip_skin', 'z2'); cid = ((R['id'].astype(float)-bg)@d)/(d@d)
    wins = [np.s_[170:215, 165:200], np.s_[170:215, 260:295]]
    o = ours('r10_lip_skin','z2')
    for name, kw in [('master', {}), ('inverted loop not covered', dict(interior_only=True)),
                     ('inner half removed', dict(half_band=True)), ('both', dict(interior_only=True, half_band=True)),
                     ('both, fringes by max', dict(interior_only=True, half_band=True, add='max'))]:
        M = raster2(E, 460, 260, **kw); t = M['total']
        img = (bg + (fg-bg)*t[..., None]).astype(np.int16)
        img2 = o.copy(); 
        for w in wins: img2[w] = img[w]
        a, _, _ = red(img2, R); oi = offid(img2, R)
        ink = sum(t[w].sum() for w in wins); inkid = sum(cid[w].sum() for w in wins)
        extra = ink - inkid
        print(f'{name:28s} red {int(a.sum()):4d} offid {int(oi.sum()):4d} tip ink {ink/inkid:.2f} excess {extra:6.1f} px  main wind {M["main"]}')
    M = raster2(E, 460, 260)
    a, _, _ = red(o, R); ys, xs = np.nonzero(a)
    print('red px by wind:', dict(zip(*[x.tolist() for x in np.unique(M['wind'][ys, xs], return_counts=True)])), 'main', M['main'])
    print('pixels with opposite wind:', int(((M['wind'] != 0) & (M['wind'] != M['main'])).sum()))
