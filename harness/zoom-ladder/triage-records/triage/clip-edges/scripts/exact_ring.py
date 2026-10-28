import sys, numpy as np, os
from PIL import Image
from exact_circle import coverage_circle
from cmp import fem, ref, load
k = 'corpus__clip-probes__evenodd-clip-thin-ring'
FR = {1: 'z1', 1.25: 'z125', 1.5: 'z15', 1.75: 'z175', 2: 'z2', 3: 'z3', 4: 'z4', 0.75: 'z075', 0.5: 'z05', 0.33: 'z033', 0.25: 'z025'}
fit = 200 / 120
print('zoom   fem   chr    ff    wk  area(id)   [px beyond 8/255 of the exact ring]   fem max err')
for z, fr in FR.items():
    X = 230 + z * (130 + fit * 60 - 230); Y = 130 + z * (30 + fit * 48 - 130)
    cov = coverage_circle(X, Y, 40 * fit * z, ss=48) - coverage_circle(X, Y, 39.5 * fit * z, ss=48)
    ex = np.stack([255 * (1 - cov), 255 * (1 - cov), 255 * (1 - cov) + 128 * cov], -1)
    Image.fromarray(np.rint(ex).astype(np.uint8)).save(f'../area/ex_ring_{fr}.png')
    row = []
    for n, img in [('fem', fem(k, z))] + [(b, ref(b, k, z)) for b in ('chr', 'ff', 'wk')] + [('id', load(f'../area/id_{k}_{fr}.png'))]:
        if img is None: row.append('    -'); continue
        d = np.abs(img[..., :3] - ex).max(-1); row.append(f'{int((d > 8).sum()):5d}')
        if n == 'fem': fm = d.max()
    print(f'{z:<5}' + ' '.join(row) + f'   {fm:.1f}')
