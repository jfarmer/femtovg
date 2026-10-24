# resvg filters under rotation and skew (#254, #1143, #874, #949, #1152), 2026-10-24

Renderers: resvg 0.48.1, 0.49.0 and two patches on 0.49.0; Chrome Canary 158, Firefox Developer Edition 159b5,
Safari 27.2's WebKit (22625) and Safari Technology Preview's WebKit (22627, loaded into `wk_shot` with
`DYLD_FRAMEWORK_PATH` and `__XPC_DYLD_FRAMEWORK_PATH`; its WebContent and GPU processes were checked to come from the
STP bundle). Each SVG is a standalone document in an iframe of its natural size; scale by device pixel ratio
(Chrome, WebKit) or CSS zoom (Firefox, whose `--screenshot` ignores the ratio; in Chrome, zoom and ratio are
pixel-identical). Chrome's new headless mode clamps a small window (200 x 200 gave a 500 x 113 viewport), hence the
iframe in a large window.

## What 0.49 already fixed

resvg#1155 (LaurenzV, merged 2026-10-16, in 0.49) filters a rotated or skewed group in its scaled user space and draws
the result with the rotation or skew: the decomposition Skia uses. #949 (2.26 -> 0.01 % beyond 20/255 vs Chrome), the
filter half of #874, the axis-aligned-bounding-box clip of #1143 (5.08 -> 1.74 %) and most `complex-transform` tests
now match. RazrFalcon's "no idea how to implement it" (2024) and the pointer from #1143 to #254 (2026-09-28) predate it.

## What remains, and the two patches

1. `0001-Keep-rotated-and-skewed-filter-layers-aligned-with-u.patch` (resvg, +30/-16, 19 references): #1155 left the
   translation in the layer transform, so a rotated layer's pixel grid sits at a fractional offset from user space, and
   it recovers the layer transform as `inv_rest * transform`, whose float error (59.999996, a column norm of
   1.4999999) `floor()` turns into a whole pixel. The patch is Skia's `Mapping::decomposeCTM` (layer = scale only,
   remainder = everything else, scale+translate CTMs unchanged) and `RoundOut` (`kRoundEpsilon = 1e-3`,
   crbug.com/1313579), src/core/SkImageFilterTypes.cpp. 34 files x 4 scales: 44 frames closer to Chrome, 4 further
   (2 feFlood frames dominated by item 2, +0.1; feTile, where the browsers disagree by 8-10 %). At the suite's 300 px:
   13 of 18 comparable references closer, feTile and the two text `filter-bbox` tests further (resvg's text bbox is
   already 2-3 px taller than the browsers'; rounding out adds a row). `layer-alignment.png`.
2. `0001-Resolve-objectBoundingBox-primitive-subregions-again.patch` (usvg, +24/-57, 3 references): with
   `primitiveUnits="objectBoundingBox"`, `feFlood`/`feImage` took unspecified x/y/width/height from the bounding box,
   and every other primitive took specified fractions of the filter region. Filter Effects: specified -> fractions of
   the bounding box, unspecified -> the filter region. All four browsers agree; the three references go to 0.00-0.90 %.
   This is why `feFlood/complex-transform` failed. With both patches it is 9.09 -> 0.11 % at 1x. `obb-subregion.png`.

## #874, retested

`i874-root-transform.png`: Chrome Canary, Firefox and Safari TP rotate a root `<svg transform>` about the centre of the
svg's box (CSS Transforms 1: `transform-origin` starts at `50% 50%`; `0 0` only for SVG elements without a CSS layout
box). Shipping Safari 27.2 ignores the attribute. resvg 0.48 rotated about (0, 0); 0.49 (#1085) about the centre,
0.11-0.13 % off; with patch 1, 0.00 %. The 2024 disagreement has converged.

## Not this class, or no common ground

- feTile + skew: the browsers disagree among themselves (7.8-10.2 %); the test is titled "UB".
- #1152 lighting under scale: Chrome and Firefox take the surface slope per user unit, WebKit and resvg per pixel;
  Filter Effects allows the pixel when `kernelUnitLength` is unspecified. The rotation half is fixed by #1155.
- feImage at a fractional scale (1.77): the image is placed at the subregion's integer origin; 3.55 % off Chrome
  unrotated too.
- feOffset with dx = dy = 0: resvg and WebKit return the input unclipped by the subregion; Chrome and Firefox clip it.

Files: `tools/` (render.py natural size, render2.py SCALE, compare*.py, strip*.py, t15.py for the suite's 300 px,
wk_shot_s.swift with `WK_SCALE`), `probes/`, `multiscale.txt`, `suite-300px.txt`, `remaining-on-0.49.png`.
