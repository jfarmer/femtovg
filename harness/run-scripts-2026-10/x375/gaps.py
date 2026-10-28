"""gaps.py TRACE FRAME - where the GPU timeline's idle gaps fall: for the passes in start order, the gap before each
(its start minus the latest end so far), grouped by what kind of pass follows the gap."""
import sys, collections
from tl import frames, label
fs = {f['n']: f for f in frames(sys.argv[1])}
f = fs[int(sys.argv[2])]
ps = [p for p in f['passes'] if p['t0'] and p['t1']]
first_use = {}
roles = collections.defaultdict(set)
for p in f['passes']:
    first_use.setdefault(p['t'], p['i'])
order = sorted(ps, key=lambda p: p['t0'])
end = order[0]['t0']; rows = []
for p in order:
    gap = max(0, p['t0'] - end)
    rows.append((gap, p))
    end = max(end, p['t1'])
tot = sum(g for g, _ in rows)
print(f"frame {f['n']}: {len(ps)} timed passes, idle total {tot/1e6:.2f} ms")
by = collections.defaultdict(lambda: [0, 0])
for g, p in rows:
    k = (label(p), 'clear' if p['clear'] else 'load', 'st' if p['st'] else 'nost')
    by[k][0] += g; by[k][1] += 1
for k, (g, n) in sorted(by.items(), key=lambda kv: -kv[1][0]):
    print(f"  {g/1e6:7.2f} ms over {n:4d} passes ({g/n/1e3:6.1f} us each)  {k}")
print('largest gaps:')
for g, p in sorted(rows, key=lambda r: -r[0])[:int(sys.argv[3]) if len(sys.argv) > 3 else 25]:
    print(f"  {g/1e3:7.1f} us before P{p['i']:<4d} {label(p):12s} t={p['t']:>8s} {p['size']:>8s} clear={p['clear']} st={p['st']} d={p['d']} r={','.join(p['r'])}")
