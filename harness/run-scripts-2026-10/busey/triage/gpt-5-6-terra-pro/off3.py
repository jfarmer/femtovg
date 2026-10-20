import sys, numpy as np
from PIL import Image
L = lambda p: np.asarray(Image.open(p).convert('RGB'), dtype=np.int16)
def off3(ours, refs):
    h = min([ours.shape[0]] + [r.shape[0] for r in refs]); w = min([ours.shape[1]] + [r.shape[1] for r in refs])
    ours = ours[:h, :w]; refs = [r[:h, :w] for r in refs]
    off = [np.abs(ours - r).max(axis=2) > 20 for r in refs]
    all3 = off[0] & off[1] & off[2]
    spread = np.zeros((h, w), bool)
    for i in range(3):
        for j in range(i + 1, 3):
            spread |= np.abs(refs[i] - refs[j]).max(axis=2) > 20
    return all3, spread
if __name__ == '__main__':
    o = L(sys.argv[1]); refs = [L(p) for p in sys.argv[2:5]]
    a, s = off3(o, refs)
    print('all3', a.sum(), 'agreed', (a & ~s).sum(), 'spread', s.sum())
