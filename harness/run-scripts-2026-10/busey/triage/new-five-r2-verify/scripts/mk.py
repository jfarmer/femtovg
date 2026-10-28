"""mk.py: my own synthetic reductions (svg/) + geometry records (svg/*.json) in device space for the analytic reference."""
import json, math, os, numpy as np
from geom import svgc, dev, FS
D = '/Users/matt/src/femtovg-wt/runs/busey/triage/new-five-r2-verify'
HEAD = '<svg viewBox="0 0 1024 1024" width="1024" height="1024" xmlns="http://www.w3.org/2000/svg">\n<rect width="1024" height="1024" fill="#000"/>\n'
def P(fr, pts): return ' '.join(f'{svgc(fr,x,y)[0]:.5f} {svgc(fr,x,y)[1]:.5f}' for x, y in pts)
def path(fr, pts, fill='#fff'):
    return f'<path d="M{P(fr, pts[:1])} L{P(fr, pts[1:])} Z" fill="{fill}"/>'
files = []; geo = {}
# ---- V1 corners (hd geometry) ----
fr = 'hd'; body = []; shapes = []
offs = [-0.3, -0.15, 0.0, 0.15, 0.3]
for j, dy in enumerate(offs):
    for i, dx in enumerate(offs):
        ox, oy = 600 + i * 30 + 0.5 + dx, 60 + j * 30 + 0.5 + dy
        sq = [(ox, oy), (ox + 16, oy), (ox + 16, oy + 16), (ox, oy + 16)]
        body.append(path(fr, sq)); shapes.append({'kind': 'square', 'pts': sq, 'convex': [1, 1, 1, 1]})
        ox, oy = 600 + i * 30 + 0.5 + dx, 230 + j * 30 + 0.5 + dy
        L = [(ox - 8, oy - 8), (ox, oy - 8), (ox, oy), (ox + 8, oy), (ox + 8, oy + 8), (ox - 8, oy + 8)]
        body.append(path(fr, L)); shapes.append({'kind': 'L', 'pts': L, 'convex': [1, 1, 0, 1, 1, 1]})
rng = np.random.default_rng(7)
for k in range(12):
    cx, cy = 600 + (k % 6) * 40 + rng.random(), 420 + (k // 6) * 40 + rng.random(); a = math.radians(10 + k * 6.5)
    sq = [(cx + 9 * math.cos(a + t * math.pi / 2), cy + 9 * math.sin(a + t * math.pi / 2)) for t in range(4)]
    body.append(path(fr, sq)); shapes.append({'kind': 'rot', 'pts': sq, 'convex': [1, 1, 1, 1]})
# straight-sided spikes, tip angle 20..90, tip at pixel centre + offsets (convex triangles)
for k, ang in enumerate([20, 30, 45, 60, 75, 90]):
    for m, (dx, dy) in enumerate([(0, 0), (0.25, 0.1), (-0.2, 0.3)]):
        tx, ty = 600 + k * 30 + 0.5 + dx, 520 + m * 30 + 0.5 + dy; h = 14; hw = h * math.tan(math.radians(ang / 2))
        tri = [(tx, ty), (tx + hw, ty + h), (tx - hw, ty + h)]
        body.append(path(fr, tri)); shapes.append({'kind': f'spike{ang}', 'pts': tri, 'convex': [1, 1, 1]})
open(f'{D}/svg/v_corners.svg', 'w').write(HEAD + '\n'.join(body) + '\n</svg>\n'); geo['v_corners'] = {'fr': fr, 'shapes': shapes}
# ---- V2 round caps sweep (hd) ----
body = []; lines = []
widths = [1.0, 1.3, 1.5, 1.6, 1.7, 2.0, 2.5, 3.0, 3.1, 3.5, 4.0, 5.0, 6.0]
s = FS[fr][2]
for i, w in enumerate(widths):
    for j, (px, py) in enumerate([(0.0, 0.0), (0.25, 0.25), (0.5, 0.0), (0.75, 0.4)]):
        for cap, col in (('round', 0), ('butt', 1)):
            for ang, row in ((0, 0), (35, 1)):
                x0, y0 = 600 + j * 60 + col * 240 + px + 0.5, 40 + i * 30 + row * 400 + py + 0.5
                L = 16; x1, y1 = x0 + L * math.cos(math.radians(ang)), y0 - L * math.sin(math.radians(ang))
                a, b = svgc(fr, x0, y0), svgc(fr, x1, y1)
                body.append(f'<path d="M{a[0]:.5f} {a[1]:.5f} L{b[0]:.5f} {b[1]:.5f}" stroke="#fff" fill="none" stroke-width="{w / s:.5f}" stroke-linecap="{cap}"/>')
                lines.append({'w': w, 'cap': cap, 'a': (x0, y0), 'b': (x1, y1), 'ang': ang})
open(f'{D}/svg/v_caps.svg', 'w').write(HEAD + '\n'.join(body) + '\n</svg>\n'); geo['v_caps'] = {'fr': fr, 'lines': lines}
# ---- V3 dash: opus L229 geometry, white, no opacity, on black ----
body = ['<path d="M 404 918 L 358 924 L 452 1020" fill="none" stroke="#fff" stroke-width="1.5" stroke-dasharray="5 4"/>']
open(f'{D}/svg/v_dash.svg', 'w').write(HEAD + '\n'.join(body) + '\n</svg>\n')
body = ['<path d="M 404 918 L 358 924 L 452 1020" fill="none" stroke="#fff" stroke-width="1.5" stroke-dasharray="5 4" stroke-dashoffset="-4"/>']
open(f'{D}/svg/v_dash_gap.svg', 'w').write(HEAD + '\n'.join(body) + '\n</svg>\n')
# ---- V4 crescent: opus L381 lower lip, white on black, and a synthetic cubic crescent ----
lip = 'M 413 672 C 430 728 468 758 512 760 C 556 758 594 728 611 672 C 600 742 560 776 512 778 C 464 776 424 742 413 672 Z'
open(f'{D}/svg/v_lip.svg', 'w').write(HEAD + f'<path d="{lip}" fill="#fff"/>\n</svg>\n')
# synthetic: thin crescent, tips 20 deg-ish, two cubics
cres = 'M 300 300 C 330 360 400 380 460 340 C 410 400 330 380 300 300 Z'
open(f'{D}/svg/v_cres.svg', 'w').write(HEAD + f'<path d="{cres}" fill="#fff"/>\n</svg>\n')
geo['v_lip'] = {'d': lip}; geo['v_cres'] = {'d': cres}
json.dump(geo, open(f'{D}/svg/geo.json', 'w'))
names = ['v_corners', 'v_caps', 'v_dash', 'v_dash_gap', 'v_lip', 'v_cres']
json.dump([{'path': f'{D}/svg/{n}.svg', 'key': f't__{n}', 'group': 't'} for n in names], open(f'{D}/files.json', 'w'))
print(names)
