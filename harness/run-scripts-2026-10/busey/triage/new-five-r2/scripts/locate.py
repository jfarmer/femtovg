"""locate.py SVG fr x y [r=1.5] : SVG elements whose outline passes within r device px of frame pixel (x,y).
Also usable as a module: elements(svg) -> list of dicts with 'line','tag','attrs','polys' (device-independent, svg units),
'kind' ('draw' or 'clip'), 'sw' (stroke width in svg units or 0)."""
import sys, re, math
import xml.parsers.expat
import numpy as np

S = {'z2': (30.0, -70.0, 0.390625), 'hd': (420.0, 0.0, 1080 / 1024), 'z1': (130.0, 30.0, 200 / 1024), 'z4': (-170.0, -370.0, 0.78125)}


def to_svg(fr, x, y):
    ox, oy, s = S[fr]
    return ((x + 0.5 - ox) / s, (y + 0.5 - oy) / s)


class Node:
    def __init__(s, tag, attrs, line, parent):
        s.tag, s.attrs, s.line, s.parent, s.kids = tag, attrs, line, parent, []


def parse(path):
    root = Node('#doc', {}, 0, None); cur = [root]
    p = xml.parsers.expat.ParserCreate()
    def st(tag, attrs):
        n = Node(tag.split(':')[-1] if ':' in tag and not tag.startswith('svg') else tag, dict(attrs), p.CurrentLineNumber, cur[-1])
        cur[-1].kids.append(n); cur.append(n)
    def en(tag): cur.pop()
    p.StartElementHandler = st; p.EndElementHandler = en
    p.Parse(open(path, 'rb').read(), True)
    return root


def mat_mul(a, b):
    return [a[0] * b[0] + a[2] * b[1], a[1] * b[0] + a[3] * b[1], a[0] * b[2] + a[2] * b[3], a[1] * b[2] + a[3] * b[3],
            a[0] * b[4] + a[2] * b[5] + a[4], a[1] * b[4] + a[3] * b[5] + a[5]]


def parse_tf(t):
    m = [1, 0, 0, 1, 0, 0]
    for name, args in re.findall(r'(\w+)\s*\(([^)]*)\)', t or ''):
        v = [float(x) for x in re.findall(r'-?[\d.]+(?:e-?\d+)?', args)]
        if name == 'translate': n = [1, 0, 0, 1, v[0], v[1] if len(v) > 1 else 0]
        elif name == 'scale': n = [v[0], 0, 0, v[1] if len(v) > 1 else v[0], 0, 0]
        elif name == 'rotate':
            a = math.radians(v[0]); c, s_ = math.cos(a), math.sin(a)
            n = [c, s_, -s_, c, 0, 0]
            if len(v) == 3: n = mat_mul(mat_mul([1, 0, 0, 1, v[1], v[2]], n), [1, 0, 0, 1, -v[1], -v[2]])
        elif name == 'matrix': n = v
        elif name == 'skewX': n = [1, 0, math.tan(math.radians(v[0])), 1, 0, 0]
        elif name == 'skewY': n = [1, math.tan(math.radians(v[0])), 0, 1, 0, 0]
        else: continue
        m = mat_mul(m, n)
    return m


