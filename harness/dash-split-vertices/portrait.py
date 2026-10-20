#!/usr/bin/env python3
"""Variants of corpus/buseybench/gemini-3-7-flash.svg for the four dashed iris rings (lines 297/298 and 347/348:
<circle r=21 stroke-dasharray=3,2> and <circle r=16 stroke-dasharray=2,3>, stroke-width 1.5).

  p00_orig          the file as it is
  p01_nodash        the four dashed circles removed (the base the ring ink is measured over)
  p02_dash_arcs     each dash written as one arc subpath, `M a A r r 0 0 1 b`: what a dasher that emits each dash as a
                    piece of the curve gives (the "after" of the sheet)
  p04_emul_split    femtovg's own dasher output, emulated in f32 below: every piece `M a L b` on its own
  p05_emul_joined   the same pieces, one polyline per dash (`M a L v1 L v2 ... L b`): a dasher that line_to's across
                    the flattened vertices
  p06_arcs_floor_z2 p02 with every dash shorter than a pixel at z2 drawn a pixel long about its centre, its
                    stroke-opacity scaled by its length in pixels (z2 only): what p02 leaves once the sub-fringe floor
                    is taken out

The emulation follows femtovg 06243b80: Path::dashed_with_tolerance (src/path.rs#L197) flattens in path units with
flatten_bezier (#L1016; tess_tol = TESS_TOL 0.125 at a device pixel ratio of 1, dist_tol 0.01), then calls
dash_line_segment (#L1073) once per chord, which move_to/line_to's every visible piece (#L1092-L1093). The circles'
cubics are usvg's, as the harness prints them with PATH_DUMP=1.

Two more BuseyBench files show the same split:

  g38_orig, g38_nodash, g38_arcs
                    gemini-3-8-flash.svg as it is, without its two dashed iris rings (lines 277/312: r=15 and r=14.5,
                    stroke-dasharray 2,3, stroke-width 1.5, opacity 0.8), and with each dash written as one arc subpath
  opus_orig, opus_joined
                    claude-opus-5-5.svg as it is, and with its two dashed polylines (lines 229/230, stroke-dasharray 5 4,
                    stroke-width 1.5) written out one subpath per dash, so that the dash that crosses each corner (1.39
                    units into it) keeps its miter join

Writes $CORPUS_RUN_OUT/svg/*.svg and $CORPUS_RUN_OUT/files.json (with the line reductions of this directory)."""
import json, math, os, re
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DA = os.path.dirname(os.path.dirname(HERE))
OUT = os.environ.get('CORPUS_RUN_OUT', os.path.join(os.getcwd(), 'corpus-run'))
F = np.float32
TESS, DIST = F(0.125), F(0.01)
SRC = f'{DA}/corpus/buseybench/gemini-3-7-flash.svg'


# usvg's four cubics for each circle, as the harness prints them with PATH_DUMP=1 (f32, shortest form): usvg rounds
# cx + r * kappa once from f64, so they are not the f32 sums cx + k (627.59796 for the right eye, not 627.598).
CUBICS = {
    (408, 21): ('429.0 458.0  429.0 469.598  419.598 479.0  408.0 479.0  396.402 479.0  387.0 469.598  387.0 458.0 '
                '387.0 446.402  396.402 437.0  408.0 437.0  419.598 437.0  429.0 446.402  429.0 458.0'),
    (408, 16): ('424.0 458.0  424.0 466.83655  416.83655 474.0  408.0 474.0  399.16345 474.0  392.0 466.83655  '
                '392.0 458.0  392.0 449.16345  399.16345 442.0  408.0 442.0  416.83655 442.0  424.0 449.16345  424.0 458.0'),
    (616, 21): ('637.0 458.0  637.0 469.598  627.59796 479.0  616.0 479.0  604.40204 479.0  595.0 469.598  595.0 458.0 '
                '595.0 446.402  604.40204 437.0  616.0 437.0  627.59796 437.0  637.0 446.402  637.0 458.0'),
    (616, 16): ('632.0 458.0  632.0 466.83655  624.83655 474.0  616.0 474.0  607.16345 474.0  600.0 466.83655  '
                '600.0 458.0  600.0 449.16345  607.16345 442.0  616.0 442.0  624.83655 442.0  632.0 449.16345  632.0 458.0'),
}


def circle(cx, cy, r):
    v = [F(t) for t in CUBICS[(cx, r)].split()]
    p = [(v[i], v[i + 1]) for i in range(0, len(v), 2)]
    return p[0], [tuple(p[1 + 3 * i:4 + 3 * i]) for i in range(4)]


def push(pts, q):  # push_flattened_point
    if pts:
        dx, dy = F(q[0] - pts[-1][0]), F(q[1] - pts[-1][1])
        if F(dx * dx + dy * dy) < F(DIST * DIST):
            return
    pts.append(q)


def mid(a, b):
    return (F(F(a[0] + b[0]) * F(0.5)), F(F(a[1] + b[1]) * F(0.5)))


