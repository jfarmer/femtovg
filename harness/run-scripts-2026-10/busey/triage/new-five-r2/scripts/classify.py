"""classify.py [names...] : every femtovg pixel > 20/255 off all three browsers, put in one class:
  area_ok     femtovg within 20/255 of the 8x area reference (the browsers share an error; femtovg is right)
  fill:tip    fixed by exact-area fills (FILL_MASKS), nearest fill corner within 1.5 px has an interior angle < 35 deg
  fill:corner fixed by FILL_MASKS, nearest fill corner within 1.5 px is convex, 35-160 deg
  fill:notch  fixed by FILL_MASKS, nearest fill corner within 1.5 px is reflex
  fill:edge   fixed by FILL_MASKS, no fill corner within 1.5 px
  stroke:roundcap / stroke:dashcorner / stroke:cap / other   not fixed by FILL_MASKS
Prints counts per portrait and framing and writes classes.json."""
import sys, os, json, math, numpy as np
from PIL import Image
S = '/Users/matt/src/femtovg-wt/runs/busey/triage/new-five-r2'
sys.path.insert(0, f'{S}/scripts')
from locate import elements, to_svg, S as FS, dist_poly
L = lambda p: np.asarray(Image.open(p).convert('RGB'), dtype=np.int16)
names = [a for a in sys.argv[1:] if '=' not in a] or ['claude-opus-5-5', 'claude-sonnet-5-5', 'gpt-6-1-sol', 'gpt-6-1-sol-pro', 'pareto']
R = '/Users/matt/src/femtovg-wt/runs/busey/refs'


def corners(P):
    """(point, interior angle deg, convex?) for vertices whose direction turns by > 25 deg."""
    P = np.asarray(P)
    if len(P) < 3: return []
    closed = np.allclose(P[0], P[-1])
    Q = P[:-1] if closed else P
    # drop repeated points
    keep = [0] + [i for i in range(1, len(Q)) if np.hypot(*(Q[i] - Q[i - 1])) > 1e-6]
    Q = Q[keep]
    while closed and len(Q) > 3 and np.hypot(*(Q[-1] - Q[0])) < 1e-6: Q = Q[:-1]
    n = len(Q)
    if n < 3: return []
    area = 0.5 * sum(Q[i][0] * Q[(i + 1) % n][1] - Q[(i + 1) % n][0] * Q[i][1] for i in range(n))
    out = []
    rng = range(n) if closed else range(1, n - 1)
    for i in rng:
        a, b, c = Q[i - 1], Q[i], Q[(i + 1) % n]
        d1, d2 = b - a, c - b
        n1, n2 = np.hypot(*d1), np.hypot(*d2)
        if n1 < 1e-9 or n2 < 1e-9: continue
        cr = (d1[0] * d2[1] - d1[1] * d2[0]) / n1 / n2
        dt = (d1 @ d2) / n1 / n2
        turn = math.degrees(math.atan2(cr, dt))
        if abs(turn) < 25: continue
        convex = (turn > 0) == (area > 0)
        interior = 180 - abs(turn) if convex else 180 + abs(turn)
        out.append((b, interior, convex))
    return out


res = {}
for n in names:
    els = elements(f'/Users/matt/src/femtovg-wt/da/corpus/buseybench/{n}.svg')
    fills = [e for e in els if e['kind'] == 'draw' and e['style'].get('fill', 'black') != 'none']
    strokes = [e for e in els if e['kind'] == 'draw' and e['sw'] > 0 and 'filter' not in e['attrs'] and not any('filter' in c[2] for c in e['ctx'])]
    fc = []
    for e in fills:
        for P in e['polys']:
            for (pt, ang, cv) in corners(P): fc.append((pt, ang, cv, e['line']))
    fcp = np.array([c[0] for c in fc]) if fc else np.zeros((0, 2))
    for fr in ('z2', 'hd'):
        k = 'corpus__buseybench__' + n
        o = L(f'{S}/png/mst4_{k}_{fr}.png'); fm = L(f'{S}/png/fm_{k}_{fr}.png')
        refs = [L(f'{R}/{x}_{k}_{fr}.png') for x in ('chr', 'ff', 'wk')]; idr = L(f'{R}/id_{k}_{fr}.png')
        def red(im):
            off = [np.abs(im - r).max(2) > 20 for r in refs]; return off[0] & off[1] & off[2]
        a3 = red(o); f3 = red(fm); oi = np.abs(o - idr).max(2) > 20
        sc = FS[fr][2]
        cnt = {}; detail = []
        for y, x in zip(*np.nonzero(a3)):
            u, v = to_svg(fr, x, y); p = np.array([u, v])
            if not oi[y, x]: c = 'area_ok'; ln = None
            elif not f3[y, x]:
                c = 'fill:edge'; ln = None
                if len(fcp):
                    dd = np.hypot(*(fcp - p).T) * sc
                    # reach of a corner: 1.5 px, or along an acute wedge as far as it is narrower than 1.5 px
                    reach = np.array([max(1.5, 1.5 / (2 * math.tan(math.radians(a_) / 2))) if cv_ else 1.5 for (_, a_, cv_, _) in fc])
                    j = int((dd / reach).argmin())
                    if dd[j] <= reach[j]:
                        pt, ang, cv, ln = fc[j]
                        c = 'fill:tip' if (cv and ang < 35) else ('fill:corner' if cv else 'fill:notch')
            else:
                c = 'other'; ln = None; best = 1e9
                for e in strokes:
                    cap = e['style'].get('stroke-linecap', 'butt'); dash = e['style'].get('stroke-dasharray', e['attrs'].get('stroke-dasharray'))
                    for P in e['polys']:
                        if len(P) < 2: continue
                        lo, hi = P.min(0) - 3 / sc - e['sw'], P.max(0) + 3 / sc + e['sw']
                        if not (lo[0] <= u <= hi[0] and lo[1] <= v <= hi[1]): continue
                        if dash and dash != 'none':
                            for (pt, ang, cv) in corners(P):
                                dd = np.hypot(*(pt - p)) * sc
                                if dd <= 1.5 + e['sw'] * sc / 2 and dd < best: best = dd; c = 'stroke:dashcorner'; ln = e['line']
                        closed = np.allclose(P[0], P[-1])
                        if not closed:
                            for end in (P[0], P[-1]):
                                dd = np.hypot(*(end - p)) * sc
                                if dd <= 1.0 + e['sw'] * sc / 2 and dd < best:
                                    best = dd; c = 'stroke:roundcap' if cap == 'round' else 'stroke:cap'; ln = e['line']
            cnt[c] = cnt.get(c, 0) + 1; detail.append((int(x), int(y), c, ln))
        res[f'{n}_{fr}'] = {'total': int(a3.sum()), 'classes': cnt, 'pixels': detail}
        print(f'{n:18s} {fr} total {a3.sum():3d} ', ' '.join(f'{k2} {v}' for k2, v in sorted(cnt.items(), key=lambda kv: -kv[1])))
json.dump(res, open(f'{S}/classes.json', 'w'), indent=0)
