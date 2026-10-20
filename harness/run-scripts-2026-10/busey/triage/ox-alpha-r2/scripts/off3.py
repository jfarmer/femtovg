"""off3.py PNG KEY FRAMING [box x0,y0,x1,y1 ...]: pixels more than 20/255 off chr, ff and wk refs (scratch refs/), agreed = browsers within 20 of each other; optional per-box counts."""
import sys, numpy as np
from PIL import Image
L = lambda p: np.asarray(Image.open(p).convert('RGB'), dtype=np.int16)
png, key, fr = sys.argv[1:4]
ours = L(png); refs = [L(f'refs/{b}_t__{key}_{fr}.png') for b in ('chr', 'ff', 'wk')]
off = [np.abs(ours - r).max(axis=2) > 20 for r in refs]
all3 = off[0] & off[1] & off[2]
spread = np.zeros(all3.shape, bool)
for i in range(3):
    for j in range(i + 1, 3):
        spread |= np.abs(refs[i] - refs[j]).max(axis=2) > 20
out = f'{png}: all3 {all3.sum()} agreed {(all3 & ~spread).sum()}  (vs chr {off[0].sum()} ff {off[1].sum()} wk {off[2].sum()})'
for b in sys.argv[4:]:
    x0, y0, x1, y1 = map(int, b.split(','))
    out += f' | box {b}: {all3[y0:y1, x0:x1].sum()}'
print(out)
np.save(png[:-4] + '_all3.npy', all3)
