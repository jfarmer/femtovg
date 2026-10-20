`tesselate_bezier` keeps a piece when its control points lie close enough to its chord: `(d2 + d3)^2 < tess_tol * chord^2`. A cubic whose four points coincide has a zero chord, both sides are zero, the test fails, and the flattener halves the cubic down to its depth limit: 2,047 pieces, none of which adds a point. Every square corner of a `rounded_rect_varying` is such a cubic, since it emits a cubic for every corner whatever the radius; so is every curve under a transform that scales to nothing, since the canvas builds a path's cache before anything could skip it; and so is a zero-length curve in SVG data. nanovg flattens the same way. Skia sizes a cubic by Wang's formula, which is zero for it, and takes one segment.

## Changes

- **`PathCache::new` skips a cubic whose control points and end equal its start**, before flattening. The outline keeps the point it already has, exactly as the descent left it. A cubic whose ends meet but whose control points do not, a loop, is flattened as before.

## Cost

M4 Max, 1080p, master 9f5ad26 -> this PR, medians of paired runs:

| | CPU encode a frame | whole frame |
|---|---:|---:|
| Ghostscript tiger at scale 0, the first frame of a scale-in | 9.06 -> 0.52 ms | 9.77 -> 0.97 ms |
| 300 tabs rounded on top, as `rounded_rect_varying(.., 6, 6, 0, 0)` draws them (demo-assets `harness/clip-bench/tabs_300.svg`) | 3.44 -> 0.70 ms | 4.40 -> 1.51 ms |
| pixel emoji icon, all 4 curves points | 0.256 -> 0.241 ms | 1.388 -> 1.372 ms |
| ember logo, 2 of 1,348 curves | 2.333 -> 2.274 ms | 8.060 -> 7.969 ms |
| line icon, 1 of 35 curves | 0.100 -> 0.093 ms | 0.693 -> 0.688 ms |

The corpus renders to the bit as on master: 11,403 frames of its 1,267 files at all nine framings. (One frame, with a layer, differed once while the machine was at a load of 100; it renders identically on both builds every time since.) Its SVGs hold few such curves, 7 of 97,536, in the three files above:

![the pixel emoji, the ember logo and the line icon at 1080p: master, this PR, Chromium, and each build against Chromium - the same pixels](https://raw.githubusercontent.com/rebeckerspecialties/femtovg/demo-assets/pr-degenerate-cubic.png?v=d17aa15c)

The Babylon canvases have none, because their capture writes a zero-radius corner as no curve at all; BabylonNative's `roundRect` goes to `rounded_rect_varying`, which makes one, and its Native Canvas test draws `roundRect(.., [0, 30, 50, 60])`. Every other curve pays one comparison; over the 160 files timed against master the median change is -0.1 %.

## Tests

Unit tests count the pieces the flattener examines: none for a cubic that is a point (master: 2,047), none for a rounded rect under a transform that scales to nothing, and for a tab with two square corners half as many as for the same rect rounded all round. A loop whose ends meet is still flattened. The count is a thread-local that only test builds compile.

