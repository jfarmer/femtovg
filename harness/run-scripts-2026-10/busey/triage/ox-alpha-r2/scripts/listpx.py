"""listpx.py PNG KEY FRAMING: every off-all-three pixel with ours / chr / ff / wk / id (id from runs/busey refs when the key is an original) and svg coordinates."""
import sys, numpy as np
from PIL import Image
L = lambda p: np.asarray(Image.open(p).convert('RGB'), dtype=np.int16)
png, key, fr = sys.argv[1:4]
idp = sys.argv[4] if len(sys.argv) > 4 else f'refs/id_t__{key}_{fr}.png'
ours = L(png); refs = [L(f'refs/{b}_t__{key}_{fr}.png') for b in ('chr', 'ff', 'wk')]
try: idr = L(idp)
except Exception: idr = None
off = [np.abs(ours - r).max(axis=2) > 20 for r in refs]
all3 = off[0] & off[1] & off[2]
def svg(x, y):
    if fr == 'hd': s = 1080 / 1024; return (x + .5 - 420) / s, (y + .5) / s
    z = {'z1': 1, 'z2': 2, 'z4': 4}[fr]; s = 200 / 1024 * z; return 512 + (x + .5 - 230) / s, 512 + (y + .5 - 130) / s
for y, x in zip(*np.nonzero(all3)):
    sx, sy = svg(x, y)
    vals = [ours[y, x]] + [r[y, x] for r in refs] + ([idr[y, x]] if idr is not None else [])
    print(f'({x},{y}) svg({sx:.1f},{sy:.1f}) ' + ' | '.join(','.join(str(int(c)) for c in v) for v in vals))
