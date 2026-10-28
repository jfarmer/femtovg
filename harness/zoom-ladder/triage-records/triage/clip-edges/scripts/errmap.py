# errmap.py KEY ZOOM: where each renderer differs from the area ref (signed, R channel and max channel)
import sys, numpy as np, os
from cmp import fem, ref, load
k = sys.argv[1]; z = float(sys.argv[2]); z = int(z) if z == int(z) else z
FR = {1: 'z1', 1.25: 'z125', 1.5: 'z15', 1.75: 'z175', 2: 'z2', 3: 'z3', 4: 'z4', 0.75: 'z075', 0.5: 'z05', 0.33: 'z033', 0.25: 'z025'}
a = load(os.path.expanduser(f'~/src/femtovg-wt/runs/zoom/triage/clip-edges/area/id_{k}_{FR[z]}.png'))
for n, img in [('fem', fem(k, z))] + [(b, ref(b, k, z)) for b in ('chr', 'ff', 'wk')]:
    if img is None: continue
    d = img[..., :3] - a[..., :3]; m = np.abs(d).max(-1) > 8
    if not m.any(): print(n, 0); continue
    ys, xs = np.nonzero(m)
    lum = d.mean(-1)
    print(f'{n}: n={m.sum()} max={np.abs(d).max()} mean signed(lum)={lum[m].mean():.1f} (neg=more ink) frac_neg={(lum[m]<0).mean():.2f} bbox x{xs.min()}-{xs.max()} y{ys.min()}-{ys.max()}')
    hist = np.histogram(np.abs(d).max(-1)[m], bins=[9, 12, 16, 24, 32, 64, 128, 256])[0]
    print('    |err| hist 9-12,12-16,16-24,24-32,32-64,64-128,128+:', hist)
