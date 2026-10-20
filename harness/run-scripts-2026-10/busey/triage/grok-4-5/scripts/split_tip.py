"""split_tip.py IN OUT 'TIP_X,TIP_Y,WIDTH_SVG_UNITS' ... : for each M/Q/Z (absolute) path with a vertex at TIP,
cut the sliver tip off where the two curves meeting at it are WIDTH apart, as a separate path with the same
attributes; the rest of the path keeps its shape (the seam is a shared straight edge)."""
import re, sys, math
import numpy as np

def parse(d):
    t = re.findall(r'[MQZLmqzl]|-?[\d.]+', d)
    i = 0; segs = []; cur = None; start = None
    while i < len(t):
        c = t[i]; i += 1
        if c == 'M':
            cur = (float(t[i]), float(t[i+1])); start = cur; i += 2
        elif c == 'Q':
            while i < len(t) and t[i] not in 'MQZLmqzl':
                c1 = (float(t[i]), float(t[i+1])); p = (float(t[i+2]), float(t[i+3])); i += 4
                segs.append((cur, c1, p)); cur = p
        elif c == 'L':
            while i < len(t) and t[i] not in 'MQZLmqzl':
                p = (float(t[i]), float(t[i+1])); i += 2
                segs.append((cur, ((cur[0]+p[0])/2, (cur[1]+p[1])/2), p)); cur = p
        elif c in 'Zz':
            if cur != start:
                segs.append((cur, ((cur[0]+start[0])/2, (cur[1]+start[1])/2), start))
            cur = start
        else:
            raise ValueError(c)
    return segs

def ev(s, t):
    p0, c, p1 = map(np.array, s)
    return (1-t)**2*p0 + 2*(1-t)*t*c + t*t*p1

def split(s, t):
    p0, c, p1 = map(np.array, s)
    a = p0 + (c-p0)*t; b = c + (p1-c)*t; m = a + (b-a)*t
    return (tuple(p0), tuple(a), tuple(m)), (tuple(m), tuple(b), tuple(p1))

def fmt(p): return f'{p[0]:.3f} {p[1]:.3f}'

def cut(segs, tip, width):
    n = len(segs)
    for k in range(n):
        if np.allclose(segs[k][0], tip) and np.allclose(segs[k-1][2], tip):
            break
    else:
        return None
    A, B = segs[k-1], segs[k]   # A ends at the tip, B starts at it
    ts = np.linspace(0, 1, 4001)
    pb = np.array([ev(B, t) for t in ts])
    best = None
    for ta in np.linspace(1, 0, 4001)[1:]:
        pa = ev(A, ta)
        dd = np.hypot(*(pb - pa).T); j = dd.argmin()
        if dd[j] >= width:
            best = (ta, ts[j]); break
    ta, tb = best
    A0, A1 = split(A, ta); B0, B1 = split(B, tb)
    tipd = f'M{fmt(A1[0])} Q{fmt(A1[1])} {fmt(A1[2])} Q{fmt(B0[1])} {fmt(B0[2])}Z'
    body = [A0] + [None] + [B1] + [segs[(k+1+i) % n] for i in range(n-2)]
    d = f'M{fmt(A0[0])} Q{fmt(A0[1])} {fmt(A0[2])} L{fmt(B1[0])}'
    for s in body[2:]:
        d += f' Q{fmt(s[1])} {fmt(s[2])}'
    d += 'Z'
    return d, tipd, (ta, tb, tuple(np.round(ev(A, ta), 2)), tuple(np.round(ev(B, tb), 2)))

src = open(sys.argv[1]).read()
for spec in sys.argv[3:]:
    x, y, w = map(float, spec.split(','))
    done = False
    def rep(m):
        global done
        if done: return m.group(0)
        tag = m.group(0); d = re.search(r' d="([^"]+)"', tag).group(1)
        try:
            segs = parse(d)
        except ValueError:
            return tag
        r = cut(segs, (x, y), w)
        if r is None: return tag
        body, tipd, info = r
        done = True
        print(spec, 'cut at', info, file=sys.stderr)
        return tag.replace(d, body) + '\n    ' + tag.replace(d, tipd)
    src = re.sub(r'<path [^>]*/>', rep, src)
    if not done: print(spec, 'NOT FOUND', file=sys.stderr)
open(sys.argv[2], 'w').write(src)
