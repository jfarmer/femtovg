"""pages.py TRACE FRAME - candidate page sums (16 KiB pages) to compare with the frame's measured page faults."""
import sys, math, collections
from tl import frames
f = {f['n']: f for f in frames(sys.argv[1])}[int(sys.argv[2])]
PAGE = 16384
def pages(p, bpp):
    w, h = map(int, p['size'].split('x'))
    return math.ceil(w * h * bpp / PAGE)
had_stencil = set(); was_filter = set(); was_loaded = set()
sums = collections.Counter(); counts = collections.Counter()
last_kind = {}
for p in f['passes']:
    t = p['t']
    if p['k'] == 2:  # filter target
        counts['filter passes'] += 1; sums['filter passes: color'] += pages(p, 4)
        if p['st']:
            sums['filter passes with a stencil: color'] += pages(p, 4); sums['filter passes with a stencil: stencil'] += pages(p, 1)
        if t in had_stencil:
            counts['filter pass on a texture that was a capture'] += 1
            sums['filter pass on a texture that was a capture: color'] += pages(p, 4)
            sums['filter pass on a texture that was a capture: stencil'] += pages(p, 1)
        if last_kind.get(t) == 1:
            counts['filter pass on a texture last rendered as a capture'] += 1
            sums['filter pass on a texture last rendered as a capture: color'] += pages(p, 4)
        was_filter.add(t)
    elif p['k'] == 1:
        counts['image passes'] += 1
        if t in was_filter:
            counts['capture pass on a texture that was a filter target'] += 1
            sums['capture pass on a texture that was a filter target: color'] += pages(p, 4)
            sums['capture pass on a texture that was a filter target: stencil'] += pages(p, 1)
        if last_kind.get(t) == 2:
            counts['capture pass on a texture last rendered as a filter target'] += 1
            sums['capture pass on a texture last rendered as a filter target: color'] += pages(p, 4)
            sums['capture pass on a texture last rendered as a filter target: stencil'] += pages(p, 1)
        had_stencil.add(t)
    last_kind[t] = p['k']
print(f"frame {f['n']}: measured faults {f['faults']}")
for k in sorted(sums): print(f"  {sums[k]:6d} pages  {k}")
for k in sorted(counts): print(f"  {counts[k]:6d} x      {k}")
