#!/usr/bin/env python3
"""Writes the reductions beside this script, 200 x 200 units so that z1 draws a unit to a pixel, z2 two (the band
y 40-160 that the z2 frame shows) and hd 5.4. White on black. shapes.json holds every stroke's geometry for
measure.py.

  caps.svg        15 widths, 0.5-8 units, one cell each (5 x 3 cells of 40 x 40 from y 40): a horizontal stroke
                  16 units long and one 16 long at -30 degrees, round caps; each cell at its own sub-pixel offset
  caps-butt.svg   the same strokes with butt caps
  joins.svg       open polylines, two legs of 10 units, butt caps, round joins: widths 1.5, 2.5, 4 and 6 (rows)
                  turning by 30, 60, 90 and 120 degrees (columns), 4 x 4 cells of 50 x 30 from y 40
  joins-miter.svg the same polylines with miter joins (stroke-miterlimit 10)
  joins-bevel.svg the same polylines with bevel joins
  repro.svg       the issue's repro: sheet-caps.svg's four strokes and a 3-unit polyline turning 90 degrees, round
                  caps and joins
  sheet-caps.svg  the sheet's rows at z1, sides on quarter pixels (where Chromium's rows of samples agree with
  sheet-joins.svg the area): horizontal 12-unit strokes 1.5, 2, 3 and 4 wide, round caps; two polylines 2 and 3
                  wide turning 90 degrees, round join, butt caps
"""
import json, math, os

HERE = os.path.dirname(os.path.abspath(__file__))
WIDTHS = [0.5, 0.75, 1, 1.25, 1.5, 1.75, 2, 2.5, 3, 3.5, 4, 5, 6, 7, 8]
JOIN_WIDTHS = [1.5, 2.5, 4, 6]
TURNS = [30, 60, 90, 120]
HEAD = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="200" height="200">\n<rect width="200" height="200" fill="#000"/>\n'


def f(v):
    return f'{v:.4f}'.rstrip('0').rstrip('.')


def caps():
    lines = []
    for i, w in enumerate(WIDTHS):
        cx, cy = 40 * (i % 5), 40 + 40 * (i // 5)
        fx, fy = (0.37 * i) % 1, (0.61 * i) % 1
        a = (cx + 10 + fx, cy + 12 + fy)
        lines.append({'w': w, 'a': a, 'b': (a[0] + 16, a[1])})
        a = (cx + 10 + fx, cy + 31 + fy)
        lines.append({'w': w, 'a': a, 'b': (a[0] + 16 * math.cos(math.radians(30)), a[1] - 16 * math.sin(math.radians(30)))})
    return lines


def joins():
    polys = []
    for j, w in enumerate(JOIN_WIDTHS):
        for k, t in enumerate(TURNS):
            cx, cy = 50 * k, 40 + 30 * j
            fx, fy = (0.41 * (4 * j + k)) % 1, (0.23 * (4 * j + k)) % 1
            corner = (cx + 24 + fx, cy + 9 + fy)
            start = (corner[0] - 10, corner[1])
            end = (corner[0] + 10 * math.cos(math.radians(t)), corner[1] + 10 * math.sin(math.radians(t)))
            polys.append({'w': w, 'turn': t, 'pts': [start, corner, end]})
    return polys


def write(name, body):
    open(f'{HERE}/{name}', 'w').write(HEAD + body + '</svg>\n')


def main():
    cl = caps()
    for cap in ('round', 'butt'):
        write('caps.svg' if cap == 'round' else 'caps-butt.svg', ''.join(
            f'<path d="M{f(l["a"][0])} {f(l["a"][1])} L{f(l["b"][0])} {f(l["b"][1])}" stroke="#fff" stroke-width="{f(l["w"])}" '
            f'stroke-linecap="{cap}" fill="none"/>\n' for l in cl))
    jl = joins()
    for join in ('round', 'miter', 'bevel'):
        write('joins.svg' if join == 'round' else f'joins-{join}.svg', ''.join(
            f'<path d="M{" L".join(f(x) + " " + f(y) for x, y in p["pts"])}" stroke="#fff" stroke-width="{f(p["w"])}" '
            f'stroke-linejoin="{join}" stroke-miterlimit="10" fill="none"/>\n' for p in jl))
    rl = [{'w': w, 'a': (x, y), 'b': (x + 12, y)} for w, y, x in ((1.5, 74.5, 74.3), (2, 79, 74.55), (3, 84.5, 74.8), (4, 91, 75.05))]
    rj = {'w': 3, 'turn': 90, 'pts': [(104.25, 75.25), (120.75, 75.25), (120.75, 83.25)]}
    write('repro.svg', '<g stroke="#fff" fill="none" stroke-linecap="round" stroke-linejoin="round">\n' + ''.join(
        f'  <path d="M{f(l["a"][0])} {f(l["a"][1])} h12" stroke-width="{f(l["w"])}"/>\n' for l in rl) +
        '  <path d="M104.25 75.25 h16.5 v8" stroke-width="3"/>\n</g>\n')
    sc = []
    for w, y, x in ((1.5, 74.5, 74.3), (2, 79, 74.55), (3, 84.5, 74.8), (4, 91, 75.05)):
        sc.append({'w': w, 'a': (x, y), 'b': (x + 12, y)})
    write('sheet-caps.svg', ''.join(
        f'<path d="M{f(l["a"][0])} {f(l["a"][1])} h12" stroke="#fff" stroke-width="{f(l["w"])}" stroke-linecap="round"/>\n'
        for l in sc))
    sj = [{'w': 2, 'turn': 90, 'pts': [(72.25, 76), (84, 76), (84, 85)]},
          {'w': 3, 'turn': 90, 'pts': [(74.25, 89.25), (90.75, 89.25), (90.75, 97.25)]}]
    write('sheet-joins.svg', ''.join(
        f'<path d="M{" L".join(f(x) + " " + f(y) for x, y in p["pts"])}" stroke="#fff" stroke-width="{f(p["w"])}" '
        f'stroke-linejoin="round" fill="none"/>\n' for p in sj))
    json.dump({'caps': cl, 'joins': jl, 'repro': rl, 'repro_join': rj, 'sheet_caps': sc, 'sheet_joins': sj}, open(f'{HERE}/shapes.json', 'w'), indent=1)


main()
