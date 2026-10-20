# Reductions for the dash-split claim. viewBox 1024 like the portrait: 0.390625 px/unit at z2.
import os
D = os.path.dirname(os.path.abspath(__file__)) + '/svg'
HEAD = '<svg viewBox="0 0 1024 1024" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">\n<rect x="0" y="0" width="1024" height="1024" fill="#000"/>\n'
ROWS = [320 + 20 * i for i in range(20)]
X0, X1 = 200.0, 800.0

def write(name, body):
    open(f'{D}/{name}.svg', 'w').write(HEAD + body + '</svg>\n')

def f(v):
    return f'{v:.4f}'.rstrip('0').rstrip('.')

def line(y, step=None):
    if step is None:
        return f'M{f(X0)} {y} L{f(X1)} {y}'
    xs, x = [], X0
    while x < X1 - 1e-6:
        xs.append(x); x += step
    xs.append(X1)
    return f'M{f(xs[0])} {y} ' + ' '.join(f'L{f(v)} {y}' for v in xs[1:])

def dashes(on, off):
    out, a = [], X0
    while a < X1 - 1e-6:
        out.append((a, min(a + on, X1))); a += on + off
    return out

def grid_split(a, b, step):
    # interior vertices of the global grid X0 + k*step inside (a, b)
    import math
    k = math.floor((a - X0) / step) + 1
    pts = [a]
    while X0 + k * step < b - 1e-6:
        v = X0 + k * step
        if v > a + 1e-6:
            pts.append(v)
        k += 1
    pts.append(b)
    return pts

ST = 'stroke="#fff" stroke-width="1.5" fill="none"'

def dashed_case(name, on, off, step):
    body = ''.join(f'<path d="{line(y, step)}" {ST} stroke-dasharray="{on},{off}"/>\n' for y in ROWS)
    write(name, body)

def manual(name, on, off, step, mode):
    body = ''
    for y in ROWS:
        d = []
        for a, b in dashes(on, off):
            pts = grid_split(a, b, step) if step else [a, b]
            if mode == 'single' or len(pts) == 2:
                d.append(f'M{f(pts[0])} {y} ' + ' '.join(f'L{f(p)} {y}' for p in pts[1:]) if mode == 'join' else f'M{f(a)} {y} L{f(b)} {y}')
            elif mode == 'join':
                d.append(f'M{f(pts[0])} {y} ' + ' '.join(f'L{f(p)} {y}' for p in pts[1:]))
            else:  # split
                d.extend(f'M{f(p)} {y} L{f(q)} {y}' for p, q in zip(pts, pts[1:]))
        body += f'<path d="{" ".join(d)}" {ST}/>\n'
    write(name, body)

write('a00_solid', ''.join(f'<path d="{line(y)}" {ST}/>\n' for y in ROWS))
write('a01_solid_v13', ''.join(f'<path d="{line(y, 1.3)}" {ST}/>\n' for y in ROWS))
dashed_case('b23_dash', 2, 3, None)
dashed_case('b23_dash_v13', 2, 3, 1.3)
manual('b23_man_single', 2, 3, 1.3, 'single')
manual('b23_man_join', 2, 3, 1.3, 'join')
manual('b23_man_split', 2, 3, 1.3, 'split')
dashed_case('c32_dash', 3, 2, None)
dashed_case('c32_dash_v13', 3, 2, 1.3)
dashed_case('d812_dash', 8, 12, None)
dashed_case('d812_dash_v4', 8, 12, 4.0)
dashed_case('d812_dash_v13', 8, 12, 1.3)
manual('d812_man_split4', 8, 12, 4.0, 'split')
manual('d812_man_split13', 8, 12, 1.3, 'split')
manual('d812_man_join13', 8, 12, 1.3, 'join')
# isolated pieces: row i has pieces of length L_i every 20 units
LS = [0.25, 0.5, 0.75, 1.0, 1.28, 1.5, 2.0, 2.56, 3.0, 4.0, 5.12, 6.0, 8.0, 10.24, 12.0, 16.0, 20.0, 1.28, 2.56, 5.12]
body = ''
for y, L in zip(ROWS, LS):
    d = ' '.join(f'M{f(a)} {y} L{f(a + L)} {y}' for a in [X0 + 20 * k for k in range(30)])
    body += f'<path d="{d}" {ST}/>\n'
write('e_pieces', body)
print('\n'.join(sorted(os.listdir(D))))
