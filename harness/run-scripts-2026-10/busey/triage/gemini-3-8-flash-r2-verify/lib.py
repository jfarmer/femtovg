import json, os, sys
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
RUN = '/Users/matt/src/femtovg-wt/runs/busey'
OKEY = 'corpus__buseybench__gemini-3-8-flash'
def L(p): return np.asarray(Image.open(p).convert('RGB'), dtype=np.int16)
def refs(name, fr):
    """chr, ff, wk, id for variant name (v00_orig -> the run's refs)."""
    out = {}
    for b in ('chr', 'ff', 'wk', 'id'):
        if name == 'v00_orig':
            p = f'{RUN}/refs/{b}_{OKEY}_{fr}.png'
        else:
            p = f'{HERE}/refs/{b}_t__{name}_{fr}.png'
        out[b] = L(p) if os.path.exists(p) else None
    return out
def ours(name, fr, tag=''):
    return L(f'{HERE}/png/{tag}{name}_{fr}.png')
def red(o, R, thr=20):
    off = [np.abs(o - R[b]).max(axis=2) > thr for b in ('chr', 'ff', 'wk')]
    all3 = off[0] & off[1] & off[2]
    sp = np.zeros(all3.shape, bool)
    bs = [R[b] for b in ('chr', 'ff', 'wk')]
    for i in range(3):
        for j in range(i + 1, 3):
            sp |= np.abs(bs[i] - bs[j]).max(axis=2) > thr
    return all3, all3 & ~sp, sp
def offid(o, R, thr=20):
    return np.abs(o - R['id']).max(axis=2) > thr
# framing transforms svg -> frame
def tf(fr):
    if fr == 'hd': return (lambda x, y: (420 + x * 1080 / 1024, y * 1080 / 1024)), 1080 / 1024
    if fr == 'z2': s = 200 / 1024 * 2; return (lambda x, y: (230 + (x - 512) * s, 130 + (y - 512) * s)), s
    if fr == 'z1': s = 200 / 1024; return (lambda x, y: (130 + x * s, 30 + y * s)), s
def inv(fr):
    f, s = tf(fr)
    if fr == 'hd': return lambda X, Y: ((X - 420) / s, Y / s)
    if fr == 'z2': return lambda X, Y: (512 + (X - 230) / s, 512 + (Y - 130) / s)
    if fr == 'z1': return lambda X, Y: ((X - 130) / s, (Y - 30) / s)
def label(m):
    """4-connected component labels (pure numpy/python union-find via BFS)."""
    h, w = m.shape
    lab = np.zeros((h, w), np.int32); n = 0
    ys, xs = np.nonzero(m)
    for y0, x0 in zip(ys, xs):
        if lab[y0, x0]: continue
        n += 1; st = [(y0, x0)]; lab[y0, x0] = n
        while st:
            y, x = st.pop()
            for dy, dx in ((1,0),(-1,0),(0,1),(0,-1)):
                yy, xx = y+dy, x+dx
                if 0 <= yy < h and 0 <= xx < w and m[yy, xx] and not lab[yy, xx]:
                    lab[yy, xx] = n; st.append((yy, xx))
    return lab, n
def dilate(m, it=1):
    for _ in range(it):
        m = m | np.roll(m,1,0) | np.roll(m,-1,0) | np.roll(m,1,1) | np.roll(m,-1,1)
    return m
