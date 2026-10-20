"""cmp.py SCRATCH name[:build-tag] ... : off-all-three (>20) counts, total and per region, for frames in SCRATCH/png."""
import sys, numpy as np
from PIL import Image
S = sys.argv[1]
L = lambda p: np.asarray(Image.open(p).convert('RGB'), dtype=np.int16)
REG = {'temples': (115, 75, 345, 125), 'eyes': (150, 125, 310, 160), 'ears': (100, 125, 360, 200), 'mouth': (150, 200, 310, 260)}
def stats(o, refs):
    off = [np.abs(o - r).max(2) > 20 for r in refs]
    a = off[0] & off[1] & off[2]
    sp = np.zeros(a.shape, bool)
    for i in range(3):
        for j in range(i + 1, 3):
            sp |= np.abs(refs[i] - refs[j]).max(2) > 20
    return a, sp, off
for arg in sys.argv[2:]:
    name, _, tag = arg.partition(':')
    tag = tag or 'mst2'
    o = L(f'{S}/png/{tag}_t__{name}_z2.png')
    refs = [L(f'{S}/refs/{x}_t__{name}_z2.png') for x in ('chr', 'ff', 'wk')]
    a, sp, off = stats(o, refs)
    reg = ' '.join(f'{k}={a[y0:y1, x0:x1].sum()}' for k, (x0, y0, x1, y1) in REG.items())
    print(f'{arg:26s} all3 {a.sum():5d} agreed {(a & ~sp).sum():5d}  off chr {off[0].sum():5d} ff {off[1].sum():5d} wk {off[2].sum():5d} | {reg}')