def flatten_d(d):
    toks = re.findall(r'[MmLlHhVvCcSsQqTtAaZz]|-?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?', d)
    polys = []; cur = []; i = 0; cmd = None; x = y = 0; sx = sy = 0; lc = None; lq = None
    def num():
        nonlocal i
        v = float(toks[i]); i += 1; return v
    def cubic(p0, p1, p2, p3, n=16):
        t = np.linspace(0, 1, n + 1)[1:, None]
        return list(map(tuple, ((1 - t) ** 3) * p0 + 3 * ((1 - t) ** 2) * t * p1 + 3 * (1 - t) * t * t * p2 + t ** 3 * p3))
    toks = re.findall(r'[A-Za-z]|-?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?', d)
    while i < len(toks):
      try:
        if re.match(r'[A-Za-z]', toks[i]): cmd = toks[i]; i += 1
        rel = cmd.islower(); c = cmd.upper()
        if c == 'Z':
            if cur: cur.append((sx, sy)); polys.append(cur); cur = []
            x, y = sx, sy; lc = lq = None
            continue
        if c == 'M':
            nx, ny = num(), num()
            if rel: nx += x; ny += y
            if cur: polys.append(cur)
            cur = [(nx, ny)]; x, y = sx, sy = nx, ny; cmd = 'l' if rel else 'L'; lc = lq = None; continue
        if c in 'LHV':
            if c == 'L': nx, ny = num(), num(); nx, ny = (nx + x, ny + y) if rel else (nx, ny)
            elif c == 'H': nx = num(); nx = nx + x if rel else nx; ny = y
            else: ny = num(); ny = ny + y if rel else ny; nx = x
            cur.append((nx, ny)); x, y = nx, ny; lc = lq = None; continue
        if c in 'CS':
            if c == 'C': x1, y1 = num(), num(); x1, y1 = (x1 + x, y1 + y) if rel else (x1, y1)
            else: x1, y1 = (2 * x - lc[0], 2 * y - lc[1]) if lc else (x, y)
            x2, y2, nx, ny = num(), num(), num(), num()
            if rel: x2 += x; y2 += y; nx += x; ny += y
            cur += cubic(np.array([x, y]), np.array([x1, y1]), np.array([x2, y2]), np.array([nx, ny]))
            lc = (x2, y2); lq = None; x, y = nx, ny; continue
        if c in 'QT':
            if c == 'Q': qx, qy = num(), num(); qx, qy = (qx + x, qy + y) if rel else (qx, qy)
            else: qx, qy = (2 * x - lq[0], 2 * y - lq[1]) if lq else (x, y)
            nx, ny = num(), num()
            if rel: nx += x; ny += y
            p0 = np.array([x, y]); q = np.array([qx, qy]); p3 = np.array([nx, ny])
            cur += cubic(p0, p0 + 2 / 3 * (q - p0), p3 + 2 / 3 * (q - p3), p3)
            lq = (qx, qy); lc = None; x, y = nx, ny; continue
        if c == 'A':
            rx, ry, phi, fa, fs, nx, ny = num(), num(), num(), num(), num(), num(), num()
            if rel: nx += x; ny += y
            cur += arc(x, y, rx, ry, phi, int(fa), int(fs), nx, ny); x, y = nx, ny; lc = lq = None; continue
        raise ValueError(cmd)
      except (ValueError, IndexError, AttributeError, TypeError):
        break
    if cur: polys.append(cur)
    return polys


def arc(x1, y1, rx, ry, phi, fa, fs, x2, y2, n=24):
    if rx == 0 or ry == 0: return [(x2, y2)]
    rx, ry = abs(rx), abs(ry); p = math.radians(phi); c, s = math.cos(p), math.sin(p)
    dx, dy = (x1 - x2) / 2, (y1 - y2) / 2
    x1p, y1p = c * dx + s * dy, -s * dx + c * dy
    lam = x1p ** 2 / rx ** 2 + y1p ** 2 / ry ** 2
    if lam > 1: rx *= math.sqrt(lam); ry *= math.sqrt(lam)
    num_ = rx * rx * ry * ry - rx * rx * y1p * y1p - ry * ry * x1p * x1p
    co = math.sqrt(max(0, num_ / (rx * rx * y1p * y1p + ry * ry * x1p * x1p)))
    if fa == fs: co = -co
    cxp, cyp = co * rx * y1p / ry, -co * ry * x1p / rx
    cx, cy = c * cxp - s * cyp + (x1 + x2) / 2, s * cxp + c * cyp + (y1 + y2) / 2
    ang = lambda ux, uy, vx, vy: math.atan2(ux * vy - uy * vx, ux * vx + uy * vy)
    t1 = ang(1, 0, (x1p - cxp) / rx, (y1p - cyp) / ry)
    dt = ang((x1p - cxp) / rx, (y1p - cyp) / ry, (-x1p - cxp) / rx, (-y1p - cyp) / ry)
    if not fs and dt > 0: dt -= 2 * math.pi
    if fs and dt < 0: dt += 2 * math.pi
    out = []
    for k in range(1, n + 1):
        t = t1 + dt * k / n
        out.append((cx + rx * math.cos(t) * c - ry * math.sin(t) * s, cy + rx * math.cos(t) * s + ry * math.sin(t) * c))
    return out


