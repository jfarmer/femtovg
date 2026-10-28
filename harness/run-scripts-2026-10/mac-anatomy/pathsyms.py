import re, subprocess, sys
def syms(b):
    out = subprocess.run(['otool', '-l', b], capture_output=True, text=True).stdout
    m = re.search(r'sectname __text\n\s+segname __TEXT\n\s+addr (0x[0-9a-f]+)\n\s+size (0x[0-9a-f]+)', out)
    lo, hi = int(m.group(1), 16), int(m.group(1), 16) + int(m.group(2), 16)
    s = []
    for line in subprocess.run(['nm', '-n', b], capture_output=True, text=True).stdout.splitlines():
        p = line.split()
        if len(p) == 3 and p[1] in 'tT' and lo <= int(p[0], 16) < hi:
            s.append((int(p[0], 16), p[2]))
    s.sort()
    d = {}
    for (a, n), (a2, _) in zip(s, s[1:] + [(hi, '')]):
        dn = subprocess.run(['swift', 'demangle', '--compact'], input=n[1:], capture_output=True, text=True).stdout.strip() if False else n
        d[n] = (a, a2 - a)
    return d
pat = sys.argv[1]
for b in sys.argv[2:]:
    d = syms(b)
    tot = 0
    print('==', b.split('/')[-1])
    for n, (a, sz) in sorted(d.items(), key=lambda kv: kv[1][0]):
        if re.search(pat, n):
            tot += sz
            print(f'  {sz:6d} {hex(a)} {re.sub(r"17h[0-9a-f]{16}E$", "", n)[:110]}')
    print('  total', tot)
