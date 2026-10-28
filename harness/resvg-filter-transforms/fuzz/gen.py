#!/usr/bin/env python3
"""Structured SVG filter fuzz cases: random filter chains under extreme transforms, units, regions and parameters.

  gen.py OUTDIR COUNT SEED
"""
import os, random, sys

out, count, seed = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
rng = random.Random(seed)
os.makedirs(out, exist_ok=True)


def num(lo, hi, log=False):
    if log:
        import math
        v = math.exp(rng.uniform(math.log(lo), math.log(hi)))
    else:
        v = rng.uniform(lo, hi)
    return f'{v:.6g}'


def extreme(lo, hi):
    """A value from the edges: 0, tiny, huge, negative, or ordinary."""
    return rng.choice(['0', num(1e-6, 1e-2, True), num(1e3, 1e7, True), f'-{num(0.1, 1e4, True)}', num(lo, hi)])


def transform():
    parts = []
    for _ in range(rng.randint(0, 3)):
        k = rng.choice(['rotate', 'skewX', 'skewY', 'scale', 'translate', 'matrix', 'nearskew'])
        if k == 'rotate':
            parts.append(f'rotate({num(-360, 360)} {num(0, 200)} {num(0, 200)})')
        elif k in ('skewX', 'skewY'):
            parts.append(f'{k}({rng.choice([num(-60, 60), num(89, 89.9999), num(-89.9999, -89)])})')
        elif k == 'nearskew':
            parts.append(f'skewX({rng.choice(["89.99", "89.999", "-89.9999", "90"])})')
        elif k == 'scale':
            parts.append(f'scale({rng.choice([num(1e-5, 1e-2, True), num(0.1, 10), num(10, 1e4, True), "-1"])} {rng.choice(["", num(0.01, 100, True), "-1", "1e-6"])})')
        elif k == 'translate':
            parts.append(f'translate({extreme(-200, 200)} {num(-200, 200)})')
        else:
            a, b, c, d = (num(-2, 2) for _ in range(4))
            if rng.random() < 0.4:  # nearly singular
                c, d = f'{float(a) * 1.00001:.8g}', f'{float(b) * 1.00001:.8g}'
            parts.append(f'matrix({a} {b} {c} {d} {num(-100, 100)} {num(-100, 100)})')
    return ' '.join(parts)


def subregion(obb):
    attrs = []
    for k in ('x', 'y', 'width', 'height'):
        if rng.random() < 0.35:
            if obb:
                attrs.append(f'{k}="{rng.choice([num(-1, 2), extreme(-1, 2), num(0, 100) + "%"])}"')
            else:
                attrs.append(f'{k}="{extreme(-100, 300)}"')
    return ' '.join(attrs)