def L(v, d=0.0):
    try: return float(re.match(r'-?[\d.]+', v).group())
    except Exception: return d


def shape_polys(n):
    a = n.attrs; t = n.tag
    if t == 'path': return flatten_d(a.get('d', ''))
    if t == 'rect':
        x, y, w, h = L(a.get('x', '0')), L(a.get('y', '0')), L(a.get('width', '0')), L(a.get('height', '0'))
        rx = L(a.get('rx', a.get('ry', '0'))); ry = L(a.get('ry', a.get('rx', '0')))
        rx, ry = min(rx, w / 2), min(ry, h / 2)
        if rx <= 0: return [[(x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)]]
        pts = []
        for cx, cy, a0 in ((x + w - rx, y + ry, -90), (x + w - rx, y + h - ry, 0), (x + rx, y + h - ry, 90), (x + rx, y + ry, 180)):
            for k in range(9):
                th = math.radians(a0 + 90 * k / 8); pts.append((cx + rx * math.cos(th), cy + ry * math.sin(th)))
        return [pts + [pts[0]]]
    if t in ('ellipse', 'circle'):
        cx, cy = L(a.get('cx', '0')), L(a.get('cy', '0'))
        rx = L(a.get('r', '0')) if t == 'circle' else L(a.get('rx', '0'))
        ry = L(a.get('r', '0')) if t == 'circle' else L(a.get('ry', '0'))
        th = np.linspace(0, 2 * np.pi, 97)
        return [list(zip(cx + rx * np.cos(th), cy + ry * np.sin(th)))]
    if t == 'line': return [[(L(a.get('x1', '0')), L(a.get('y1', '0'))), (L(a.get('x2', '0')), L(a.get('y2', '0')))]]
    if t in ('polyline', 'polygon'):
        v = [float(q) for q in re.findall(r'-?[\d.]+', a.get('points', ''))]
        p = list(zip(v[::2], v[1::2]))
        return [p + ([p[0]] if t == 'polygon' else [])]
    return []


INH = ('fill', 'stroke', 'stroke-width', 'stroke-dasharray', 'stroke-linecap', 'stroke-linejoin')


