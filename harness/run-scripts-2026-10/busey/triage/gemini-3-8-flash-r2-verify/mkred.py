import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = '/Users/matt/src/femtovg-wt/da/corpus/buseybench/gemini-3-8-flash.svg'
L = open(SRC).read().split('\n')
HEAD = '<svg viewBox="0 0 1024 1024" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">'
defs = '\n'.join(L[1:132])  # <defs> ... </defs>
def red(name, bg, body, use_defs=False):
    s = HEAD + '\n' + (defs + '\n' if use_defs else '') + f'<rect width="1024" height="1024" fill="{bg}"/>\n' + body + '\n</svg>\n'
    open(f'{HERE}/svg/{name}.svg', 'w').write(s); return name
n = []
n.append(red('r10_lip_skin', '#df9a78', L[545]))
n.append(red('r11_lip_dark', '#1f0305', L[545]))
n.append(red('r12_nose', '#e8a080', L[415]))
caps = '\n'.join(L[i - 1] for i in (616, 617, 629, 634, 636, 637, 638, 639))
n.append(red('r20_caps_round', '#11161d', '<g fill="none" stroke-linecap="round" opacity="0.85">\n' + caps + '\n</g>'))
n.append(red('r21_caps_butt', '#11161d', '<g fill="none" stroke-linecap="butt" opacity="0.85">\n' + caps + '\n</g>'))
teeth = [465, 466, 469, 473, 477, 485, 496, 500, 504, 505]
import re
n.append(red('r22_teeth', '#3d090d', '\n'.join(re.sub(r'url\(#teethTop\)', '#f7f3e6', L[i - 1]) for i in teeth)))
n.append(red('r24_teeth_strokeonly', '#f7f3e6', '\n'.join(re.sub(r'fill="[^"]*"', 'fill="none"', L[i - 1]) for i in teeth)))
n.append(red('r25_teeth_fillonly', '#3d090d', '\n'.join(re.sub(r' stroke="[^"]*" stroke-width="[^"]*"', '', re.sub(r'url\(#teethTop\)', '#f7f3e6', L[i - 1])) for i in teeth)))
# axis-aligned squares, stroke 1.8, several sub-pixel phases, for the corner model
sq = []
for k in range(6):
    x0 = 300 + k * 70 + k * 0.17; y0 = 600 + k * 0.23
    sq.append(f'<path d="M {x0:.2f},{y0:.2f} L {x0+40:.2f},{y0:.2f} L {x0+40:.2f},{y0+40:.2f} L {x0:.2f},{y0+40:.2f} Z" fill="none" stroke="#2b0a07" stroke-width="1.8"/>')
n.append(red('r26_squares', '#f7f3e6', '\n'.join(sq)))
sqr = [s.replace('stroke-width="1.8"', 'stroke-width="1.8" stroke-linejoin="round"') for s in sq]
n.append(red('r27_squares_round', '#f7f3e6', '\n'.join(sqr)))
# darts with the lip's 4.14 degree tip: one segment per side vs collinear points every 10 units
import math
def dart(name, step):
    # tip at (300,500), axis +x, half-angle 2.07 deg, length 200; notch in the base keeps it concave
    ha = math.radians(4.14 / 2); Lx = 200
    top = [(300 + t, 500 - t * math.tan(ha)) for t in ([0, Lx] if not step else [i * step for i in range(int(Lx / step) + 1)])]
    bot = [(x, 1000 - y) for x, y in top][::-1]
    pts = top + [(300 + Lx - 6, 500)] + bot  # notch
    d = 'M ' + ' L '.join(f'{x:.4f},{y:.4f}' for x, y in pts) + ' Z'
    return red(name, '#df9a78', f'<path d="{d}" fill="#ab4f47"/>\n<path d="{d}" fill="#ab4f47" transform="translate(800,600.37) rotate(180) translate(-300,-500)"/>')
n.append(dart('r30_dart', 0))
n.append(dart('r31_dart_split10', 10))
json.dump([{'path': f'{HERE}/svg/{x}.svg', 'key': f't__{x}', 'group': 'r'} for x in n], open(f'{HERE}/files_r.json', 'w'))
print(n)
