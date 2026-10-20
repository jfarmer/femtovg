`PathCache::add_point` is meant to merge a point that lands within the distance tolerance (0.01 device pixels) of the one before it, OR-ing in its flags, as nanovg's `nvg__addPoint` does. Since cb5eb84 (2020) it has looked up `points[contour.point_range.end]`: while a contour is being built it is the last one and `end == points.len()`, so the lookup was always `None` and every repeat survived as a zero-length edge. Before that commit it compared with the last point, as `push_flattened_point` (dashing) still does.

A zero-length edge has no direction, so the vertex at it extrudes along one neighbour's normal only:

- a mitred join there leaves its outer corner bare: `M0 0 L10 0 L10 0 L10 10` stroked 4 wide covers nothing of the square at (10..12, -2..0);
- a square or round cap at a repeated end loses its extension;
- the fill's fringe slants along both neighbouring edges, inking up to 100/255 outside an edge that lies on a pixel boundary;
- the contour has no left turn at the repeat, so a convex shape is classified concave and filled through the stencil.

Repeats are common: a pill from `rounded_rect`, and an SVG `rect` whose radius is half its height (usvg emits its zero-length sides as lines), has two; the Illustrator export of the App Store button below ends its outline with a line onto the start point; and at small sizes, segments shorter than the tolerance make them.

The lookup now takes the contour's last point. A flattened curve's chord starts within the tolerance of that point (on it unless the chord before was merged), so a chord twice as long cannot end on it and skips the comparison: without that, the check cost `PathCache::new` 5-7 % more instructions on curve-heavy files.

### Evidence

Master and this PR at 1080p, with Chromium 131 and each build's difference from it (orange 9-20/255, red beyond 20, a deviating pixel drawn three wide):

![a filled icon with repeated corners, the App Store button's bottom edge, a stroked pill and a hole-with-strip probe: master, this PR, Chromium, and each build against Chromium](https://raw.githubusercontent.com/rebeckerspecialties/femtovg/demo-assets/pr-repeated-vertex.png?v=0d36c10)

Corpus (1,196 files at 1x, 2x, 4x, 1080p, 0.5x, 0.25x and 0.1x: 8,372 frames): 7,908 are bit-identical; 464 change, in 143 files. On those, against the exact area (Chromium at 8 device pixels a pixel, each block averaged), 24,805 of the 30,676 pixels that differ end nearer and 3,794 farther, 60.7 -> 11.1 of 255 from it on average; 101 frames move toward it and none away by the share of pixels beyond 20/255. Where software Chromium, Firefox and the area agree to within 20/255, 12,257 pixels move nearer all three by more than 20/255 and 118 farther, at most 5 in a frame. 19 of those are in frames whose repeats are all exact, where this PR draws what master draws without them (below): master's skewed joins had covered one of its own errors there, such as a flattened curve's chord inside the curve. 93 are below 1x, on shapes a few pixels across, and the rest include the tip of an acute fill corner that master's repeat had cut short.

- The 93 frames whose repeats are all lines onto the current point render to the bit as master does with those lines removed from the path. The others merge points under the tolerance, 315 frames of them only those, most below 1x.
- One frame moves away from Chromium (App Store button at 2x): Chromium and WebKit are 17-19/255 from the area on its bottom edges, this PR 1.0 and Firefox 0.3.
- The hole-strip probe (a 0.001-unit strip along a hole's first edge, which must not change the hole) failed at 4x and 1080p, 956 and 1,292 pixels off the control; its strip now merges to a line. From about 10x, where the strip is wider than the tolerance, the hole's classification still samples on it, as before.

### Tests

`src/path/cache.rs`: the corner above keeps three points; a merged point takes the repeat's flags; a contour's first point is never merged into the previous contour; a curve shorter than the tolerance merges into its start; a pill from `rounded_rect` is convex. `tests/repeated_vertex_wgpu.rs`: the mitre covers its corner square with the corner repeated, and mitre, round and bevel joins, butt, square and round caps at repeated ends, and the triangle's fill render the same pixels with and without the repeats. On master the mitre's corner square is bare (alpha 0), the mitre and bevel differ in 4 and 3 pixels, the square and round caps in 36 and 32, and the fill in 38.

### Cost

Instructions per pass of `PathCache::new` over a file's paths at 1080p (spread 0.2 % or less), master -> PR: Ghostscript tiger +0.8 %, puzzle-fox +1.9 %, mr-settodefault +2.0 %, the clip-bench cards page -0.1 % (the comparison without the chord bound: +5.3, +6.7, +7.0 and +3.7 %). In a whole wgpu frame that is 0.1-0.45 %: the harness measures tiger 27.96 -> 28.07 M instructions, puzzle-fox 5.13 -> 5.14, the three card pages within 0.1 %, inside its run-to-run spread of 0.5-2.6 %. Where repeats are merged, points drop out and pills are filled as convex shapes, without the stencil: the page of stroked pills takes 1.6 % fewer instructions on the CPU.
