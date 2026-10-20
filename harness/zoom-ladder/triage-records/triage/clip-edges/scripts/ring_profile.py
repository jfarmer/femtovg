# ring_profile.py ZOOM: ink-weighted mean radius of the thin ring per angle wedge, minus the exact ring's
import sys, numpy as np
from PIL import Image
from cmp import fem, ref, load
k = 'corpus__clip-probes__evenodd-clip-thin-ring'
z = float(sys.argv[1]); z = int(z) if z == int(z) else z
FR = {1: 'z1', 1.25: 'z125', 1.5: 'z15', 1.75: 'z175', 2: 'z2', 3: 'z3', 4: 'z4'}
fr = FR[z]; X = 230; Y = 130 - 20 * z
ex = load(f'../area/ex_ring_{fr}.png')
imgs = [('exact', ex), ('fem', fem(k, z)), ('fem16', load(f'../exp/fem_ring16_{fr}.png') if z in (2, 3) else None), ('chr', ref('chr', k, z)), ('ff', ref('ff', k, z)), ('wk', ref('wk', k, z)), ('wk16', load(f'../exp/wk_ring16_{fr}.png') if z in (2, 3) else None), ('id', load(f'../area/id_{k}_{fr}.png'))]
yy, xx = np.mgrid[0:260, 0:460]; r = np.hypot(xx + .5 - X, yy + .5 - Y); ang = np.degrees(np.arctan2(yy + .5 - Y, xx + .5 - X))
# fold to the angle within a 90-degree segment, measured from the nearest axis start (segments start at 0, 90, 180, 270)
seg = np.mod(ang, 90)
bins = np.arange(0, 91, 7.5)
R0 = (40 + 39.5) / 2 * 200 / 120 * z
band = np.abs(r - R0) < 3
print(f'zoom {z}: mean radial offset of the ring (px) vs the exact ring, by angle within each 90-degree arc segment')
print('seg-angle  ' + ' '.join(f'{(bins[i]+bins[i+1])/2:6.1f}' for i in range(len(bins) - 1)))
def prof(img):
    cov = np.clip(1 - img[..., 0] / 255, 0, 1)
    out = []
    for i in range(len(bins) - 1):
        m = band & (seg >= bins[i]) & (seg < bins[i + 1])
        out.append((cov[m] * r[m]).sum() / max(cov[m].sum(), 1e-9))
    return np.array(out)
pe = prof(ex)
for n, img in imgs:
    if img is None: continue
    print(f'{n:9}  ' + ' '.join(f'{v:+6.3f}' for v in prof(img) - pe))
