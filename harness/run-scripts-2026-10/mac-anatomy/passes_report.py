#!/usr/bin/env python3
"""Per-pass instructions per frame and per point from passes.jsonl (median over repeats), and the slope between
tolerances: instructions per extra point, per pass."""
import collections, json, statistics as st, sys
rows = [json.loads(l) for l in open('passes.jsonl')]
probe = {(r['file'], r['framing'], r['tol']): r for r in map(json.loads, open('probe.jsonl'))}
NAMES = ["new_flatten", "new_contour_pass", "new_collinear", "fill_holes", "fill_orient", "fill_joins", "fill_reserve",
         "fill_fan", "fill_tris", "fill_fringe", "fill_restore", "stroke_joins", "stroke_expand", "canvas_fill_total",
         "canvas_fill_cache", "canvas_fill_clip", "canvas_fill_expand", "canvas_fill_copy", "canvas_stroke_total",
         "canvas_stroke_cache", "canvas_stroke_expand", "canvas_stroke_copy", "flush_render", "write_buffer", "flush_total"]
agg = collections.defaultdict(lambda: collections.defaultdict(list))
for r in rows:
    if 'new_flatten' not in r:
        continue
    k = (r['file'], r['framing'], r['tol'])
    for n in NAMES:
        c, i, cy = r[n]
        agg[k][n + '.i'].append(i / r['frames'])
        agg[k][n + '.c'].append(cy / r['frames'])
med = {k: {n: st.median(v) for n, v in d.items()} for k, d in agg.items()}
json.dump({'/'.join(k): v for k, v in med.items()}, open('passes_median.json', 'w'), indent=1)
files = sorted({k[0] for k in med}, key=lambda f: ['tiger', 'puzzle-fox', 'mr-settodefault', 'svgenius-icon32', 'svgenius-icon5'].index(f))
for f in files:
    for fr in ('hd', 'z1'):
        if (f, fr, '0.25') not in med:
            continue
        m, a = med[(f, fr, '0.25')], med.get((f, fr, '0.0625'))
        pm = probe[(f, fr, '0.25')]['probe_points'] / 3
        pa = probe[(f, fr, '0.0625')]['probe_points'] / 3
        n_rep = len(agg[(f, fr, '0.25')]['new_flatten.i'])
        print(f'== {f} {fr}: points {pm:.0f} (A {pa:.0f}), {n_rep} repeats; columns: master instr/frame, per point, cycles/frame (E-core), A instr/frame, extra instr per extra point')
        for n in NAMES:
            mi, ai = m[n + '.i'], (a[n + '.i'] if a else float('nan'))
            print(f'  {n:22s} {mi / 1e3:9.1f} k {mi / pm:7.1f}/pt {m[n + ".c"] / 1e3:9.1f} kcyc | A {ai / 1e3:9.1f} k  slope {(ai - mi) / (pa - pm) if pa > pm else float("nan"):7.1f}/pt')