def flat(pts, p0, p1, p2, p3, level):  # flatten_bezier
    if level > 10:
        push(pts, p3)
        return
    p01, p12, p23 = mid(p0, p1), mid(p1, p2), mid(p2, p3)
    p012, p123 = mid(p01, p12), mid(p12, p23)
    p0123 = mid(p012, p123)
    dx, dy = F(p3[0] - p0[0]), F(p3[1] - p0[1])
    d1 = abs(F(F(F(p1[0] - p3[0]) * dy) - F(F(p1[1] - p3[1]) * dx)))
    d2 = abs(F(F(F(p2[0] - p3[0]) * dy) - F(F(p2[1] - p3[1]) * dx)))
    if F(F(d1 + d2) * F(d1 + d2)) < F(TESS * F(F(dx * dx) + F(dy * dy))):
        push(pts, p3)
        return
    flat(pts, p0, p01, p012, p0123, level + 1)
    flat(pts, p0123, p123, p23, p3, level + 1)


def contour(cx, cy, r):
    start, cubics = circle(cx, cy, r)
    pts, cur = [start], start
    for c1, c2, e in cubics:
        flat(pts, cur, c1, c2, e, 0)
        cur = e
    return pts  # closed


def dash(pts, pattern, closed=True):
    """dash_line_segment over every chord: a list of dashes, each the list of pieces (a, b) femtovg emits for it."""
    rem, idx, drawing = F(pattern[0]), 0, True
    dashes, cur = [], None
    segs = list(zip(pts, pts[1:])) + ([(pts[-1], pts[0])] if closed else [])
    for s, e in segs:
        ddx, ddy = F(e[0] - s[0]), F(e[1] - s[1])
        length = F(np.sqrt(F(F(ddx * ddx) + F(ddy * ddy))))
        if length <= DIST:
            continue
        inv = F(F(1.0) / length)
        dirx, diry = F(ddx * inv), F(ddy * inv)
        t = F(0.0)
        while t < length:
            if rem <= F(np.finfo(np.float32).eps):
                idx = (idx + 1) % len(pattern)
                rem, drawing, cur = F(pattern[idx]), idx % 2 == 0, None
                continue
            step = min(rem, F(length - t))
            if drawing and step > DIST:
                a = (F(s[0] + F(dirx * t)), F(s[1] + F(diry * t)))
                b = (F(s[0] + F(dirx * F(t + step))), F(s[1] + F(diry * F(t + step))))
                if cur is None:
                    cur = []
                    dashes.append(cur)
                cur.append((a, b))
            t, rem = F(t + step), F(rem - step)
    return dashes


def fmt(v):
    return repr(float(v))


def arcs(cx, cy, r, on, off):
    C, s, d = 2 * math.pi * r, 0.0, []
    pt = lambda a: (cx + r * math.cos(a / r), cy + r * math.sin(a / r))
    while s < C - 1e-9:
        (x0, y0), (x1, y1) = pt(s), pt(min(s + on, C))
        d.append(f'M{x0:.4f} {y0:.4f} A{r} {r} 0 0 1 {x1:.4f} {y1:.4f}')
        s += on + off
    return ' '.join(d)


def arcs_floor(cx, cy, r, on, off, col, px=0.390625):
    # p02's arcs, each dash shorter than a device pixel at z2 (px pixels per unit) drawn one pixel long about its
    # centre with stroke-opacity = its length in pixels: the length analogue of femtovg's thin-stroke rule, for z2 only
    C, s, groups = 2 * math.pi * r, 0.0, {}
    pt = lambda a: (cx + r * math.cos(a / r), cy + r * math.sin(a / r))
    while s < C - 1e-9:
        e = min(s + on, C)
        a, b, o = s, e, 1.0
        if (e - s) * px < 1.0:
            m, o = (s + e) / 2, (e - s) * px
            a, b = m - 0.5 / px, m + 0.5 / px
        (x0, y0), (x1, y1) = pt(a), pt(b)
        groups.setdefault(round(o, 6), []).append(f'M{x0:.4f} {y0:.4f} A{r} {r} 0 0 1 {x1:.4f} {y1:.4f}')
        s += on + off
    return ''.join(f'<path d="{" ".join(d)}" stroke="{col}" stroke-width="1.5" fill="none"'
                   + (f' stroke-opacity="{o:g}"' if o < 1 else '') + '/>' for o, d in sorted(groups.items()))


def polyline_dashes(pts, on, off):
    """One subpath per dash along an open polyline (f64), each dash a polyline through the vertices it crosses."""
    out, s, cur, drawing, rem = [], 0.0, None, True, on
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        L, t = math.hypot(x1 - x0, y1 - y0), 0.0
        at = lambda t: (x0 + (x1 - x0) * t / L, y0 + (y1 - y0) * t / L)
        while t < L - 1e-12:
            step = min(rem, L - t)
            if drawing:
                if cur is None:
                    cur = [at(t)]
                    out.append(cur)
                cur.append(at(t + step))
            t, rem = t + step, rem - step
            if rem <= 1e-12:
                drawing, rem, cur = not drawing, (off if drawing else on), None
    return ' '.join('M' + ' L'.join(f'{x:.4f} {y:.4f}' for x, y in d) for d in out)


