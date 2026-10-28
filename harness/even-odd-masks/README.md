# Even-odd holes in coverage masks

Evidence for femtovg's "Wind an even-odd hole against what it cuts out of a
mask" (branch `even-odd-mask-winding`, 153e3f0 on master 9f5ad26).

A coverage mask (a clip's, and on the `thin-fill-masks` branch a thin fill's)
is rasterized by adding each edge's signed area into the cells it crosses and
folding the sum by the fill rule. The fold is exact where a pixel sees at most
two windings, one apart. An even-odd ring thinner than a pixel with both
circles wound alike puts windings 0, 1 and 2 into the pixels it crosses, and
its hole counted as coverage. Even-odd does not depend on direction, so the fix
winds each hole's contour against the contours around it - as `expand_fill`
already winds them for its fringe - and nested contours wind 0 or 1.
Non-zero is left alone: there the direction is the meaning.

- `scenes.json`: three clips (`clippath`: contours and a rule) filled through
  with navy on a 120 x 96 canvas.
- `scenes-vs-area.png`: before, after, the 8x area reference (Chromium 131 at
  8x, averaged over each 8 x 8 block), and each against it, at 3x;
  `scenes-vs-area-detail.png`: the top-right quarter at 10x, the pixels the fix
  moved outlined in magenta; `scenes-vs-chromium.png`: against Chromium at 1x.
- To reproduce: `../thin-fill-masks/scenes_area.py scenes.json OUT` (area),
  `SCENES=scenes.json ../hard-mask-scenes/scenes_chromium.py OUT` (Chromium),
  `../hard-mask-scenes/wgpu_scenes.rs` (WGPU) and `../clip-bench/gl_scenes.rs`
  (OpenGL), then `../hard-mask-scenes/strip.py` with `REF_NAME='8x area'`.
  OpenGL and WGPU are pixel-identical on all three, before and after.

Ink in pixels of navy, and pixels more than 20 levels off the area reference:

| scene | area | master | fix | Chromium 1x |
|---|---|---|---|---|
| even-odd ring 0.5 px wide, circles wound alike | 103.5 | 132.8 (136 off) | 103.9 (0) | 105.3 (22) |
| non-zero ring, hole wound against it (control) | 103.5 | 103.9 (0) | 103.9 (0) | 105.3 (22) |
| even-odd disc, its hole 0.2 px from the edge | 407.4 | 419.2 (48) | 408.0 (0) | 413.3 (47) |

The library's unit test `an_even_odd_ring_wound_alike_holds_its_area` (a ring
0.4 px wide, area 74.9): the clip's mask held 113.4 px before the fix.

Corpus, 2026-10-15: every one of the 11,403 frames is identical before and
after with thin-fill masks off (`identity.py tfm_off tfme_off`: the
`thin-fill-masks` branch before and after it was rebuilt on this fix, the
masks switched off, so that the two differ by this fix alone). No corpus clip
has even-odd contours nested within a pixel of each other.
