"""o3.py PNG REFPREFIX FR [boxes]: REFPREFIX like /path/refs/{b}_KEY -> {b} in chr ff wk (id optional)."""
import sys, numpy as np, os
from PIL import Image
L = lambda p: np.asarray(Image.open(p).convert('RGB'), dtype=np.int16)
png, pre, fr = sys.argv[1:4]
ours = L(png); refs = [L(pre.format(b=b) + f'_{fr}.png') for b in ('chr', 'ff', 'wk')]
off = [np.abs(ours - r).max(axis=2) > 20 for r in refs]
all3 = off[0] & off[1] & off[2]
spread = np.zeros(all3.shape, bool)
for i in range(3):
    for j in range(i + 1, 3):
        spread |= np.abs(refs[i] - refs[j]).max(axis=2) > 20
s = f'{os.path.basename(png)}: all3 {all3.sum()} agreed {(all3 & ~spread).sum()} (chr {off[0].sum()} ff {off[1].sum()} wk {off[2].sum()})'
idp = pre.format(b='id') + f'_{fr}.png'
if os.path.exists(idp):
    idr = L(idp); s += f' | vs id: ours {(np.abs(ours-idr).max(2)>20).sum()} ' + ' '.join(f'{n} {(np.abs(r-idr).max(2)>20).sum()}' for n, r in zip(('chr','ff','wk'), refs))
for b in sys.argv[4:]:
    x0, y0, x1, y1 = map(int, b.split(','))
    s += f' | box {b}: {all3[y0:y1, x0:x1].sum()}'
print(s)
np.save(png[:-4] + '_all3.npy', all3)
