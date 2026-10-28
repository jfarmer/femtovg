# Exact and three-box (SVG spec / Skia GaussPass) blur of an axis-aligned
# rect cropped to a filter region, composited over white; compares with
# the femtovg frame and the browser frames.
import sys, math
import numpy as np
from PIL import Image
from math import erf, sqrt

def Phi(t): return 0.5*(1+erf(t/sqrt(2)))

def exact_profile(n, r0, r1, sigma, reg0, reg1, ss=16):
    # pixel-averaged 1-D profile of a box [r0,r1] blurred by sigma, cropped to [reg0,reg1]
    out = np.zeros(n)
    for i in range(n):
        acc = 0.0
        for k in range(ss):
            x = i + (k+0.5)/ss
            if reg0 <= x <= reg1:
                acc += Phi((x-r0)/sigma) - Phi((x-r1)/sigma)
        out[i] = acc/ss
    return out

def sampled_gauss_profile(n, r0, r1, sigma, reg0, reg1):
    # femtovg's kernel: Gaussian point-sampled at integer taps, radius ceil(3s)-1, normalised
    cov = np.array([max(0.0, min(i+1, r1, reg1) - max(i, r0, reg0)) for i in range(n)])
    R = math.ceil(3*sigma) - 1
    taps = np.array([math.exp(-0.5*(j/sigma)**2) for j in range(-R, R+1)]); taps /= taps.sum()
    out = np.convolve(cov, taps, mode='same')
    for i in range(n):
        if not (reg0 <= i+0.5 <= reg1): out[i] = 0
    return out

def box(v, lo, hi):
    # mean over offsets lo..hi inclusive
    n = len(v); w = hi-lo+1
    c = np.concatenate([[0.0], np.cumsum(v)])
    i = np.arange(n)
    a = np.clip(i+lo, 0, n); b = np.clip(i+hi+1, 0, n)
    return (c[b]-c[a])/w

def threebox_profile(n, r0, r1, sigma, reg0, reg1):
    cov = np.array([max(0.0, min(i+1, r1, reg1) - max(i, r0, reg0)) for i in range(n)])
    d = int(math.floor(sigma*3*sqrt(2*math.pi)/4 + 0.5))
    if d % 2 == 1:
        h = d//2; v = box(box(box(cov, -h, h), -h, h), -h, h)
    else:
        h = d//2
        v = box(cov, -h, h-1); v = box(v, -h+1, h); v = box(v, -h, h)
    for i in range(n):
        if not (reg0 <= i+0.5 <= reg1): v[i] = 0
    return v, d

def compose(ax, ay, color):
    a = np.outer(ay, ax)
    rgb = np.zeros(a.shape+(3,))
    for c in range(3): rgb[...,c] = color[c]*a + 255*(1-a)
    return rgb

if __name__ == '__main__':
    import json
    args = json.loads(sys.argv[1])
    W, H = 460, 260
    r = args['rect']; reg = args.get('region', r); sx, sy = args['sigma']; col = args['color']
    ex = compose(exact_profile(W, r[0], r[2], sx, reg[0], reg[2]), exact_profile(H, r[1], r[3], sy, reg[1], reg[3]), col)
    tbx, dx = threebox_profile(W, r[0], r[2], sx, reg[0], reg[2]); tby, dy = threebox_profile(H, r[1], r[3], sy, reg[1], reg[3])
    tb = compose(tbx, tby, col)
    sg = compose(sampled_gauss_profile(W, r[0], r[2], sx, reg[0], reg[2]), sampled_gauss_profile(H, r[1], r[3], sy, reg[1], reg[3]), col)
    imgs = {'exact': ex, 'threebox(d=%d,%d)' % (dx, dy): tb, 'sampled_gauss': sg}
    for name, p in args['frames'].items():
        imgs[name] = np.asarray(Image.open(p).convert('RGB')).astype(float)
    names = list(imgs)
    print('pixels beyond 8/255 (max diff):')
    print(' '*22 + ''.join('%-20s' % n[:19] for n in names))
    for a in names:
        row = '%-22s' % a[:21]
        for b in names:
            d = np.abs(imgs[a]-imgs[b]).max(axis=2)
            row += '%-20s' % ('%d (%d)' % ((d > 8).sum(), round(d.max())))
        print(row)
    if 'row' in args:
        y = args['row']; x0, x1 = args['cols']
        for n in names:
            print('%-22s' % n[:21], [int(round(v)) for v in imgs[n][y, x0:x1, 0]])
