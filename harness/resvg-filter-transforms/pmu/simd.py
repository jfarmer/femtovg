#!/usr/bin/env python3
"""Per-function instruction and NEON counts of two binaries (llvm-objdump -d -C), and what differs.
NEON = an instruction with a vector operand (v<n>.<arrangement>, q/d/s/h/b register as a vector lane or ld1/st1)."""
import re, subprocess, sys, collections
VEC = re.compile(r'\bv\d+\.(?:\d+)?[bhsdq]\b|\bq\d+\b|\b(?:ld|st)[1-4]\b')
def funcs(binary):
    out = subprocess.run(['xcrun', 'llvm-objdump', '-d', '-C', '--no-show-raw-insn', '--no-leading-addr', binary],
                         capture_output=True, text=True).stdout
    f, name = collections.OrderedDict(), None
    for line in out.splitlines():
        m = re.match(r'^<(.*)>:$', line.strip()) or re.match(r'^[0-9a-f]+ <(.*)>:$', line)
        if m:
            name = re.sub(r'::h[0-9a-f]{16}$', '', m.group(1)); f.setdefault(name, [0, 0]); continue
        if name and line.startswith('\t') or (name and line.startswith(' ')):
            ins = line.strip()
            if not ins or ins.startswith(';'): continue
            f[name][0] += 1
            if VEC.search(ins): f[name][1] += 1
    return f
a, b = funcs(sys.argv[1]), funcs(sys.argv[2])
tot = lambda f, pat: [sum(v[i] for k, v in f.items() if re.search(pat, k)) for i in (0, 1)]
for pat in ['tiny_skia', 'tiny_skia::pipeline', 'resvg::filter', 'resvg::render|resvg::geom', 'usvg', '.']:
    ta, tb = tot(a, pat), tot(b, pat)
    print(f'{pat:28} instructions {ta[0]:8} -> {tb[0]:8}   NEON {ta[1]:7} -> {tb[1]:7}')
print('\nfunctions whose NEON count changed (or that vanished/appeared with NEON):')
for k in sorted(set(a) | set(b)):
    va, vb = a.get(k, [0, 0]), b.get(k, [0, 0])
    if va[1] != vb[1]:
        print(f'  {va[1]:5} -> {vb[1]:5} NEON  ({va[0]:6} -> {vb[0]:6} instr)  {k[:150]}')
