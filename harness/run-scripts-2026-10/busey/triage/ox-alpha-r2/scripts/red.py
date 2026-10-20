import sys, numpy as np
from PIL import Image
L = lambda p: np.asarray(Image.open(p).convert('RGB'), dtype=np.int16)
ours, refs = L(sys.argv[1]), [L(p) for p in sys.argv[2:5]]
h = min([ours.shape[0]] + [r.shape[0] for r in refs]); w = min([ours.shape[1]] + [r.shape[1] for r in refs])
ours = ours[:h, :w]; refs = [r[:h, :w] for r in refs]
off = [np.abs(ours - r).max(axis=2) > 20 for r in refs]
all3 = off[0] & off[1] & off[2]
spread = np.zeros((h, w), bool)
for i in range(3):
    for j in range(i + 1, 3):
        spread |= np.abs(refs[i] - refs[j]).max(axis=2) > 20
agreed = all3 & ~spread
print('all3', all3.sum(), 'agreed', agreed.sum(), 'vs chr', off[0].sum(), 'ff', off[1].sum(), 'wk', off[2].sum())
def dil(m, it):
    for _ in range(it):
        m = m | np.roll(m, 1, 0) | np.roll(m, -1, 0) | np.roll(m, 1, 1) | np.roll(m, -1, 1)
    return m
def label(m):
    lab = np.zeros(m.shape, int); n = 0
    for y, x in zip(*np.nonzero(m)):
        if lab[y, x]: continue
        n += 1; st = [(y, x)]; lab[y, x] = n
        while st:
            cy, cx = st.pop()
            for dy, dx in ((1,0),(-1,0),(0,1),(0,-1)):
                yy, xx = cy+dy, cx+dx
                if 0 <= yy < m.shape[0] and 0 <= xx < m.shape[1] and m[yy, xx] and not lab[yy, xx]:
                    lab[yy, xx] = n; st.append((yy, xx))
    return lab, n
lab, n = label(dil(all3, 6))
rows = []
for i in range(1, n + 1):
    m = (lab == i) & all3
    ys, xs = np.nonzero(m)
    if not len(ys): continue
    rows.append((m.sum(), (m & agreed).sum(), xs.min(), ys.min(), xs.max(), ys.max()))
for r in sorted(rows, reverse=True): print(r)
if len(sys.argv) > 5:
    np.save(sys.argv[5], all3)
