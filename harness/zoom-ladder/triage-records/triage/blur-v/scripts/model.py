# Independent blur models for an axis-aligned rect cropped to a filter region.
import math, numpy as np
from math import erf, sqrt, exp, pi
from PIL import Image

def Phi(t): return 0.5*(1+erf(t/sqrt(2)))
def phi(t): return exp(-t*t/2)/sqrt(2*pi)
def iPhi(t): return t*Phi(t)+phi(t)   # antiderivative of Phi

def exact1d(n, r0, r1, s, g0, g1):
    # pixel-integrated (analytic) profile of box [r0,r1] * N(0,s), cropped to [g0,g1]
    out = np.zeros(n)
    for i in range(n):
        a, b = max(i, g0), min(i+1, g1)
        if b <= a: continue
        F = lambda x: s*(iPhi((x-r0)/s) - iPhi((x-r1)/s))
        out[i] = F(b) - F(a)
    return out

def cov1d(n, r0, r1):
    return np.array([max(0.0, min(i+1, r1) - max(i, r0)) for i in range(n)])

def crop(v, g0, g1):
    v = v.copy()
    for i in range(len(v)):
        v[i] *= max(0.0, min(i+1, g1) - max(i, g0))
    return v

def sampled1d(n, r0, r1, s, g0, g1, R=None):
    c = cov1d(n, r0, r1)
    if R is None: R = math.ceil(3*s) - 1
    t = np.array([exp(-0.5*(j/s)**2) for j in range(-R, R+1)]); t /= t.sum()
    return crop(np.convolve(c, t, mode='same'), g0, g1)

def boxmean(v, lo, hi):
    n = len(v); w = hi-lo+1
    c = np.concatenate([[0.0], np.cumsum(v)])
    i = np.arange(n)
    return (c[np.clip(i+hi+1, 0, n)] - c[np.clip(i+lo, 0, n)])/w

def threebox1d(n, r0, r1, s, g0, g1):
    c = cov1d(n, r0, r1)
    d = max(1, int(math.floor(s*3*sqrt(2*pi)/4 + 0.5)))
    h = d//2
    if d % 2:
        v = boxmean(boxmean(boxmean(c, -h, h), -h, h), -h, h)
    else:
        v = boxmean(boxmean(boxmean(c, -h, h-1), -h+1, h), -h, h)
    return crop(v, g0, g1), d

def over_white(ax, ay, col):
    a = np.outer(ay, ax)
    return np.stack([col[k]*a + 255*(1-a) for k in range(3)], axis=-1)

def load(p): return np.asarray(Image.open(p).convert('RGB')).astype(float)

def cmp(a, b, mask=None):
    d = np.abs(a-b).max(axis=2)
    if mask is not None: d = d*mask
    return int((d > 8).sum()), int(round(d.max()))
