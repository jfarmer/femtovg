"""stsum.py TRACE FRAME - the frame's stencil textures and candidate page sums."""
import sys, math, collections
from tl import frames
fs = {f['n']: f for f in frames(sys.argv[1])}
f = fs[int(sys.argv[2])]
size = {}; flags = {}
# A frame's textures are allocated while its scene is recorded, which the trace logs with the frame before.
for e in fs[int(sys.argv[2]) - 1]['events']:
    if e[1] == 'alloc':
        w, h = map(int, e[3].split('x')); size[e[2]] = (w, h); flags[e[2]] = e[4]
st = [e[2] for e in f['events'] if e[1] == 'stencil']
# how each texture is rendered
kinds = collections.defaultdict(collections.Counter)
for p in f['passes']:
    kinds[p['t']][(p['k'], p['clear'], p['st'])] += 1
def pg(n): return math.ceil(n / 16384)
both = [t for t in st if any(k[2] == 0 for k in kinds[t])]          # has a stencil, also rendered without one
only = [t for t in st if not any(k[2] == 0 for k in kinds[t])]
print(f"stencils {len(st)}: {len(only)} on textures always rendered with it, {len(both)} on textures also rendered without it")
for name, group in (('always with', only), ('also without', both), ('all', st)):
    px = [size[t][0] * size[t][1] for t in group if t in size]
    print(f"  {name:13s} n={len(px):3d}  stencil pages {sum(pg(p) for p in px):5d}  color pages {sum(pg(4*p) for p in px):5d}  color+stencil {sum(pg(4*p)+pg(p) for p in px):5d}  missing={len(group)-len(px)}")
if len(sys.argv) > 3:
    for t in both:
        print('   ', t, size.get(t), flags.get(t), dict(kinds[t]))
