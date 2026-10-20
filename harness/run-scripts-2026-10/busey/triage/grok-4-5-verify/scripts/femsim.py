"""A port of femtovg master (09f5174c) concave antialiased fill: PathCache flattening (tesselate_bezier with
CHORD_SHIFT), calculate_joins, expand_fill (concave branch), and the wgpu concave_fill passes (stencil fan,
fringe strip with stencil==0 and back-face culling, cover where stencil!=0), rasterized at pixel centres.
Switches let parts of the mechanism be turned off to attribute the excess."""
import numpy as np
W, H = 460, 260
S = 0.390625
def dev(u, v): return (30 + u * S, -70 + v * S)
TESS, DIST = 0.125, 0.01
CHORD_SHIFT = 0.375
CORNER, LEFT, BEVEL, INNER = 1, 2, 4, 8

def flatten(segs):
    """segs: list of ('M',x,y) ('L',x,y) ('Q',cx,cy,x,y) ('C',...) in user units; returns [(x,y,flags)] device."""
    pts = []
    def add(x, y, f):
        if pts and (pts[-1][0]-x)**2 + (pts[-1][1]-y)**2 < DIST*DIST:
            pts[-1][2] |= f; return
        pts.append([x, y, f])
    last = None
    for s in segs:
        if s[0] in 'ML':
            x, y = dev(s[1], s[2]); add(x, y, CORNER); last = (s[1], s[2])
        else:
            if s[0] == 'Q':
                cx, cy, ex, ey = s[1:]
                x0, y0 = last
                c1 = (x0 + (cx-x0)*2/3, y0 + (cy-y0)*2/3); c2 = (ex + (cx-ex)*2/3, ey + (cy-ey)*2/3)
            else:
                c1, c2, (ex, ey) = (s[1], s[2]), (s[3], s[4]), (s[5], s[6])
            p0 = (pts[-1][0], pts[-1][1])
            curve = [p0[0], p0[1], *dev(*c1), *dev(*c2), *dev(ex, ey)]
            bez(curve, pts, add)
            last = (ex, ey)
    if len(pts) > 1 and (pts[0][0]-pts[-1][0])**2 + (pts[0][1]-pts[-1][1])**2 < DIST*DIST:
        pts.pop()
    return pts

def bez(curve, pts, add):
    pending = []
    piece, depth = curve, 0
    held = None
    last = [curve[0], curve[1]]
    while True:
        x1, y1, x2, y2, x3, y3, x4, y4 = piece
        dx, dy = x4-x1, y4-y1
        d2 = (x2-x4)*dy - (y2-y4)*dx
        d3 = (x3-x4)*dy - (y3-y4)*dx
        chord = dx*dx + dy*dy
        if (abs(d2)+abs(d3))**2 < TESS*chord:
            bend = -CHORD_SHIFT*0.5*(d2+d3)/chord if chord > 0 else 0.0
            shift = (-dy*bend, dx*bend)
            prev = held; held = ((x4, y4), shift)
            if prev is not None:
                at, ps = prev
                mean = ((ps[0]+shift[0])*0.5, (ps[1]+shift[1])*0.5)
                p = (at[0]+mean[0], at[1]+mean[1])
                if (p[0]-last[0])**2 + (p[1]-last[1])**2 >= DIST*DIST:
                    pts.append([p[0], p[1], 0]); last = list(p)
        elif depth < 10:
            x12, y12 = (x1+x2)/2, (y1+y2)/2; x23, y23 = (x2+x3)/2, (y2+y3)/2; x34, y34 = (x3+x4)/2, (y3+y4)/2
            x123, y123 = (x12+x23)/2, (y12+y23)/2; x234, y234 = (x23+x34)/2, (y23+y34)/2
            x1234, y1234 = (x123+x234)/2, (y123+y234)/2
            depth += 1
            pending.append(([x1234, y1234, x234, y234, x34, y34, x4, y4], depth))
            piece = [x1, y1, x12, y12, x123, y123, x1234, y1234]
            continue
        if not pending: break
        piece, depth = pending.pop()
    if held is not None:
        add(held[0][0], held[0][1], CORNER)

def orth(v): return np.array([v[1], -v[0]])

