## Problem

`Canvas::clip_path` (#324) resolves the clip on one stencil bit: a pixel is inside the clip or outside it, so every clip boundary is a hard, single-sample edge. Browsers antialias clip edges: Chromium's canvas `clip()` and its SVG `clip-path` go through Skia with `SkCanvas::clipPath(path, /*doAntiAlias=*/true)`, and Firefox's cairo clips blend coverage the same way. Every fill and stroke edge in femtovg is antialiased by its fringe; the clip edge is the one edge that is not.

## Evidence

The clip scene (`clipdemo.svg`: a nonzero star clip and an even-odd donut clip over gradients and overlapping shapes) against Chromium 131 on master 1334764, 460x260 pivot-zoom framing:

| zoom | px > 20/255 | structural (2 px erosion) |
|---|---|---|
| 1x | 0.54 % | 0.000 % |
| 2x | 0.68 % | 0.000 % |
| 4x | 0.43 % | 0.000 % |

Every differing pixel is on a clip edge. At 4x, crop of the star's clip edge (femtovg / Chromium / diff in red), then the whole diff frame with the crop marked:

![clip edge at 4x: femtovg staircase vs Chromium coverage](https://raw.githubusercontent.com/rebeckerspecialties/femtovg/demo-assets/clip-edge-antialiasing.png)

Real-world reach: 24 of the 27 BuseyBench portraits and the Reddit logo (a circle `clip-path`, 0.31 % of pixels at 1x) carry this ribbon; it is what stays of the clip residual after #324 and it grows visible under zoom.

## Proposal

Two tiers, so the common case costs no texture:

1. **Analytic coverage for rect, rounded-rect and ellipse clips** - #380. A clip whose path outlines a rectangle under any transform, a rounded rectangle or an ellipse is evaluated in the fragment shader of the draws under it instead of the stencil, blending coverage at the edge. Zero textures, zero allocations, no render-pass break. Of the corpus's 325 clips at 1x it takes 176; 6 more add nothing to the shape around them.
2. **Coverage mask for arbitrary paths** - what remains of this issue after #380: 135 of the 325 clips (86 of them in BuseyBench portraits), and the 8 shapes that only partly overlap another shape clip. render the clip path with its antialiased fringe into a single-channel transient (budgeted like a layer store; `R8` where the backend has it, RGBA8 otherwise) and multiply it in the fragment shader; the stencil keeps gating the interior so nesting stays one compare and the mask only decides the edge. One mask per active arbitrary-path clip level; a level the budget cannot admit keeps today's hard edge, so the fallback is the current behaviour rather than an unclipped draw.

Reference: Skia draws simple clip shapes as analytic coverage fragment processors and complex ones through a coverage mask (`GrClipStackClip`, `GrSWMaskHelper`).

## Tests

The clip scene ladder at 1x / 2x / 4x dropping from 0.4-0.7 % of pixels toward the browser-vs-browser envelope; the WPT `2d.path.clip.*` cases stay pixel-exact; a pixel test that a circle clip's edge column takes intermediate coverage values; the stencil tests of #324 unchanged (nesting, even-odd, resize, per-target clips).


## Reftests (2026-10-03)

The clip-path group of an extracted reftest suite (47 test/reference pairs modelled on WPT `css-masking` and the resvg `clipPath` tests: circles, ellipses, polygons, stars, rotated and nested clips, and a 40-case parameter sweep) shows the same ribbon on every pair. On the #372/#373/#374 stack, 46 of the 47 pairs differ from Chromium 131 by 0.16-0.66 % of pixels at 2x or 4x, and in every one femtovg's own test-against-reference difference is that same number (within 0.02 points) while Chromium's is 0.00: the reference fills the shape, the test clips a rect to it, and the clip edge is all that differs.

| pair (worst framing) | px > 20/255 vs Chromium | femtovg test vs its reference | Chromium test vs its reference |
|---|---:|---:|---:|
| clip-path-multiple-shapes-union (2x) | 0.66 % | 0.68 % | 0.00 % |
| clip-path-star-evenodd (2x) | 0.61 % | 0.62 % | 0.00 % |
| clip-path-ellipse (4x) | 0.48 % | 0.48 % | 0.00 % |
| clip-path-circle (2x) | 0.43 % | 0.43 % | 0.00 % |
| clip-path-transform-rotate (4x) | 0.43 % | 0.43 % | 0.00 % |
| clip-path-polygon-triangle (4x) | 0.43 % | 0.43 % | 0.00 % |
| clip-path-variation-11 to -50 (40 pairs, 2x/4x) | 0.16-0.49 % | the same, pair by pair | 0.00 % |

clip-path-ellipse at 4x, the upper-right edge (femtovg / Chromium / diff, red beyond 20/255):

![clip-path-ellipse at 4x: femtovg's single-sample clip edge vs Chromium](https://raw.githubusercontent.com/rebeckerspecialties/femtovg/demo-assets/wpt-clip-edge.png)

The 47th pair (clip-path-concentric-circles-evenodd, 38 %) is a different defect - the clip's children combined under one fill rule instead of unioned (#377) - and is not this issue's.

With #380 the circle, rect, rounded-rect and rotated-rect pairs and the 40-case sweep come within 0.15 % of Firefox at every framing: 45 of the suite's 50 clip-path tests, against 3 on master. The ellipse pair stays at 0.34 % at 4x, where Firefox's own edge is up to 73/255 from the exact pixel area and the PR's 13/255. The triangle, the even-odd star and the multi-shape union are arbitrary paths and keep the ribbon until tier 2.


