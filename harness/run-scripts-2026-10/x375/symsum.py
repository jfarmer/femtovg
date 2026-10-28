import re, sys, collections
# Sum the samples of the *shallowest* occurrence of each symbol per thread (inclusive time).
def load(fn):
    incl = collections.Counter()
    stack = []  # (indent, sym)
    in_graph = False
    for line in open(fn, errors='replace'):
        if line.startswith('Call graph:'): in_graph = True; continue
        if line.startswith('Total number in stack'): break
        if not in_graph: continue
        m = re.match(r'^([ +!:|]*?)(\d+) (.+?)(?:  \(in (.+?)\))?(?: \+ [\d,\.]+)?(?:  \[.*\])?$', line.rstrip('\n'))
        if not m: continue
        indent = len(m.group(1)); n = int(m.group(2)); sym = m.group(3).strip()
        while stack and stack[-1][0] >= indent: stack.pop()
        if not any(s == sym for _, s in stack):
            incl[sym] += n
        stack.append((indent, sym))
    return incl
a, b = load(sys.argv[1]), load(sys.argv[2])
keys = [k for k in set(a) | set(b) if re.search(sys.argv[3], k)]
keys.sort(key=lambda k: -(a[k] + b[k]))
for k in keys[:int(sys.argv[4]) if len(sys.argv) > 4 else 60]:
    print(f'{a[k]:7d} {b[k]:7d}  {k[:150]}')
