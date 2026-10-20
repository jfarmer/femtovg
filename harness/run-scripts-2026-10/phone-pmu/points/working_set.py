#!/usr/bin/env python3
"""Working-set estimate per frame and per path from the anatomy probe counts
(probe.tsv): Point 32 B, Contour 80 B, Vertex 16 B (sizes printed by the probe)."""
import collections
rows = {}
for line in open("probe.tsv"):
    n, fr, z, tol, p = line.rstrip("\n").split("\t")
    d = {k: int(v) for k, v in (kv.split("=") for kv in p.split()[1:])}
    rows[(n, fr, z, tol)] = d
KB = 1024
print("| file | framing | tol | points | path-cache bytes (points+contours) | largest path: points / bytes | vertices (frame) | vertex bytes | verts per point | frame total |")
print("|---|---|---|---|---|---|---|---|---|---|")
for (n, fr, z, tol), d in sorted(rows.items()):
    if not ((fr == "hd" and z == "1") or (fr == "small" and z == "1")):
        continue
    if not (n in ("c_tiger", "c_mr-settodefault", "c_puzzle-fox", "c_svg395_40", "c_duckduckgo") or n.startswith("b_gpt-5-6-sol")):
        continue
    pc = d["points"] * d["size_point"] + d["contours"] * d["size_contour"]
    vb = d["flush_verts"] * d["size_vertex"]
    vpp = d["flush_verts"] / max(1, d["points"])
    big = d["max_cache_points"] * d["size_point"]
    print(f"| {n} | {fr}{z} | {tol} | {d['points']} | {pc/KB:.0f} KiB | {d['max_cache_points']} / {big/KB:.0f} KiB (+~{d['max_cache_points']*vpp*16/KB:.0f} KiB verts) | {d['flush_verts']} | {vb/KB:.0f} KiB | {vpp:.1f} | {(pc+vb)/KB:.0f} KiB |")
