#!/usr/bin/env python3
"""Per-symbol sizes from a dSYM's symbol table (address deltas within __text),
summed per crate prefix, and the femtovg path-cache functions listed.
usage: symsize.py <dwarf-binary> [<dwarf-binary> ...]"""
import subprocess, sys, re, collections
def syms(path):
    out = subprocess.run(["nm", "-n", "--defined-only", path], capture_output=True, text=True).stdout
    rows = []
    for line in out.splitlines():
        p = line.split(None, 2)
        if len(p) == 3 and p[1] in "tT":
            rows.append((int(p[0], 16), p[2]))
    sizes = {}
    for (a, n), (b, _) in zip(rows, rows[1:]):
        sizes[n] = sizes.get(n, 0) + (b - a)
    return sizes
def crate_of(n):
    # legacy Rust mangling: _ZN<len><ident>...; the first identifier is the crate
    # (or a "<impl ...>" segment such as _$LT$femtovg..x$u20$as$u20$...).
    m = re.search(r"_ZN(\d+)", n)
    if not m:
        return "other"
    k = int(m.group(1)); ident = n[m.end():m.end() + k]
    if ident.startswith("_$LT$"):
        inner = re.match(r"_\$LT\$([a-z_0-9]+)\.\.", ident)
        return inner.group(1) if inner else "impl"
    return ident
def dem(names):
    out = subprocess.run(["xcrun", "swift-demangle", "--simplified"], input="\n".join(names), capture_output=True, text=True).stdout
    return out.splitlines()
res = {}
for path in sys.argv[1:]:
    s = syms(path)
    crate = collections.Counter()
    for n, z in s.items():
        c = crate_of(n)
        crate[c] += z
    res[path] = (s, crate)
for path, (s, crate) in res.items():
    print(path.split("/")[-1], "total __text from symbols", sum(s.values()))
    print("   femtovg", crate["femtovg"], " wgpu*", sum(v for k, v in crate.items() if k.startswith("wgpu")), " naga", crate["naga"], " usvg", crate["usvg"])
    for n, z in sorted(s.items(), key=lambda x: -x[1]):
        if "femtovg" in n and ("cache" in n.lower() or "tesselate" in n or "flatten" in n):
            print("   ", z, n[:140])
