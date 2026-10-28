# Layer-alignment patch: E-core counters, codegen, fuzz (2026-10-24)

## Counters (M4 efficiency cores, `taskpolicy -c background`)

`fbench/` parses each SVG once and renders it N times; `thread_selfcounts` gives the render thread's exact
instructions and cycles. Builds: resvg's `production` profile (LTO, one codegen unit) with line tables;
`fbench-base` = v0.49.0, `fbench-cap` = both patches (layer alignment with the skew cap + objectBoundingBox
subregions). Min over two alternating rounds per file (`pmu/ab.txt`):

| workload | instructions | cycles | same binary, run to run |
|---|---:|---:|---:|
| 34 rotated/skewed filter files, 1x | -0.01 % | -0.02 % | 0.3-1.2 % / 1.9-7.9 % |
| same, 2x | +0.06 % | -0.05 % | 0.2-0.6 % / 1.9-4.6 % |
| 406 resvg filter tests, 1.5x (pre-cap build) | -0.06 % | -0.06 % | 0.0-0.7 % / 1.6-3.5 % |

Event sampling (femtovg-events template, `pmu/events_*.txt`): branch mispredicts 0.76 / 1,000 branches in both
builds; L1D load misses 6.25 -> 6.44 / 1,000 instructions, IPC 2.66 -> 2.58 in a sampled recording (sampled totals
vary up to ~25 % between recordings; the exact counts above are the measure). Hot path: tiny-skia's pipeline 49 %,
multiply/demultiply alpha 12 %, linear RGB 7 %, box blur 8 %.

Codegen (`pmu/simd.txt`, llvm-objdump per function): tiny-skia's pipeline 17,891 instructions / 2,316 NEON and
`resvg::filter` 11,794 / 235 in both builds. Only per-group set-up code changed: `render_group` +283 instructions,
`to_int_rect`, `Rect::inset` and `copy_region` outlined.

## Fuzz (`fuzz/`)

`gen.py r1 2000 7`: random filter chains (all primitives, extreme parameters, obb/userSpace units, regions,
subregions) under random transform stacks (rotations, skews up to 90°, nearly singular matrices, tiny/huge/negative
scales, nested filtered groups). `run.py`: each case on both builds, 10 s limit, killed past 2 GB RSS (macOS has no
address-space limit). `triage-seed7.txt`, `results-seed7.jsonl`.

| outcome | 0.49.0 | patched |
|---|---:|---:|
| ok | 1,781 | 1,903 |
| killed past 2 GB | 98 | 0 |
| allocation abort (up to 72 PB requested) | 24 | 0 |
| panic | 9 | 6 |
| timeout (10 s) | 49 | 65 |
| outsized (> 1 s or > 256 MB) | 39 | 26 |

0.49's memory blow-ups come from #1155: a near-90° skew makes the scale-only layer millions of pixels tall
(`repro/skew_89.999.svg`: 57 s and 6 GB; 89.9999: 47 GB and climbing). The patch caps each side of such a layer as
Skia's `SkCanvas::get_layer_mapping_and_bounds` does (`max(2 x device, 2048)` there; the filter bounds or 2048 here),
at a lower resolution, and sets the layer bounds to the reduced rect. An earlier version of the cap that re-derived
the bounds from the inverse of a nearly singular matrix still made a 24,474 px layer (`repro/c7_00063.min.svg`).

Every case where the patched build is worse reduces (`reduce.py`) to a cost 0.49 has too: on the minimal files 0.49
is as slow or slower (c7_01077: 52 GB in 30 s on 0.49, 52 MB in 2 s patched); in the full files 0.49 looked fine only
because an IntRect overflow made it skip the group. Pre-existing problems, all reproduced on 0.48.1 and 0.49.0:

1. `feTurbulence` `numOctaves` is not capped (`1e9` = a billion octaves per pixel); Skia caps at 255.
2. `feMorphology` is O(W x H x (2rx+1)(2ry+1)), the radius clamped only to the image (`radius-larger-than-region.svg`
   in resvg's own suite: 12 s on a P-core). A rectangular min/max is separable, and van Herk/Gil-Werman makes each
   pass independent of the radius, output identical.
3. A negative `feMorphology` radius keeps the default (under objectBoundingBox, the whole bounding box) instead of
   passing the input through as Filter Effects says (`repro/c7_01484.min.svg`).
4. `feOffset` / `feDropShadow` with a huge offset panic in tiny-skia's `IntSize::to_int_rect` (`repro/huge-offset.svg`).
5. tiny-skia 0.12: an anti-aliased `fill_path` of a finite rect under a large finite transform panics in
   `AlphaRuns::break_run` (`tsk/`, `repro/tsk-alpharuns.svg`: a plain `<rect>`, no filter).
