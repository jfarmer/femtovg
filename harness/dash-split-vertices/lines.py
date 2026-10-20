#!/usr/bin/env python3
"""The straight-line reductions, written into this directory. 200 x 200 user units, so the harness's 1x framing
(z1: the 200 px box) draws one unit to one device pixel and the femtovg Canvas snippet in the issue needs no transform.
White strokes 1 px wide on black, butt caps; 20 rows, their start shifted by 1/16 px in y and 3/16 px in x per row
so that dash ends land at every phase.

  line-plain.svg         M x0 y L x1 y, stroke-dasharray 2 2
  line-points.svg        the same line with a collinear point every 0.5 px, stroke-dasharray 2 2
  line-points-1px.svg    the same with a point every 1 px (pieces as long as the fringe), stroke-dasharray 2 2
  line-split.svg         no dash array: femtovg's own output for line-points.svg written out, every piece M a L b
                         (the emulation of portrait.py)
  line-joined.svg        no dash array: one polyline per dash through the inner points (a dasher that line_to's
                         across vertices)
  line-segments.svg      no dash array: one M a L b per dash (a dasher that emits each dash as a piece of the
                         original segment) - the "after"
  line-points-03.svg, line-joined-03.svg
                         the same with a collinear point every 0.3 px, where a dash's first and last chords are often
                         shorter than half the fringe (one segment per dash is line-segments.svg again)
  endchord-plain.svg     isolated 2 px segments, no dash array
  endchord-short.svg     the same with a collinear point END_CHORDS[i] px before each segment's end: the last chord
                         alone is shorter than half the fringe
  pieces.svg             isolated butt-capped segments, no dash array: row i holds 16 segments of PIECES[i] px
  pieces-scaled.svg      the same, each segment shorter than 1 px drawn 1 px long about its centre with its opacity
                         scaled by its length: the length analogue of the rule femtovg applies to a stroke thinner
                         than the fringe (src/lib.rs#L1623)
  repro.svg              the issue's repro, two lines as written there: M20 28 L180 28, and the same line at y 36 with
                         a collinear point every 0.5 px, both 1 px wide, stroke-dasharray 2 2
  corner.svg             a 16-unit stroke, stroke-dasharray 100 20, whose first dash crosses a 90 degree corner
                         20 units before it ends
  corner-split.svg       no dash array: femtovg's dasher output for corner.svg written out, M a L b per piece
  corner-joined.svg      no dash array: one subpath per dash, the first through the corner (its miter join kept)"""
import os
import numpy as np
from portrait import dash, F

HERE = os.path.dirname(os.path.abspath(__file__))
ROWS = [(20 + 3 * i / 16, 20 + 8 + 8 * i + i / 16) for i in range(20)]  # (x0, y)
LEN = 160.0
PATTERN = (2.0, 2.0)
END_CHORDS = [0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0, 1.5] * 2
PIECES = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.25, 1.5, 2.0, 3.0, 4.0, 0.25, 0.75, 0.5, 1.0]
HEAD = ('<svg viewBox="0 0 200 200" width="200" height="200" xmlns="http://www.w3.org/2000/svg">\n'
        '<rect width="200" height="200" fill="#000"/>\n')
ST = 'stroke="#fff" stroke-width="1" fill="none"'


def f(v):
    return repr(float(v)) if isinstance(v, np.floating) else f'{v:.6f}'.rstrip('0').rstrip('.')


def write(name, body):
    open(f'{HERE}/{name}.svg', 'w').write(HEAD + body + '</svg>\n')


def points(x0, step):
    xs = [x0 + step * k for k in range(int(LEN / step + 1e-9) + 1)]
    return xs if abs(xs[-1] - (x0 + LEN)) < 1e-9 else xs + [x0 + LEN]


def poly(xs, y):
    return f'M{f(xs[0])} {f(y)} ' + ' '.join(f'L{f(x)} {f(y)}' for x in xs[1:])


def emulated(x0, y, step):
    # The f32 values usvg reads from line-points.svg, dashed as femtovg dashes them.
    xs = [F(float(f(x))) for x in points(x0, step)]
    return dash([(x, F(float(f(y)))) for x in xs], [F(PATTERN[0]), F(PATTERN[1])], closed=False)


