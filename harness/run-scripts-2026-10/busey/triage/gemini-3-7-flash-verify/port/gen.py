import math, os, re
S = os.path.dirname(os.path.abspath(__file__))
src = open('/Users/matt/src/femtovg-wt/da/corpus/buseybench/gemini-3-7-flash.svg').read()
pat = re.compile(r'<circle cx="(\d+)" cy="(\d+)" r="(\d+)" stroke="(#[0-9a-f]+)" stroke-width="1.5" stroke-dasharray="(\d),(\d)" fill="none"/>')
hits = pat.findall(src)
assert len(hits) == 4, hits
def arcs(cx, cy, r, on, off, joined=True):
    C = 2 * math.pi * r
    d, s = [], 0.0
    pt = lambda a: (cx + r * math.cos(a / r), cy + r * math.sin(a / r))
    while s < C - 1e-9:
        e = min(s + on, C)
        (x0, y0), (x1, y1) = pt(s), pt(e)
        d.append(f'M{x0:.4f} {y0:.4f} A{r} {r} 0 0 1 {x1:.4f} {y1:.4f}')
        s += on + off
    return ' '.join(d)
def sub(fn):
    return pat.sub(lambda m: fn(*m.groups()), src)
open(f'{S}/svg/p00_orig.svg', 'w').write(src)
open(f'{S}/svg/p01_nodash.svg', 'w').write(sub(lambda *g: ''))
open(f'{S}/svg/p02_dash_arcs.svg', 'w').write(sub(lambda cx, cy, r, col, on, off:
    f'<path d="{arcs(int(cx), int(cy), int(r), int(on), int(off))}" stroke="{col}" stroke-width="1.5" fill="none"/>'))
# the same rings solid, to compare ring ink scale
open(f'{S}/svg/p03_solid_rings.svg', 'w').write(sub(lambda cx, cy, r, col, on, off:
    f'<circle cx="{cx}" cy="{cy}" r="{r}" stroke="{col}" stroke-width="1.5" fill="none"/>'))
print(hits)
