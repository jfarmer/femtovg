"""femsim (port of master's concave fill, from grok-4-5-verify) with bevel_join ported in full (BEVEL and
INNERBEVEL-only branches, choose_bevel) and a switch for the fringe's join test: 'both' = femtovg master
(p1.flags.contains(BEVEL | INNERBEVEL)), 'either' = nanovg (flags & (BEVEL|INNERBEVEL)) != 0."""
import numpy as np
import femsim as fs
from femsim import CORNER, LEFT, BEVEL, INNER, orth
def expand(pts, fringe=1.0, miter=2.4, woff=0.5, test='both'):
    P = np.array([[p[0], p[1]] for p in pts], float); F = [p[2] for p in pts]
    n = len(P)
    area = 0.5*sum((P[(i+1) % n][0]-P[i][0])*(P[(i+1) % n][1]+P[i][1]) for i in range(n))
    if area < 0:
        P = P[::-1].copy(); F = F[::-1]
    d = np.roll(P, -1, axis=0) - P
    L = np.hypot(d[:, 0], d[:, 1]); D = d / L[:, None]
    dm = np.zeros_like(P); flags = []
    for i in range(n):
        j = i-1
        dm[i] = (orth(D[j]) + orth(D[i]))*0.5
        r2 = dm[i] @ dm[i]
        if r2 > 1e-6: dm[i] *= min(1/r2, 600.0)
        f = CORNER if F[i] & CORNER else 0
        if orth(D[j]) @ D[i] > 0: f |= LEFT
        lim = max(min(L[j], L[i])/fringe, 1.01)
        if r2*lim*lim < 1: f |= INNER
        if (f & CORNER) and r2*miter*miter < 1: f |= BEVEL
        flags.append(f)
    fill = []
    for i in range(n):
        j = i-1
        if flags[i] & BEVEL:
            if flags[i] & LEFT: fill.append(P[i] + dm[i]*woff)
            else: fill.append(P[i] + orth(D[j])*woff); fill.append(P[i] + orth(D[i])*woff)
        else:
            fill.append(P[i] + dm[i]*woff)
    lw, lu, rw, ru = fringe + woff, 0.0, fringe - woff, 1.0
    st = []
    for i in range(n):
        j = i-1; f = flags[i]; p = P[i]; dl0, dl1 = orth(D[j]), orth(D[i])
        use = ((f & BEVEL) and (f & INNER)) if test == 'both' else bool(f & (BEVEL | INNER))
        if use:
            inner = bool(f & INNER)
            def choose(w):
                return (p + dl0*w, p + dl1*w) if inner else (p + dm[i]*w, p + dm[i]*w)
            if f & LEFT:
                lp0, lp1 = choose(lw)
                st += [(lp0, lu), (p-dl0*rw, ru)]
                if f & BEVEL:
                    st += [(lp0, lu), (p-dl0*rw, ru), (lp1, lu), (p-dl1*rw, ru)]
                else:
                    rp0 = p - dm[i]*rw
                    st += [(p, 0.5), (p-dl0*rw, ru), (rp0, ru), (rp0, ru), (p, 0.5), (p-dl1*rw, ru)]
                st += [(lp1, lu), (p-dl1*rw, ru)]
            else:
                rp0, rp1 = choose(-rw)
                st += [(p+dl0*lw, lu), (rp0, ru)]
                if f & BEVEL:
                    st += [(p+dl0*lw, lu), (rp0, ru), (p+dl1*lw, lu), (rp1, ru)]
                else:
                    lp0 = p + dm[i]*lw
                    st += [(p+dl0*lw, lu), (p, 0.5), (lp0, lu), (lp0, lu), (p+dl1*lw, lu), (p, 0.5)]
                st += [(p+dl1*lw, lu), (rp1, ru)]
        else:
            st += [(p+dm[i]*lw, lu), (p-dm[i]*rw, ru)]
    st += [st[0], st[1]]
    return P, np.array(fill), st, flags, False
def render(paths, test='both', cull_sign=1, img=None):
    old = fs.expand
    fs.expand = lambda pts, woff=0.5, half=False: expand(pts, woff=woff, test=test)
    try:
        return fs.render(paths, img=img if img is not None else np.zeros((fs.H, fs.W)), cull_sign=cull_sign)
    finally:
        fs.expand = old
