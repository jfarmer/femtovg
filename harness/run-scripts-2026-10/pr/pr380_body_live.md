The analytic tier of #346. A `clip_path` whose path outlines a rectangle (under any transform), a rounded rectangle or an ellipse is fitted to a box with elliptical corners and carried by each draw under it in two more uniform rows; the fragment shader turns it into the pixel's share inside the box. The clip's edge is antialiased, and the clip costs no stencil draws, no replay and no pass. Only a draw under a shape runs the shader variant that evaluates one. Other paths clip on the stencil as before, as do a shape that partly overlaps the one in force, a box thinner than a pixel, and a shape drawn under with a composite operation coverage cannot bound (`Copy`, `SourceIn`, `SourceOut`, `DestinationIn`, `DestinationAtop`).

### Evidence

master, this PR, Chromium 131, Firefox 158, and the PR's difference from each browser (orange up to 20/255, red beyond):

![clip edges on master, this PR, Chromium and Firefox, and the PR's difference from each browser](https://raw.githubusercontent.com/rebeckerspecialties/femtovg/demo-assets/clip-shapes-evidence.png)

| | master | PR |
|---|---:|---:|
| circle and ellipse clips against the exact pixel area, largest error of 255 (Chromium 70, Firefox 73) | 165 | 13 |
| clip-path reftests (50) within 0.15 % of Firefox at every framing | 3 | 45 |
| the same against Chromium (the browsers agree with each other on 21) | 3 | 13 |
| reftest pairs (290) whose test and reference frames agree within 0.15 % | 163 | 185 |

Corpus: 4,362 of 4,748 frames are bit-identical; of the rest 240 move toward Chromium and 10 away, 228 toward Firefox and 21 away, none structurally. The frames that move away by more than 0.1 points (3 against Chromium, the last row the worst; 12 against Firefox, two of them the half-pixel probes) are single rows or columns where the clip's edge runs along another antialiased edge part of the way across a pixel. The coverages multiply there, as in the browsers (row 4), but the browsers snap a path's edge to quarter pixels vertically, and of a half-covered column draw a quarter or nothing (row 6, [probes](https://github.com/rebeckerspecialties/femtovg/tree/demo-assets/corpus/clip-probes)).

### Tests

`tests/clip_shape_wgpu.rs`: coverage against each pixel's exact share inside the shape (turned, skewed, tight corners, one pixel thick), every kind of draw, nesting, layers, targets and the composite operations that fall back; unit tests for the fit, coverage map, containment and intersection; the OpenGL shader checked against the same shares behind a hidden window ([`gl_clip_check.rs`](https://github.com/rebeckerspecialties/femtovg/tree/demo-assets/harness/clip-bench)).

### Cost

1080p on an M4 Max, master -> PR, medians of paired runs ([pages and scripts](https://github.com/rebeckerspecialties/femtovg/tree/demo-assets/harness/clip-bench)):

| scene | wgpu | OpenGL |
|---|---:|---:|
| 200 cards, each under a rounded-rect clip | 13.5 -> 2.6 ms | 8.2 -> 0.6 ms |
| 200 cards, no clip | 2.11 -> 2.08 ms | 0.42 -> 0.42 ms |
| 40 full-screen fills, no clip | 0.92 -> 0.92 ms | 0.82 -> 0.81 ms |
| 40 full-screen fills under one rounded-rect clip | 0.99 -> 1.03 ms | 0.98 -> 1.17 ms |

The cost moves from the clip to the fragments under it: fill-bound content under one clip pays 2-9 % on wgpu and 15-19 % on OpenGL.

