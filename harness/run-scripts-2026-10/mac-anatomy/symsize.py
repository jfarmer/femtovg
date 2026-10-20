#!/usr/bin/env python3
"""symsize.py BIN... : __TEXT/__text bytes per crate, from symbol address gaps (nm -n), plus segment sizes."""
import collections, re, subprocess, sys
def crate(sym):
    s = sym
    if s.startswith('__ZN'):
        m = re.match(r'__ZN(\d+)', s)
        if m:
            n = int(m.group(1)); name = s[len(m.group(0)):len(m.group(0)) + n]
            return name.replace('$LT$', '<').lstrip('_<')
    if s.startswith('__R'):
        return 'rust-v0'
    if s.startswith('__Z'):
        return 'c++'
    return 'other'
def text_range(b):
    out = subprocess.run(['otool', '-l', b], capture_output=True, text=True).stdout
    m = re.search(r'sectname __text\n\s+segname __TEXT\n\s+addr (0x[0-9a-f]+)\n\s+size (0x[0-9a-f]+)', out)
    a, s = int(m.group(1), 16), int(m.group(2), 16)
    return a, a + s
for b in sys.argv[1:]:
    lo, hi = text_range(b)
    syms = []
    for line in subprocess.run(['nm', '-n', b], capture_output=True, text=True).stdout.splitlines():
        parts = line.split()
        if len(parts) == 3 and parts[1] in 'tT':
            a = int(parts[0], 16)
            if lo <= a < hi:
                syms.append((a, parts[2]))
    syms.sort()
    per = collections.Counter(); femto = collections.Counter()
    for (a, s), (a2, _) in zip(syms, syms[1:] + [(hi, '')]):
        size = a2 - a
        c = crate(s)
        per[c] += size
        if c == 'femtovg':
            m = re.match(r'__ZN\d+femtovg((?:\d+[A-Za-z_$][\w$.]*?)+?)17h[0-9a-f]{16}E', s)
            parts = re.findall(r'(\d+)', s[11:])
            # module path: femtovg::<mod>
            rest = s[len('__ZN7femtovg'):]
            mm = re.match(r'(\d+)', rest)
            mod = rest[len(mm.group(1)):len(mm.group(1)) + int(mm.group(1))] if mm else '?'
            femto[mod] += size
    seg = subprocess.run(['size', '-m', b], capture_output=True, text=True).stdout
    text = int(re.search(r'Segment __TEXT: (\d+)', seg).group(1)); textsec = int(re.search(r'Section __text: (\d+)', seg).group(1))
    import os
    print(f'== {b.split("/")[-1]}: file {os.path.getsize(b)} __TEXT {text} __text {textsec}')
    for c, n in per.most_common(14):
        print(f'   {c:28s} {n:9d}')
    print('   femtovg modules:', ', '.join(f'{k} {v}' for k, v in femto.most_common(12)))
