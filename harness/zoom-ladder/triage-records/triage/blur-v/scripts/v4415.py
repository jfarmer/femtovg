import sys; sys.path.insert(0, sys.path[0])
from model import *
import numpy as np
H='/Users/matt/src/femtovg-wt/runs/zoom'
key = sys.argv[1]; step = sys.argv[2]; fr = sys.argv[3]
rx0, ry0, rx1, ry1 = map(float, sys.argv[4].split(','))
sx, sy = map(float, sys.argv[5].split(','))
col = (0, 128, 0)
W, Hh = 460, 260
imgs = {}
imgs['fvg'] = load(f'{H}/png/zl_zm_svg/{key}/{step}.png')
for b in ('chr', 'ff', 'wk'):
    try: imgs[b] = load(f'{H}/fresh/refs/{b}_{key}_{fr}.png')
    except FileNotFoundError: pass
imgs['exact'] = over_white(exact1d(W, rx0, rx1, sx, rx0, rx1), exact1d(Hh, ry0, ry1, sy, ry0, ry1), col)
imgs['sampled'] = over_white(sampled1d(W, rx0, rx1, sx, rx0, rx1), sampled1d(Hh, ry0, ry1, sy, ry0, ry1), col)
tbx, dx = threebox1d(W, rx0, rx1, sx, rx0, rx1); tby, dy = threebox1d(Hh, ry0, ry1, sy, ry0, ry1)
imgs[f'3box{dx},{dy}'] = over_white(tbx, tby, col)
names = list(imgs)
print(' '*10 + ''.join('%-12s' % n for n in names))
for a in names:
    print('%-10s' % a + ''.join('%-12s' % ('%d(%d)' % cmp(imgs[a], imgs[b])) for b in names))
