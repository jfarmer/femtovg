#!/usr/bin/env python3
"""Synthetic still scenes of thin rects whose mask keys are controlled.

At fit 1 (200x200 viewBox) and zoom 1, device = (130 + u, 30 + v): a rect's
fractional offset is its subpixel phase, the integer part only moves its mask.
Each rect is 2.5 x 0.375 px (convex, mean width 0.326 < 1: thin), one per
4 x 2 cell, its own path and fill.

  distinct N   N rects, each with a distinct phase (x frac k/256, y frac m/256)
  dupafter U D U distinct rects, then D copies of rect 0's phase
  dupfirst U D rect 0, its D copies, then the other U-1 distinct rects
"""
import sys

COLS, ROWS = 50, 100


def cell(i):
    return 4 * (i % COLS), 2 * (i // COLS)


def phase(n):
    return (n % 256) / 256.0, (n // 256) / 256.0


def rect(i, n):
    x, y = cell(i)
    fx, fy = phase(n)
    return f'<rect x="{x + fx:.8f}" y="{y + fy:.8f}" width="2.5" height="0.375" fill="#000"/>'


def svg(phases):
    assert len(phases) <= COLS * ROWS
    body = '\n'.join(rect(i, n) for i, n in enumerate(phases))
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200">\n'
            '<rect width="200" height="200" fill="#fff"/>\n' + body + '\n</svg>\n')


def main():
    kind = sys.argv[1]
    if kind == 'distinct':
        phases = list(range(int(sys.argv[2])))
    elif kind == 'dupafter':
        u, d = int(sys.argv[2]), int(sys.argv[3])
        phases = list(range(u)) + [0] * d
    elif kind == 'dupfirst':
        u, d = int(sys.argv[2]), int(sys.argv[3])
        phases = [0] * (d + 1) + list(range(1, u))
    else:
        raise SystemExit(kind)
    sys.stdout.write(svg(phases))


main()
