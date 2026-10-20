# Split each bad step's >8/255 pixels into frame-ring pixels and the rest, per browser.
import json, os, sys, numpy as np
from PIL import Image
H = os.path.expanduser('~')
R = f'{H}/src/femtovg-wt/runs/zoom'
LADDER = [1, 1.25, 1.5, 1.75, 2, 3, 4, 3, 2, 1.75, 1.5, 1.25, 1, 0.75, 0.5, 0.33, 0.25, 0.33, 0.5, 0.75, 1]
FR = {1: 'z1', 1.25: 'z125', 1.5: 'z15', 1.75: 'z175', 2: 'z2', 3: 'z3', 4: 'z4', 0.75: 'z075', 0.5: 'z05', 0.33: 'z033', 0.25: 'z025'}
def load(p): return np.asarray(Image.open(p).convert('RGB'), dtype=np.int16)
def ring(z, h=260, w=460, margin=1.0):
    # frame stroke covers user [0.5,1.5] and [198.5,199.5] on both axes; fit = 1
    def dev(u, c): return c + (u - 100 + (c - (130 if c == 230 else 30) - 100) * 0) * z
    x0 = 230 + (130 + 0.5 - 230) * z; x1 = 230 + (130 + 1.5 - 230) * z
    X0 = 230 + (130 + 198.5 - 230) * z; X1 = 230 + (130 + 199.5 - 230) * z
    y0 = 130 + (30 + 0.5 - 130) * z; y1 = 130 + (30 + 1.5 - 130) * z
    Y0 = 130 + (30 + 198.5 - 130) * z; Y1 = 130 + (30 + 199.5 - 130) * z
    xs = np.arange(w) + 0.5; ys = np.arange(h) + 0.5
    def band(c, a, b): return (c + 0.5 > a - margin) & (c - 0.5 < b + margin)
    inx = band(xs, x0, X1); iny = band(ys, y0, Y1)
    vx = band(xs, x0, x1) | band(xs, X0, X1); hy = band(ys, y0, y1) | band(ys, Y0, Y1)
    m = (vx[None, :] & iny[:, None]) | (hy[:, None] & inx[None, :])
    return m
if __name__ == '__main__':
    d = json.load(open(f'{R}/triage/clusters_compact.json'))['thin-frame-stroke-fractional']
    for e in d:
        k = e['key']
        print(k)
        for b in e['bad']:
            z = b[0]
            idx = [i for i, zz in enumerate(LADDER) if zz == z][0]
            a = load(f'{R}/png/zl_zm_svg/{k}/{idx:02}.png')
            m = ring(z)
            parts = []
            for br in ['chr', 'ff', 'wk']:
                p = f'{R}/fresh/refs/{br}_{k}_{FR[z]}.png'
                if not os.path.exists(p): parts.append(f'{br}: -'); continue
                r = load(p)
                dd = np.abs(a - r).max(axis=2) > 8
                parts.append(f'{br}: {dd.sum():5d} ring {(dd & m).sum():5d} rest {(dd & ~m).sum():5d}')
            print(f'  z={z:<5} ' + ' | '.join(parts))
