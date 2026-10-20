"""sample_share.py SAMPLE.txt  - from a /usr/bin/sample call graph: samples under Canvas::flush_to_output and,
of those, the ones in the pipeline map (hashbrown rustc_entry, hash_one, DefaultHasher::write) and in the other
callees of update_renderpass."""
import re, sys, collections
lines = open(sys.argv[1]).read().split('\n')
start = next(i for i, l in enumerate(lines) if l.startswith('Call graph:'))
row = re.compile(r'^([ +!:|]*?)(\d+) (.*)$')
nodes = []  # (depth, count, name)
for l in lines[start + 1:]:
    if not l.strip() or l.startswith('Total number'):
        break
    m = row.match(l)
    if not m:
        continue
    depth = len(m.group(1))
    name = m.group(3).split('  (in ')[0]
    name = re.sub(r'::h[0-9a-f]{16}$', '', name)
    name = name.replace('$LT$', '<').replace('$GT$', '>').replace('$u20$', ' ').replace('$C$', ',').replace('..', '::').replace('_<', '<')
    nodes.append((depth, int(m.group(2)), name))
# inclusive samples of every node; children = following nodes with greater depth
def subtree(i):
    d = nodes[i][0]; j = i + 1
    while j < len(nodes) and nodes[j][0] > d:
        j += 1
    return j
def first(pred, lo=0, hi=None):
    for i in range(lo, hi if hi is not None else len(nodes)):
        if pred(nodes[i][2]):
            return i
main_total = nodes[0][1]
f = first(lambda n: 'flush_to_output' in n)
fe = subtree(f); flush = nodes[f][1]
def topmost(pred, lo, hi):
    """Sum of inclusive counts of the topmost nodes matching pred in [lo, hi)."""
    total, i = 0, lo
    while i < hi:
        if pred(nodes[i][2]):
            total += nodes[i][1]; i = subtree(i)
        else:
            i += 1
    return total
is_hash = lambda n: 'rustc_entry' in n or 'hash_one' in n or 'DefaultHasher' in n
hashing = topmost(is_hash, f + 1, fe)
upd = topmost(lambda n: 'update_renderpass' in n, f + 1, fe)
print(f"main thread samples {main_total}; under Canvas::flush_to_output {flush}")
print(f"  in the pipeline map (rustc_entry + hash_one + DefaultHasher::write): {hashing} = {100 * hashing / flush:.1f} % of flush_to_output")
print(f"  update_renderpass inclusive: {upd} = {100 * upd / flush:.1f} %")
# self/leaf breakdown by symbol under flush_to_output: exclusive = count - sum(direct children)
excl = collections.Counter()
for i in range(f, fe):
    d, c, n = nodes[i]
    j = i + 1; kids = 0
    while j < fe and nodes[j][0] > d:
        if all(nodes[k][0] != nodes[j][0] or k == j for k in range(i + 1, j)) or True:
            pass
        j += 1
    # direct children: nodes after i with the smallest depth greater than d, until depth <= d
    j = i + 1; child_depth = None
    while j < fe and nodes[j][0] > d:
        if child_depth is None or nodes[j][0] < child_depth:
            child_depth = nodes[j][0]
        j += 1
    kids = sum(nodes[k][1] for k in range(i + 1, j) if nodes[k][0] == child_depth) if child_depth is not None else 0
    excl[n] += c - kids
if len(sys.argv) > 2:
    for n, c in excl.most_common(int(sys.argv[2])):
        print(f"  {c:6d} {100 * c / flush:5.1f} %  {n[:150]}")