def main():
    da = ' stroke-dasharray="2 2"'
    write('line-plain', ''.join(f'<path d="M{f(x0)} {f(y)} L{f(x0 + LEN)} {f(y)}" {ST}{da}/>\n' for x0, y in ROWS))
    write('line-points', ''.join(f'<path d="{poly(points(x0, 0.5), y)}" {ST}{da}/>\n' for x0, y in ROWS))
    write('line-points-1px', ''.join(f'<path d="{poly(points(x0, 1.0), y)}" {ST}{da}/>\n' for x0, y in ROWS))
    split, joined, segs = '', '', ''
    for x0, y in ROWS:
        ds = emulated(x0, y, 0.5)
        split += '<path d="' + ' '.join(f'M{f(a[0])} {f(a[1])} L{f(b[0])} {f(b[1])}' for d in ds for a, b in d) + f'" {ST}/>\n'
        joined += '<path d="' + ' '.join(f'M{f(d[0][0][0])} {f(d[0][0][1])} ' + ' '.join(f'L{f(b[0])} {f(b[1])}' for a, b in d)
                                         for d in ds) + f'" {ST}/>\n'
        segs += '<path d="' + ' '.join(f'M{f(d[0][0][0])} {f(d[0][0][1])} L{f(d[-1][1][0])} {f(d[-1][1][1])}' for d in ds) + f'" {ST}/>\n'
    write('line-split', split)
    write('line-joined', joined)
    write('line-segments', segs)
    # vertices every 0.3 px: dash ends fall between them, so a dash's first and last chords are often shorter than
    # half the fringe
    write('line-points-03', ''.join(f'<path d="{poly(points(x0, 0.3), y)}" {ST}{da}/>\n' for x0, y in ROWS))
    joined, segs = '', ''
    for x0, y in ROWS:
        ds = emulated(x0, y, 0.3)
        joined += '<path d="' + ' '.join(f'M{f(d[0][0][0])} {f(d[0][0][1])} ' + ' '.join(f'L{f(b[0])} {f(b[1])}' for a, b in d)
                                         for d in ds) + f'" {ST}/>\n'
        segs += '<path d="' + ' '.join(f'M{f(d[0][0][0])} {f(d[0][0][1])} L{f(d[-1][1][0])} {f(d[-1][1][1])}' for d in ds) + f'" {ST}/>\n'
    write('line-joined-03', joined)
    assert segs == open(f'{HERE}/line-segments.svg').read()[len(HEAD):-len('</svg>\n')], 'one segment per dash differs'
    body, scaled = '', ''
    for (x0, y), L in zip(ROWS, PIECES):
        starts = [x0 + 10 * k + k / 8 for k in range(16)]
        body += '<path d="' + ' '.join(f'M{f(a)} {f(y)} L{f(a + L)} {f(y)}' for a in starts) + f'" {ST}/>\n'
        if L < 1:
            c = [a + L / 2 for a in starts]
            scaled += ('<path d="' + ' '.join(f'M{f(m - 0.5)} {f(y)} L{f(m + 0.5)} {f(y)}' for m in c) +
                       f'" {ST} stroke-opacity="{f(L)}"/>\n')
        else:
            scaled += '<path d="' + ' '.join(f'M{f(a)} {f(y)} L{f(a + L)} {f(y)}' for a in starts) + f'" {ST}/>\n'
    write('pieces', body)
    write('pieces-scaled', scaled)
    # 2 px segments, no dash array; endchord-short.svg adds a collinear point END_CHORDS[i] px before each end
    plain, short = '', ''
    for (x0, y), e in zip(ROWS, END_CHORDS):
        starts = [x0 + 10 * k + k / 8 for k in range(16)]
        plain += '<path d="' + ' '.join(f'M{f(a)} {f(y)} L{f(a + 2)} {f(y)}' for a in starts) + f'" {ST}/>\n'
        short += '<path d="' + ' '.join(f'M{f(a)} {f(y)} L{f(a + 2 - e)} {f(y)} L{f(a + 2)} {f(y)}' for a in starts) + f'" {ST}/>\n'
    write('endchord-plain', plain)
    write('endchord-short', short)
    # the issue's repro, as written there (black is the rect's default fill)
    open(f'{HERE}/repro.svg', 'w').write(
        '<svg viewBox="0 0 200 200" width="200" height="200" xmlns="http://www.w3.org/2000/svg">\n'
        '  <rect width="200" height="200"/>\n'
        f'  <path d="M20 28 L180 28" {ST.replace(' fill="none"', '')} stroke-dasharray="2 2" fill="none"/>\n'
        f'  <path d="{poly(points(20.0, 0.5), 36)}" {ST.replace(' fill="none"', '')} stroke-dasharray="2 2" fill="none"/>\n'
        '</svg>\n')
    # a dash across a corner: dash 100 20 over 80 + 100 units. femtovg: M40 60 L120 60, M120 60 L120 80, M120 100 L120 160
    wide = 'stroke="#fff" stroke-width="16" fill="none"'
    write('corner', f'<path d="M40 60 L120 60 L120 160" {wide} stroke-dasharray="100 20"/>\n')
    write('corner-split', f'<path d="M40 60 L120 60 M120 60 L120 80 M120 100 L120 160" {wide}/>\n')
    write('corner-joined', f'<path d="M40 60 L120 60 L120 80 M120 100 L120 160" {wide}/>\n')


if __name__ == '__main__':
    main()