def others():
    """The gemini-3-8-flash and claude-opus-5-5 variants: {name: svg text}."""
    g = open(f'{DA}/corpus/buseybench/gemini-3-8-flash.svg').read()
    gpat = re.compile(r'<circle cx="(\d+)" cy="(\d+)" r="([\d.]+)" fill="none" stroke="(#[0-9a-f]+)" stroke-width="1.5" '
                      r'stroke-dasharray="(\d),(\d)" opacity="0.8"/>')
    assert len(gpat.findall(g)) == 2
    o = open(f'{DA}/corpus/buseybench/claude-opus-5-5.svg').read()
    opat = re.compile(r'<path d="M (\d+) (\d+) L (\d+) (\d+) L (\d+) (\d+)" fill="none" stroke="(#[0-9a-f]+)" '
                      r'stroke-width="1.5" stroke-dasharray="5 4" opacity="0.8"/>')
    assert len(opat.findall(o)) == 2

    def g_arcs(m):
        cx, cy, r = int(m.group(1)), int(m.group(2)), float(m.group(3))
        return (f'<path d="{arcs(cx, cy, r, int(m.group(5)), int(m.group(6)))}" fill="none" stroke="{m.group(4)}" '
                f'stroke-width="1.5" opacity="0.8"/>')

    def o_joined(m):
        v = [int(t) for t in m.groups()[:6]]
        d = polyline_dashes([(v[0], v[1]), (v[2], v[3]), (v[4], v[5])], 5.0, 4.0)
        return f'<path d="{d}" fill="none" stroke="{m.group(7)}" stroke-width="1.5" opacity="0.8"/>'

    return {'g38_orig': g, 'g38_nodash': gpat.sub('', g), 'g38_arcs': gpat.sub(g_arcs, g),
            'opus_orig': o, 'opus_joined': opat.sub(o_joined, o)}


def main():
    src = open(SRC).read()
    pat = re.compile(r'<circle cx="(\d+)" cy="(\d+)" r="(\d+)" stroke="(#[0-9a-f]+)" stroke-width="1.5" '
                     r'stroke-dasharray="(\d),(\d)" fill="none"/>')
    assert len(pat.findall(src)) == 4
    stats = []

    def emul(mode):
        def f(m):
            cx, cy, r, col, on, off = m.groups()
            pts = contour(int(cx), int(cy), int(r))
            ds = dash(pts, [F(int(on)), F(int(off))])
            if mode == 'split':
                d = ' '.join(f'M{fmt(a[0])} {fmt(a[1])} L{fmt(b[0])} {fmt(b[1])}' for dd in ds for a, b in dd)
                lens = [float(np.hypot(b[0] - a[0], b[1] - a[1])) for dd in ds for a, b in dd]
                stats.append(dict(cx=int(cx), r=int(r), dash=f'{on},{off}', chords=len(pts) - 1, dashes=len(ds),
                                  dashes_split=sum(len(dd) > 1 for dd in ds), pieces=len(lens),
                                  pieces_under_1px_z2=sum(v * 0.390625 < 1.0 for v in lens),
                                  piece_px_z2_median=round(float(np.median(lens)) * 0.390625, 3)))
            else:
                d = ' '.join(f'M{fmt(dd[0][0][0])} {fmt(dd[0][0][1])} ' +
                             ' '.join(f'L{fmt(b[0])} {fmt(b[1])}' for a, b in dd) for dd in ds)
            return f'<path d="{d}" stroke="{col}" stroke-width="1.5" fill="none"/>'
        return f

    os.makedirs(f'{OUT}/svg', exist_ok=True)
    variants = {
        'p00_orig': src,
        'p01_nodash': pat.sub('', src),
        'p02_dash_arcs': pat.sub(lambda m: f'<path d="{arcs(*(int(v) for v in m.groups()[:3]), int(m.group(5)), int(m.group(6)))}" '
                                           f'stroke="{m.group(4)}" stroke-width="1.5" fill="none"/>', src),
        'p04_emul_split': pat.sub(emul('split'), src),
        'p06_arcs_floor_z2': pat.sub(lambda m: arcs_floor(*(int(v) for v in m.groups()[:3]), int(m.group(5)), int(m.group(6)),
                                                          m.group(4)), src),
        'p05_emul_joined': pat.sub(emul('joined'), src),
        **others(),
    }
    files = []
    for name, text in variants.items():
        open(f'{OUT}/svg/{name}.svg', 'w').write(text)
        files.append({'path': f'{OUT}/svg/{name}.svg', 'key': f'portrait__{name}', 'group': 'portrait'})
    for name in sorted(n[:-4] for n in os.listdir(HERE) if n.endswith('.svg')):
        files.append({'path': f'{HERE}/{name}.svg', 'key': f'repro__{name}', 'group': 'repro'})
    json.dump(files, open(f'{OUT}/files.json', 'w'), indent=0)
    json.dump(stats, open(f'{OUT}/emul_stats.json', 'w'), indent=1)
    for s in stats:
        print(s)


if __name__ == '__main__':
    main()
