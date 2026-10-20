import sys, math; sys.path.insert(0, '.')
from lib import *
def cd(r, tol):
    da = math.acos(r / (r + tol)) * 2; return max(2, math.ceil(math.pi / da))
def tri_raster(tris, W, H, x0, y0, x1, y1):
    """tris: list of (a,b,c) with (pos, u). Point-sample at pixel centres; first triangle wins (no overlap expected)."""
    ys, xs = np.mgrid[y0:y1, x0:x1]; px = xs + 0.5; py = ys + 0.5
    out = np.full(px.shape, np.nan)
    for (a, ua), (b, ub), (c, uc) in tris:
        den = (b[1]-c[1])*(a[0]-c[0]) + (c[0]-b[0])*(a[1]-c[1])
        if abs(den) < 1e-9: continue
        l1 = ((b[1]-c[1])*(px-c[0]) + (c[0]-b[0])*(py-c[1]))/den
        l2 = ((c[1]-a[1])*(px-c[0]) + (a[0]-c[0])*(py-c[1]))/den
        l3 = 1-l1-l2
        ins = (l1 >= -1e-9) & (l2 >= -1e-9) & (l3 >= -1e-9) & np.isnan(out)
        out[ins] = (l1*ua + l2*ub + l3*uc)[ins]
    return out
def stroke_cov(A, B, hw, ncap, fringe=1.0):
    """femtovg's straight stroke A->B with round caps: body quad + two cap fans, coverage per shader."""
    R = hw + fringe/2; mult = R/fringe
    t = np.array(B, float)-np.array(A, float); t /= np.hypot(*t); n = np.array([t[1], -t[0]])  # orthogonal() = (y,-x)
    A = np.array(A, float); B = np.array(B, float)
    tris = []
    q = [(A+n*R, 0.0), (A-n*R, 1.0), (B+n*R, 0.0), (B-n*R, 1.0)]
    tris += [(q[0], q[1], q[2]), (q[1], q[2], q[3])]
    for P, d in ((B, t), (A, -t)):
        nn = np.array([d[1], -d[0]])
        rim = [P + (math.cos(i/(ncap-1)*math.pi)*(-nn) + math.sin(i/(ncap-1)*math.pi)*d)*R for i in range(ncap)]
        for i in range(ncap-1): tris.append(((P, 0.5), (rim[i], 0.0), (rim[i+1], 0.0)))
    return tris, mult
