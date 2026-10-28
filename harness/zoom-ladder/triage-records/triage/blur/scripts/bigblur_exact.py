# Exact (pixel-integrated Gaussian) rendering of probes/bigblur.svg at a zoom,
# and the SVG-spec three-box approximation; compared with femtovg and browsers.
import sys, math, json
import numpy as np
from PIL import Image
erf = np.vectorize(math.erf)
sys.path.insert(0, __file__.rsplit('/',1)[0])
from exact_rect import threebox_profile

Z = float(sys.argv[1]); frames = json.loads(sys.argv[2])
W, H = 460, 260; fit = 200/1024
def X(u): return 230 + (130 + fit*u - 230)*Z
def Y(v): return 130 + (30 + fit*v - 130)*Z
groups = [(100, 128, (0x28,0x80,0xc0)), (250, 96, (0x50,0x80,0xc0)), (400, 64, (0x78,0x80,0xc0)), (550, 128, (0xa0,0x80,0xc0))]
def prof(n, r0, r1, s, g0, g1, ss=8):
    t = (np.arange(n*ss)+0.5)/ss
    v = 0.5*(erf((t-r0)/(s*math.sqrt(2))) - erf((t-r1)/(s*math.sqrt(2))))
    v[(t < g0) | (t > g1)] = 0
    return v.reshape(n, ss).mean(axis=1)
def render(kind):
    img = np.full((H, W, 3), 255.0)
    for x, sd, col in groups:
        s = sd*fit*Z
        rx0, rx1, ry0, ry1 = X(x), X(x+300), Y(200), Y(500)
        gx0, gx1, gy0, gy1 = X(x-150), X(x+450), Y(50), Y(650)
        if kind == 'exact':
            ax = prof(W, rx0, rx1, s, gx0, gx1); ay = prof(H, ry0, ry1, s, gy0, gy1)
        else:
            P = 1200  # pad so the boxes see the rect beyond the frame
            ax, _ = threebox_profile(W+2*P, rx0+P, rx1+P, s, gx0+P, gx1+P); ax = ax[P:P+W]
            ay, _ = threebox_profile(H+2*P, ry0+P, ry1+P, s, gy0+P, gy1+P); ay = ay[P:P+H]
        a = np.outer(ay, ax)[..., None]
        img = img*(1-a) + np.array(col)[None, None, :]*a
    return img
imgs = {'exact': render('exact'), 'threebox': render('box')}
for n, p in frames.items(): imgs[n] = np.asarray(Image.open(p).convert('RGB')).astype(float)
names = list(imgs)
print(' '*12 + ''.join('%-14s' % n for n in names))
for a in names:
    print('%-12s' % a + ''.join('%-14s' % ('%d (%d)' % (((d := np.abs(imgs[a]-imgs[b]).max(axis=2)) > 8).sum(), round(d.max()))) for b in names))
if len(sys.argv) > 3:
    for n in names[2:]:
        d = imgs[n]-imgs['exact']
        m = np.abs(d).max(axis=2) > 8
        ys, xs = np.nonzero(m)
        print(n, 'beyond 8 vs exact at x', (xs.min(), xs.max()) if len(xs) else None, 'y', (ys.min(), ys.max()) if len(ys) else None,
              'mean signed (R,G,B) vs exact over x<60:', d[:, :60].reshape(-1, 3).mean(axis=0).round(2), 'elsewhere:', d[:, 60:].reshape(-1, 3).mean(axis=0).round(2))
    y = int(sys.argv[3])
    for n in names: print('%-9s' % n, [int(round(v)) for v in imgs[n][y, 0:60:4, 0]])