def expand(pts, fringe=1.0, miter=2.4, woff=0.5, half=False):
    P = np.array([[p[0], p[1]] for p in pts], float); F = [p[2] for p in pts]
    n = len(P)
    area = 0.5*sum((P[(i+1) % n][0]-P[i][0])*(P[(i+1) % n][1]+P[i][1]) for i in range(n))
    # PointPairsIter on area: (prev,curr) pairs: sum over (p1.x-p0.x)*(p1.y+p0.y) same up to orientation
    if area < 0:
        P = P[::-1].copy(); F = F[::-1]
    d = np.roll(P, -1, axis=0) - P
    L = np.hypot(d[:, 0], d[:, 1]); D = d / L[:, None]
    dm = np.zeros_like(P); flags = []
    nleft = 0
    for i in range(n):
        j = i-1
        dm[i] = (orth(D[j]) + orth(D[i]))*0.5
        r2 = dm[i] @ dm[i]
        if r2 > 1e-6: dm[i] *= min(1/r2, 600.0)
        f = CORNER if F[i] & CORNER else 0
        cross = orth(D[j]) @ D[i]
        if cross > 0: f |= LEFT; nleft += 1
        lim = max(min(L[j], L[i])/fringe, 1.01)
        if r2*lim*lim < 1: f |= INNER
        if (f & CORNER) and r2*miter*miter < 1: f |= BEVEL
        flags.append(f)
    fill = []
    for i in range(n):
        j = i-1
        if flags[i] & BEVEL:
            if flags[i] & LEFT: fill.append(P[i] + dm[i]*woff)
            else:
                fill.append(P[i] + orth(D[j])*woff); fill.append(P[i] + orth(D[i])*woff)
        else:
            fill.append(P[i] + dm[i]*woff)
    lw, lu, rw, ru = fringe + woff, 0.0, fringe - woff, 1.0
    if half: lw, lu = woff, 0.5
    st = []
    for i in range(n):
        j = i-1
        f = flags[i]; p = P[i]; dl0, dl1 = orth(D[j]), orth(D[i])
        if (f & BEVEL) and (f & INNER):
            if f & LEFT:
                lp0, lp1 = (p+dl0*lw, p+dl1*lw)  # INNER set
                st += [(lp0, lu), (p-dl0*rw, ru), (lp0, lu), (p-dl0*rw, ru), (lp1, lu), (p-dl1*rw, ru), (lp1, lu), (p-dl1*rw, ru)]
            else:
                rp0, rp1 = (p-dl0*rw, p-dl1*rw)
                st += [(p+dl0*lw, lu), (rp0, ru), (p+dl0*lw, lu), (rp0, ru), (p+dl1*lw, lu), (rp1, ru), (p+dl1*lw, lu), (rp1, ru)]
        else:
            st += [(p+dm[i]*lw, lu), (p-dm[i]*rw, ru)]
    st += [st[0], st[1]]
    return P, np.array(fill), st, flags, nleft == n

def raster_tri(a, b, c):
    """pixel-centre coverage mask and barycentrics over the bbox; returns (ys, xs, l0, l1, l2, sign)."""
    xs0 = max(int(np.floor(min(a[0], b[0], c[0]))), 0); xs1 = min(int(np.ceil(max(a[0], b[0], c[0]))), W)
    ys0 = max(int(np.floor(min(a[1], b[1], c[1]))), 0); ys1 = min(int(np.ceil(max(a[1], b[1], c[1]))), H)
    if xs1 <= xs0 or ys1 <= ys0: return None
    yy, xx = np.mgrid[ys0:ys1, xs0:xs1]
    px = xx + 0.5 + 1.3e-6; py = yy + 0.5 + 0.7e-6
    area = (b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0])
    if area == 0: return None
    w0 = ((b[0]-px)*(c[1]-py) - (b[1]-py)*(c[0]-px)) / area
    w1 = ((c[0]-px)*(a[1]-py) - (c[1]-py)*(a[0]-px)) / area
    w2 = 1 - w0 - w1
    m = (w0 >= 0) & (w1 >= 0) & (w2 >= 0)
    return yy[m], xx[m], w0[m], w1[m], w2[m], np.sign(area)

def render(paths, img=None, cull_sign=None, parts=('cover', 'fringe'), woff=0.5, half=False, stencil_mode=None, log=None):
    if img is None: img = np.zeros((H, W))
    for segs in paths:
        pts = flatten(segs)
        P, fill, st, flags, convex = expand(pts, woff=woff, half=half)
        assert not convex
        stencil = np.zeros((H, W), int)
        for k in range(1, len(fill)-1):
            r = raster_tri(fill[0], fill[k], fill[k+1])
            if r is None: continue
            ys, xs, *_, sg = r
            np.add.at(stencil, (ys, xs), int(sg))
        if stencil_mode == 'no_inverted':
            vals, cnt = np.unique(stencil[stencil != 0], return_counts=True)
            body = vals[np.argmax(cnt)]
            stencil = np.where(stencil == body, stencil, 0)
        elif stencil_mode == 'none':
            stencil = np.zeros_like(stencil)
        fr = np.zeros((H, W)); cov = np.zeros((H, W))
        if 'fringe' in parts:
            for k in range(len(st)-2):
                (a, ua), (b, ub), (c, uc) = st[k], st[k+1], st[k+2]
                r = raster_tri(a, b, c)
                if r is None: continue
                ys, xs, l0, l1, l2, sg = r
                eff = sg if k % 2 == 0 else -sg
                if cull_sign is not None and eff == cull_sign: continue
                u = l0*ua + l1*ub + l2*uc
                al = np.clip(1 - np.abs(u*2 - 1), 0, 1)
                ok = stencil[ys, xs] == 0
                ys, xs, al = ys[ok], xs[ok], al[ok]
                for y_, x_, a_ in zip(ys, xs, al):
                    img[y_, x_] = img[y_, x_] + a_*(1 - img[y_, x_])
                    fr[y_, x_] = fr[y_, x_] + a_*(1 - fr[y_, x_])
        if 'cover' in parts:
            m = stencil != 0
            img[m] = 1.0; cov[m] = 1.0
        if log is not None: log.append(dict(P=P, fill=fill, st=st, flags=flags, stencil=stencil, fringe=fr, cover=cov))
    return img