def primitive(i, obb):
    prev = f'r{i - 1}' if i else 'SourceGraphic'
    src = rng.choice([prev, prev, 'SourceGraphic', 'SourceAlpha'])
    sub = subregion(obb)
    k = rng.choice(['blur', 'blur', 'morph', 'morph', 'offset', 'flood', 'tile', 'image', 'turb', 'turb', 'convolve',
                    'diffuse', 'specular', 'displace', 'shadow', 'composite', 'merge', 'matrix', 'transfer', 'blend'])
    r = f'result="r{i}"'
    if k == 'blur':
        return f'<feGaussianBlur in="{src}" stdDeviation="{extreme(0, 20)} {rng.choice(["", extreme(0, 20)])}" {sub} {r}/>'
    if k == 'morph':
        return f'<feMorphology in="{src}" operator="{rng.choice(["erode", "dilate"])}" radius="{extreme(0, 20)} {rng.choice(["", extreme(0, 20)])}" {sub} {r}/>'
    if k == 'offset':
        return f'<feOffset in="{src}" dx="{extreme(-50, 50)}" dy="{extreme(-50, 50)}" {sub} {r}/>'
    if k == 'flood':
        return f'<feFlood flood-color="#{rng.randrange(1 << 24):06x}" flood-opacity="{num(0, 1)}" {sub} {r}/>'
    if k == 'tile':
        return f'<feTile in="{src}" {sub} {r}/>'
    if k == 'image':
        return f'<feImage href="#{rng.choice(["shape", "grp", "missing"])}" {sub} {r}/>'
    if k == 'turb':
        return (f'<feTurbulence type="{rng.choice(["turbulence", "fractalNoise"])}" baseFrequency="{extreme(0, 0.2)}" '
                f'numOctaves="{rng.choice(["1", "4", "10", "100", "10000", "1e9"])}" seed="{rng.randint(-5, 1 << 31)}" '
                f'stitchTiles="{rng.choice(["stitch", "noStitch"])}" {sub} {r}/>')
    if k == 'convolve':
        n = rng.choice([1, 3, 5, 9, 15, 31])
        km = ' '.join(num(-1, 1) for _ in range(n * n))
        return f'<feConvolveMatrix in="{src}" order="{n}" kernelMatrix="{km}" edgeMode="{rng.choice(["duplicate", "wrap", "none"])}" {sub} {r}/>'
    if k in ('diffuse', 'specular'):
        light = rng.choice([f'<feDistantLight azimuth="{num(0, 360)}" elevation="{num(0, 90)}"/>',
                            f'<fePointLight x="{extreme(-100, 300)}" y="{num(-100, 300)}" z="{extreme(0, 300)}"/>',
                            f'<feSpotLight x="{num(-100, 300)}" y="{num(-100, 300)}" z="{num(0, 300)}" pointsAtX="100" pointsAtY="100" '
                            f'specularExponent="{extreme(1, 128)}" limitingConeAngle="{num(0, 90)}"/>'])
        tag = 'feDiffuseLighting' if k == 'diffuse' else 'feSpecularLighting'
        extra = f'specularExponent="{num(1, 128)}"' if k == 'specular' else ''
        return f'<{tag} in="{src}" surfaceScale="{extreme(0, 10)}" {extra} {sub} {r}>{light}</{tag}>'
    if k == 'displace':
        return f'<feDisplacementMap in="{src}" in2="{prev}" scale="{extreme(0, 50)}" xChannelSelector="R" yChannelSelector="A" {sub} {r}/>'
    if k == 'shadow':
        return f'<feDropShadow in="{src}" dx="{extreme(-20, 20)}" dy="{num(-20, 20)}" stdDeviation="{extreme(0, 20)}" {sub} {r}/>'
    if k == 'composite':
        op = rng.choice(['over', 'in', 'out', 'atop', 'xor', 'arithmetic', 'lighter'])
        ks = ' '.join(f'k{j}="{num(-2, 2)}"' for j in range(1, 5)) if op == 'arithmetic' else ''
        return f'<feComposite in="{src}" in2="{prev}" operator="{op}" {ks} {sub} {r}/>'
    if k == 'merge':
        nodes = ''.join(f'<feMergeNode in="{rng.choice([prev, "SourceGraphic", "SourceAlpha"])}"/>' for _ in range(rng.randint(1, 6)))
        return f'<feMerge {sub} {r}>{nodes}</feMerge>'
    if k == 'matrix':
        return f'<feColorMatrix in="{src}" type="{rng.choice(["saturate", "hueRotate", "luminanceToAlpha"])}" values="{num(0, 2)}" {sub} {r}/>'
    if k == 'transfer':
        return f'<feComponentTransfer in="{src}" {sub} {r}><feFuncA type="table" tableValues="{" ".join(num(0, 1) for _ in range(rng.randint(1, 64)))}"/></feComponentTransfer>'
    return f'<feBlend in="{src}" in2="{prev}" mode="{rng.choice(["multiply", "screen", "plus-lighter", "color-dodge"])}" {sub} {r}/>'


def case():
    obb = rng.random() < 0.5
    funits = rng.choice(['objectBoundingBox', 'userSpaceOnUse'])
    fattrs = []
    for k in ('x', 'y', 'width', 'height'):
        if rng.random() < 0.5:
            wild = rng.random() < 0.2
            if funits == 'objectBoundingBox':
                v = extreme(-1, 2) if wild else (num(-0.5, 0.2) if k in 'xy' else num(0.5, 2.5))
            else:
                v = extreme(-100, 400) if wild else (num(-50, 100) if k in 'xy' else num(50, 400))
            fattrs.append(f'{k}="{v}"')
    n = rng.choice([1, 1, 2, 3, 5, 8, 30, 120])
    prims = '\n    '.join(primitive(i, obb) for i in range(n))
    shape = rng.choice(['<rect id="shape" x="40" y="50" width="120" height="80" fill="seagreen"/>',
                        '<circle id="shape" cx="100" cy="100" r="50" fill="#36c"/>',
                        f'<rect id="shape" x="40" y="50" width="{extreme(0, 100)}" height="{extreme(0, 100)}" fill="red"/>',
                        '<path id="shape" d="M 20 20 L 180 40 L 60 180 Z" fill="orange" stroke="black"/>'])
    nest = rng.randint(0, 3)
    body = f'<g id="grp" filter="url(#f)" transform="{transform()}">{shape}</g>'
    for _ in range(nest):
        body = f'<g transform="{transform()}"{" filter=\"url(#f)\"" if rng.random() < 0.3 else ""}>{body}</g>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200">\n'
            f'  <filter id="f" filterUnits="{funits}" primitiveUnits="{"objectBoundingBox" if obb else "userSpaceOnUse"}" '
            f'{" ".join(fattrs)}>\n    {prims}\n  </filter>\n  {body}\n</svg>\n')


for i in range(count):
    open(f'{out}/c{seed}_{i:05}.svg', 'w').write(case())
print(count, 'cases in', out)
