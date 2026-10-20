"""cmp.py TRACE_A TRACE_B [frames...] - two traces with the same pass sequence: per pass, how much the GPU timeline
advances (the running maximum of pass end times), averaged over the frames, and where A advances more than B."""
import sys, collections, statistics
from tl import frames, label
def adv(path, want):
    out = None; n = 0; ref = None
    for f in frames(path):
        if f['n'] not in want or not f['passes']: continue
        ps = f['passes']; ref = ps
        start = min(p['t0'] for p in ps if p['t0']); run = start; d = []
        for p in ps:
            e = p['t1'] if p['t1'] else run
            d.append(max(0, e - run)); run = max(run, e)
        out = d if out is None else [a + b for a, b in zip(out, d)]; n += 1
    return [x / n for x in out], ref
want = [int(a) for a in sys.argv[3:]] or [3, 4, 5, 6]
a, pa = adv(sys.argv[1], want); b, pb = adv(sys.argv[2], want)
assert len(a) == len(b), (len(a), len(b))
print(f"timeline: A {sum(a)/1e6:.2f} ms, B {sum(b)/1e6:.2f} ms, A-B {(sum(a)-sum(b))/1e6:.2f} ms over {len(a)} passes")
# what each pass's target was last used for
def history(ps):
    last = {}; out = []
    for p in ps:
        prev = last.get(p['t'])
        out.append(prev)
        last[p['t']] = 'target-st' if p['st'] else 'target'
        for r in p['r']:
            last[r] = last.get(r, '') and last[r]
    return out
ha = history(pa)
by = collections.defaultdict(lambda: [0.0, 0.0, 0])
for i, (x, y) in enumerate(zip(a, b)):
    p = pa[i]
    k = (label(p), f"prev={ha[i]}")
    by[k][0] += x; by[k][1] += y; by[k][2] += 1
print("by pass kind in A and what A's target texture was last rendered as:")
for k, (x, y, n) in sorted(by.items(), key=lambda kv: -(kv[1][0] - kv[1][1])):
    print(f"  A {x/1e6:6.2f} ms  B {y/1e6:6.2f} ms  diff {(x-y)/1e6:6.2f} ms  n={n:4d}  ({(x-y)/n/1e3:6.1f} us each)  {k}")
