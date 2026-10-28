"""vsid.py PNG KEY FRAMING: pixels more than 20/255 off the area reference, for ours and each browser."""
import sys, numpy as np
from PIL import Image
L = lambda p: np.asarray(Image.open(p).convert('RGB'), dtype=np.int16)
png, key, fr = sys.argv[1:4]
idr = L(sys.argv[4] if len(sys.argv) > 4 else f'refs/id_t__{key}_{fr}.png')
row = {'ours': L(png)} | {b: L(f'refs/{b}_t__{key}_{fr}.png') for b in ('chr', 'ff', 'wk')}
print(png, ' '.join(f'{n} {int((np.abs(v - idr).max(2) > 20).sum())}' for n, v in row.items()), '(px > 20 off the area reference)')
