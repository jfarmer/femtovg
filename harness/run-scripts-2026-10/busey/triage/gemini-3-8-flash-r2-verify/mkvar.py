"""Variants of the portrait: drop lines / replace lines. Writes svg/NAME.svg and files.json."""
import json, math, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = '/Users/matt/src/femtovg-wt/da/corpus/buseybench/gemini-3-8-flash.svg'
lines = open(SRC).read().split('\n')
def var(name, drop=(), repl=None, insert_end=None):
    out = []
    for i, l in enumerate(lines, 1):
        if i in drop: continue
        if repl and i in repl: l = repl[i]
        out.append(l)
    if insert_end:
        out.insert(len(out) - 2, insert_end)
    open(f'{HERE}/svg/{name}.svg', 'w').write('\n'.join(out))
    return name
def dash_arcs(cx, cy, r, on, off, stroke, sw, op):
    C = 2 * math.pi * r; s = 0; d = []
    while s < C:
        e = min(s + on, C)
        a0, a1 = s / r, e / r
        x0, y0 = cx + r * math.cos(a0), cy + r * math.sin(a0)
        x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
        d.append(f'M {x0:.4f},{y0:.4f} A {r},{r} 0 0 1 {x1:.4f},{y1:.4f}')
        s += on + off
    return f'      <path d="{" ".join(d)}" fill="none" stroke="{stroke}" stroke-width="{sw}" opacity="{op}"/>'
names = []
names.append(var('v01_no_lower_lip', drop={546}))
names.append(var('v02_no_upper_lip', drop={448}))
names.append(var('v03_no_nose_cres', drop={416}))
names.append(var('v04_no_iris_dashes', drop={277, 312}))
names.append(var('v05_iris_presplit', repl={277: dash_arcs(423, 452, 15, 2, 3, '#9ee5ff', 1.5, 0.8),
                                           312: dash_arcs(600, 448, 14.5, 2, 3, '#9ee5ff', 1.5, 0.8)}))
names.append(var('v06_caps_butt', repl={610: lines[609].replace('stroke-linecap="round"', 'stroke-linecap="butt"')}))
# teeth strokes removed (fills kept)
tl = {465, 466, 469, 473, 477, 485, 496, 500, 504, 505}
names.append(var('v07_no_teeth_strokes', repl={i: re.sub(r' stroke="[^"]*" stroke-width="[^"]*"', '', lines[i - 1]) for i in tl}))
# crow's feet: the light strokes' groups without the default black fill
names.append(var('v08_crow_fill_none', repl={336: lines[335].replace('<g ', '<g fill="none" '), 349: lines[348].replace('<g ', '<g fill="none" '),
                                             330: lines[329].replace('<g ', '<g fill="none" '), 343: lines[342].replace('<g ', '<g fill="none" ')}))
names.append(var('v09_no_filters', repl={i: re.sub(r' filter="url\(#[^)]*\)"', '', l) for i, l in enumerate(lines, 1) if 'filter="url' in l}))
names.append(var('v10_no_catchlights', drop={281, 316}))
json.dump([{'path': f'{HERE}/svg/{n}.svg', 'key': f't__{n}', 'group': 't'} for n in names], open(f'{HERE}/files_v.json', 'w'))
print(names)