def elements(path):
    root = parse(path); ids = {}
    def index(n):
        if 'id' in n.attrs: ids[n.attrs['id']] = n
        for k in n.kids: index(k)
    index(root)
    out = []
    def style(n, inh):
        s = dict(inh)
        for k in INH:
            if k in n.attrs: s[k] = n.attrs[k]
        for kv in n.attrs.get('style', '').split(';'):
            if ':' in kv:
                k, v = kv.split(':', 1)
                if k.strip() in INH: s[k.strip()] = v.strip()
        return s
    def walk(n, m, inh, ctx, kind):
        if n.tag in ('defs', 'clipPath', 'mask', 'pattern', 'filter', 'linearGradient', 'radialGradient', 'symbol', 'title', 'desc', 'style', 'marker'):
            return
        m2 = mat_mul(m, parse_tf(n.attrs.get('transform')))
        s = style(n, inh)
        c2 = ctx + [n]
        if n.tag == 'use':
            h = n.attrs.get('href') or n.attrs.get('xlink:href')
            ref = ids.get(h[1:]) if h else None
            if ref is not None:
                tx, ty = L(n.attrs.get('x', '0')), L(n.attrs.get('y', '0'))
                walk_ref(ref, mat_mul(m2, [1, 0, 0, 1, tx, ty]), s, c2, kind)
            return
        emit(n, m2, s, c2, kind)
        for k in n.kids: walk(k, m2, s, c2, kind)
    def walk_ref(n, m, inh, ctx, kind):
        m2 = mat_mul(m, parse_tf(n.attrs.get('transform')))
        s = style(n, inh)
        emit(n, m2, s, ctx + [n], kind)
        for k in n.kids: walk_ref(k, m2, s, ctx + [n], kind)
    def emit(n, m, s, ctx, kind):
        polys = shape_polys(n)
        if not polys: return
        polys = [np.array([(m[0] * x + m[2] * y + m[4], m[1] * x + m[3] * y + m[5]) for x, y in p]) for p in polys if len(p)]
        sc = math.sqrt(abs(m[0] * m[3] - m[1] * m[2]))
        sw = L(s.get('stroke-width', '1'), 1) * sc if s.get('stroke', 'none') != 'none' else 0
        anc = [c for c in ctx[:-1] if any(k in c.attrs for k in ('filter', 'clip-path', 'mask', 'opacity'))]
        out.append({'line': n.line, 'tag': n.tag, 'attrs': n.attrs, 'polys': polys, 'sw': sw, 'style': s, 'kind': kind,
                    'ctx': [(c.tag, c.line, {k: c.attrs[k] for k in ('filter', 'clip-path', 'mask', 'opacity', 'id') if k in c.attrs}) for c in anc],
                    'use_line': ctx[0].line if ctx and ctx[0].tag == 'use' else None,
                    'uses': [c.line for c in ctx if c.tag == 'use']})
    svg = [k for k in root.kids if k.tag.endswith('svg')][0]
    for k in svg.kids: walk(k, [1, 0, 0, 1, 0, 0], {'fill': 'black'}, [], 'draw')
    # clip-path shapes
    for cid, cn in ids.items():
        if cn.tag == 'clipPath':
            for k in cn.kids:
                if k.tag == 'use':
                    h = k.attrs.get('href') or k.attrs.get('xlink:href'); ref = ids.get(h[1:])
                    if ref is not None: walk_ref(ref, parse_tf(k.attrs.get('transform')), {'fill': 'black'}, [cn, k], 'clip:' + cid)
                else: walk_ref(k, [1, 0, 0, 1, 0, 0], {'fill': 'black'}, [cn], 'clip:' + cid)
    return out


def dist_poly(p, P):
    a = P[:-1]; b = P[1:]; ab = b - a; ap = p - a
    t = np.clip((ap * ab).sum(1) / np.maximum((ab * ab).sum(1), 1e-12), 0, 1)
    q = a + ab * t[:, None]
    return np.sqrt(((p - q) ** 2).sum(1)).min() if len(a) else 1e9


def near(els, u, v, r_svg):
    hits = []
    p = np.array([u, v])
    for i, e in enumerate(els):
        best = 1e9
        for P in e['polys']:
            if len(P) < 2: continue
            lo, hi = P.min(0) - r_svg - e['sw'], P.max(0) + r_svg + e['sw']
            if not (lo[0] <= u <= hi[0] and lo[1] <= v <= hi[1]): continue
            best = min(best, dist_poly(p, P))
        if e['sw']:
            d = abs(best - e['sw'] / 2)
        else:
            d = best
        if d <= r_svg: hits.append((i, d))
    return hits


def describe(e):
    a = e['attrs']; s = e['style']
    k = {x: a[x] for x in ('id', 'filter', 'opacity', 'clip-path', 'mask', 'stroke-dasharray') if x in a}
    return f"L{e['line']}{' via use L'+str(e['uses']) if e['uses'] else ''} {e['kind']} <{e['tag']}> fill={s.get('fill')} stroke={s.get('stroke')} sw={e['sw']:.2f} {k} ctx={e['ctx']}"


if __name__ == '__main__':
    svg, fr, x, y = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
    r = float(sys.argv[5]) if len(sys.argv) > 5 else 1.5
    els = elements(svg); u, v = to_svg(fr, x, y)
    print(f'svg ({u:.1f},{v:.1f})')
    for i, d in near(els, u, v, r / S[fr][2]):
        print(f'  d={d * S[fr][2]:.2f}px', describe(els[i]))
