"""sample_tree.py SAMPLE.txt ROOT_SUBSTR DEPTH [MIN]  - callee tree under the first frame matching ROOT_SUBSTR,
merging the per-call-site rows of one callee, to DEPTH levels, rows of at least MIN samples."""
import re, sys, collections
lines = open(sys.argv[1]).read().split('\n')
start = next(i for i, l in enumerate(lines) if l.startswith('Call graph:'))
row = re.compile(r'^([ +!:|]*?)(\d+) (.*)$')
nodes = []
for l in lines[start + 1:]:
    if not l.strip() or l.startswith('Total number'):
        break
    m = row.match(l)
    if not m:
        continue
    name = m.group(3).split('  (in ')[0]
    name = re.sub(r'::h[0-9a-f]{16}$', '', name)
    for a, b in (('$LT$', '<'), ('$GT$', '>'), ('$u20$', ' '), ('$C$', ','), ('..', '::'), ('_<', '<'), ('$u7b$', '{'), ('$u7d$', '}')):
        name = name.replace(a, b)
    nodes.append((len(m.group(1)), int(m.group(2)), name))
def end(i):
    d = nodes[i][0]; j = i + 1
    while j < len(nodes) and nodes[j][0] > d:
        j += 1
    return j
def children(i):
    j, e, out = i + 1, end(i), []
    while j < e:
        out.append(j); j = end(j)
    return out
root = next(i for i, n in enumerate(nodes) if sys.argv[2] in n[2])
maxd, minc = int(sys.argv[3]), int(sys.argv[4]) if len(sys.argv) > 4 else 5
def show(idxs, depth, total):
    # merge rows of the same callee among these sibling groups
    merged = collections.OrderedDict()
    for i in idxs:
        merged.setdefault(nodes[i][2], []).append(i)
    rows = sorted(merged.items(), key=lambda kv: -sum(nodes[i][1] for i in kv[1]))
    for name, group in rows:
        c = sum(nodes[i][1] for i in group)
        if c < minc:
            continue
        kids = [k for i in group for k in children(i)]
        self_ = c - sum(nodes[k][1] for k in kids)
        print(f"{'  ' * depth}{c:5d} {100 * c / total:5.1f} %  (self {self_:4d})  {name[:130]}")
        if depth < maxd:
            show(kids, depth + 1, total)
total = nodes[root][1]
print(f"{total} samples under {nodes[root][2][:100]}")
show(children(root), 1, total)
