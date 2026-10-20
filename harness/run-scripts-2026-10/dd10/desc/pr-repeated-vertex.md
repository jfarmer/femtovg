`PathCache::add_point` is meant to merge a point that lands within the distance tolerance (0.01 device pixels) of the one before it, OR-ing in its flags, as nanovg's `nvg__addPoint` does. Since cb5eb84 (2020) it has looked up `points[contour.point_range.end]`, one past the last point of a contour still being built, so the lookup was always `None` and every repeat survived as a zero-length edge. A zero-length edge has no direction, so the vertex at it extrudes along one neighbour's normal only:

- a mitred join there leaves its outer corner bare: `M0 0 L10 0 L10 0 L10 10` stroked 4 wide covers nothing of the square at (10..12, -2..0);
- a square or round cap at a repeated end loses its extension;
- the fill's fringe slants along both neighbouring edges, inking up to 100/255 outside an edge that lies on a pixel boundary;
- a convex contour has no left turn at the repeat, so it is classified concave and filled through the stencil.

Repeats are common. `Path::rounded_rect` gives a pill two, its sides being zero long, and usvg does the same for an SVG `rect` whose radius is half its height; the Babylon canvas captures start each rounded corner with a line to the current point, as the canvas `arc` does; the Illustrator export of the App Store button below ends its outline with a line onto its start; and below 1x, segments shorter than the tolerance make them.

## Changes

- **`add_point` compares with the contour's last point** (`src/path/cache.rs`) and merges the new point's flags into it. `push_point` is the push without the comparison.
- **The flattener compares the points between chords in registers.** It knows the last point it emitted - the cubic's start, then each point taken - so a point within the tolerance of it is dropped there; such a point has no flags to merge. The cubic's end, which carries the corner flag, goes through `add_point`. Over the corpus this renders every frame as calling `add_point` for every point does (8,869 frames, 52 points dropped this way).

## Corpus

1,267 files, Babylon's canvas tests among them, at 1x, 2x, 4x, 1080p, 0.5x, 0.25x and 0.1x: 8,336 of 8,869 frames are unchanged, and 533 change, in 158 files. Against Chromium 131 (the difference panels are white within 8/255 of the reference, orange from 9 to 20 and red beyond):

![Babylon's Native Canvas, GUI and ktx2 tests, the firefox.com App Store button, a stroked pill and the hole-strip probe: master, this PR, Chromium, and each build against Chromium](https://raw.githubusercontent.com/rebeckerspecialties/femtovg/demo-assets/pr-repeated-vertex.png?v=d17aa15c)

Where Chromium is the one off, against the area reference instead (Chromium at 8 device pixels a pixel, each block averaged):

![a svgenius icon, the NYT tiles and the banner lettering: master, this PR, the area reference, and each build against it](https://raw.githubusercontent.com/rebeckerspecialties/femtovg/demo-assets/pr-repeated-vertex-area.png?v=d17aa15c)

| 1080p, px beyond 20/255 of the area | master | this PR | Chromium | Firefox |
|---|---:|---:|---:|---:|
| svgenius icon (`page_700 icon_30`) | 2,595 | 25 | 1,123 | 1,159 |
| App Store button | 1,358 | 203 | 2,164 | 2,156 |
| Babylon GUI rectangles (`gui-force-resize-width`) | 811 | 288 | 763 | 488 |
| banner lettering | 655 | 71 | 653 | 482 |
| NYT tiles | 142 | 27 | 1,154 | 1,828 |

Over the 533 frames, against the area reference, 124 move toward it, 406 stay level and 3 move away, each by about 0.01 points (one or two pixels at 0.25x and 0.1x). Of the 47,725 pixels that change, 37,104 end nearer and 7,934 farther; on average they were 49.0/255 from it and are 13.0. Where Chromium, Firefox and the area agree to within 20/255, 13,970 pixels move nearer all three by more than 20/255 and 112 farther, at most 5 in a frame.

- The 136 frames whose repeats are all lines onto the current point render to the bit as master does with those lines removed from the path. The others also merge points closer than the tolerance, most of them below 1x.
- Every changed pixel lies near a contour that merged a point - within 2 px of its bounds, or a stroke's width for a stroke - or, inside a layer, near the same contour offset by the layer's origin. The exception is the hole-strip probe: its 0.0054 px strip along the hole's edge now merges to a line and no longer flips the hole's fringe.
- Three frames move away from Chromium. The App Store button at 2x and 0.25x: on its changed pixels this PR is 0.9/255 from the area and Firefox, Chromium 19. The ktx2 test at 4x: its changed pixels are the labels in the bars, where Chromium and Firefox are 46 and 62/255 from the area on average; the PR moves toward both browsers there (28.6 -> 19.1 and 41.4 -> 30.8) and away from the area (22.5 -> 31.2).

## Tests

`src/path/cache.rs`: the corner above keeps three points; a merged point takes the repeat's flags; a contour's first point is never merged into the previous contour's last; a curve shorter than the tolerance merges into its start; a pill from `rounded_rect` is convex. `tests/repeated_vertex_wgpu.rs`: with the corner repeated, the mitre still covers its corner square, and mitre, round and bevel joins, butt, square and round caps at repeated ends, and the triangle's fill render the same pixels with and without repeats. On master the corner square is bare (alpha 0) and the mitre, the bevel, the square and round caps and the fill differ in 4, 3, 36, 32 and 38 pixels.

## Cost

`PathCache::new` alone, instructions per pass over a file's paths at the canvas's tolerance (spread 1 % or less), master -> this PR: Ghostscript tiger -5.7 %, puzzle-fox -6.3 %, the clip-bench cards page -4.6 %, mr-settodefault -6.4 %, Babylon's Native Canvas -5.2 % (with 3 % fewer points). Part of that may be how the compiler lays the function out rather than work saved. Frame times are unchanged within run-to-run noise.
