#!/usr/bin/env python3
"""counts.py: points per round cap on master 06243b80 and with the prototype, by device width (antialiased, fringe
1 px, tess_tol 0.125), the half-coverage outline's deepest cut inside the arc on master (r (1 - cos(pi / 2 n)) for
n = ncap - 1 chords), and the widest turn a master round join draws with two points (one chord, the bevel's). Then the
cut swept over every width from 1 px to 100 px (steps of 0.0001 px), with its smallest and largest values."""
import math
TOL, F = 0.125, 1.0


def cd(radius, arc, tol):
    return max(2, math.ceil(arc / (2 * math.acos(radius / (radius + tol)))))


print('width px | master points  cut px  share of the half disc | prototype points | widest two-point join turn')
for w in (1, 1.2, 1.6, 2, 2.64, 3, 3.2, 4, 5, 6, 8, 16, 26):
    r = max(w, F) / 2
    m = cd(r, math.pi, TOL); n = m - 1
    cut = r * (1 - math.cos(math.pi / (2 * n)))
    share = (n / 2) * math.sin(math.pi / n) / (math.pi / 2)
    p = cd(r + F / 2, math.pi, TOL / 2) + 1
    turn = 180 * 2 / m  # n = ceil(turn / pi * ncap) <= 2
    print(f'{w:8} | {m:6d} {cut:12.3f} {share:12.2f} | {p:8d} | {turn:5.0f} deg')
# The width below which master's caps have 3 points, and 4.
for k in (3, 4, 5):
    lo, hi = 0.5, 20.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if cd(mid, math.pi, TOL) <= k: lo = mid
        else: hi = mid
    print(f'master caps have at most {k} points up to a width of {2 * lo:.2f} px')
# The cut over every width from 1 px up: largest just below a width where a point comes in, smallest just above it.
cuts = []
for i in range(10000, 1000001):
    w = i / 10000; r = w / 2; n = cd(r, math.pi, TOL) - 1
    cuts.append((r * (1 - math.cos(math.pi / (2 * n))), w))
lo, hi = min(cuts), max(cuts)
print(f'widths 1-100 px: the cut runs from {lo[0]:.3f} px (at {lo[1]:.4f} px) to {hi[0]:.3f} px (at {hi[1]:.4f} px), '
      f'{lo[0] / TOL:.2f}-{hi[0] / TOL:.2f} times tess_tol')
