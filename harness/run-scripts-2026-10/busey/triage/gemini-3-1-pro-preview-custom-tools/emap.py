import sys, numpy as np
from PIL import Image
L = lambda p: np.asarray(Image.open(p).convert('RGB'), dtype=np.int16)
def masks(ours, refs):
    off = [np.abs(ours - r).max(axis=2) > 20 for r in refs]
    all3 = off[0] & off[1] & off[2]
    spread = np.zeros(all3.shape, bool)
    for i in range(3):
        for j in range(i+1,3):
            spread |= np.abs(refs[i]-refs[j]).max(axis=2) > 20
    return all3, all3 & ~spread, spread
def dilate(m, it):
    for _ in range(it):
        m = m | np.roll(m,1,0) | np.roll(m,-1,0) | np.roll(m,1,1) | np.roll(m,-1,1)
    return m
def label(m):
    lab = np.zeros(m.shape, int); n = 0
    H, W = m.shape
    for y in range(H):
        for x in range(W):
            if m[y,x] and not lab[y,x]:
                n += 1; st=[(y,x)]; lab[y,x]=n
                while st:
                    cy,cx = st.pop()
                    for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
                        ny,nx=cy+dy,cx+dx
                        if 0<=ny<H and 0<=nx<W and m[ny,nx] and not lab[ny,nx]:
                            lab[ny,nx]=n; st.append((ny,nx))
    return lab, n
if __name__ == '__main__':
    k = 'corpus__buseybench__gemini-3-1-pro-preview-custom-tools'
    ours = L(f'png/mst2_{k}_z2.png'); refs = [L(f'refs/{x}_{k}_z2.png') for x in ('chr','ff','wk')]
    a, ag, sp = masks(ours, refs)
    print('all3', a.sum(), 'agreed', ag.sum(), 'spread', sp.sum())
    # sign: ours brighter or darker vs mean refs
    m = np.mean(refs, axis=0)
    d = (ours - m).mean(axis=2)
    lab, n = label(dilate(a, 3))
    rows = []
    for i in range(1, n+1):
        mm = (lab == i) & a
        if not mm.any(): continue
        ys, xs = np.nonzero(mm)
        rows.append((mm.sum(), (mm & ag).sum(), xs.min(), ys.min(), xs.max(), ys.max(), d[mm].mean()))
    rows.sort(reverse=True)
    for r in rows[:25]:
        x0,y0,x1,y1 = r[2:6]
        # svg coords
        sx0, sy0 = (x0-30)/0.390625, (y0+70)/0.390625; sx1, sy1 = (x1-30)/0.390625, (y1+70)/0.390625
        print(f'{r[0]:4d} agreed {r[1]:4d} box ({x0},{y0})-({x1},{y1}) svg ({sx0:.0f},{sy0:.0f})-({sx1:.0f},{sy1:.0f}) ours-refs {r[6]:+.0f}')
