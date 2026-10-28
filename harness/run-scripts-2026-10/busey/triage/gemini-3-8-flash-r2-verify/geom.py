import numpy as np, re
def parse(d):
    toks = re.findall(r'[MLCQZmlcqz]|-?[\d.]+', d)
    pts = []; i = 0; cur = None; start = None; cmd = None
    segs = []
    while i < len(toks):
        t = toks[i]
        if t in 'MLCQZ': cmd = t; i += 1
        if cmd == 'Z':
            segs.append(('L', cur, start)); cur = start; cmd = None; continue
        n = {'M': 2, 'L': 2, 'C': 6, 'Q': 4}[cmd]
        v = [float(x) for x in toks[i:i + n]]; i += n
        if cmd == 'M': cur = start = (v[0], v[1]); cmd = 'L'
        elif cmd == 'L': segs.append(('L', cur, (v[0], v[1]))); cur = (v[0], v[1])
        elif cmd == 'C': segs.append(('C', cur, (v[0], v[1]), (v[2], v[3]), (v[4], v[5]))); cur = (v[4], v[5])
        elif cmd == 'Q': segs.append(('Q', cur, (v[0], v[1]), (v[2], v[3]))); cur = (v[2], v[3])
    return segs
def flatten(segs, n=400):
    P = []
    for s in segs:
        t = np.linspace(0, 1, n + 1)[:-1][:, None]
        if s[0] == 'L':
            a, b = np.array(s[1]), np.array(s[2]); P.append(a + (b - a) * t)
        elif s[0] == 'C':
            p0, p1, p2, p3 = map(np.array, s[1:])
            P.append((1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t * t * p2 + t ** 3 * p3)
        elif s[0] == 'Q':
            p0, p1, p2 = map(np.array, s[1:])
            P.append((1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t * t * p2)
    return np.concatenate(P)
def area_perim(P):
    x, y = P[:, 0], P[:, 1]; x2, y2 = np.roll(x, -1), np.roll(y, -1)
    A = 0.5 * abs((x * y2 - x2 * y).sum()); per = np.hypot(x2 - x, y2 - y).sum()
    return A, per
