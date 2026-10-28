The analytic tier of #346. A `clip_path` whose path outlines a rectangle (under any transform), a rounded rectangle or an ellipse is fitted to a box with elliptical corners and carried by each draw under it in two more uniform rows; the fragment shader turns it into the pixel's share inside the box. The clip's edge is antialiased, and the clip costs no stencil draws, no replay and no pass. Only a draw under a shape runs the shader variant that evaluates one. Other paths clip on the stencil as before, as do a shape that partly overlaps the one in force, a box thinner than a pixel, and a shape drawn under with a composite operation coverage cannot bound (`Copy`, `SourceIn`, `SourceOut`, `DestinationIn`, `DestinationAtop`).

Where a draw ends on the clip's own edge the browsers disagree: the software rasterizers of Chromium and Firefox multiply the two coverages everywhere, Chromium's GPU rasterizer in fewer cases, and where it does not it is at the exact area. The clip follows the GPU rasterizer: a draw that stays inside the clip is not clipped, an upright rect filled under an upright rect clip is cut to it, nested clips and a scissor on the clip's outline (the viewport of an export whose clip is its own frame) count once, and any other clip's coverage multiplies the draw's.

### Evidence

master, this PR, and each build's difference from Chromium 131 rasterizing in software and on the GPU and from Firefox 158 (orange 9-20/255, red beyond 20):

![clip edges on master and this PR: each build's difference from Chromium 131 in software, Chromium 131 on the GPU and Firefox 158, side by side](https://raw.githubusercontent.com/rebeckerspecialties/femtovg/demo-assets/pr380-clip-shapes.png)

| | master | PR |
|---|---:|---:|
| circle and ellipse clips against the exact pixel area, largest error of 255 (Chromium 70 in software and 36 on the GPU, Firefox 73) | 165 | 13 |
| clip-path reftests (50) within 0.15 % of GPU Chromium at every framing | 3 | 37 |
| the same against software Chromium | 3 | 13 |
| the same against Firefox (the three agree with one another on 12 to 21) | 3 | 45 |
| [edge probes](https://github.com/rebeckerspecialties/femtovg/tree/demo-assets/corpus/clip-probes) (16) with GPU Chromium's ink to a pixel | 3 | 14 |
| reftest pairs (290) whose test and reference frames agree within 0.15 % | 163 | 185 |

Corpus: 4,367 of 4,768 frames are bit-identical; of the rest 305 move toward GPU Chromium and 36 away, 247 toward software Chromium and 14 away, 242 toward Firefox and 38 away, none structurally. Of the 23 that move away from GPU Chromium by more than 0.1 points, 15 are WPT mask and nested-clip tests 4-82 % from it on both builds and 3 a reduction whose 128-contour fill the PR draws under its clip, where master and that rasterizer run out of stencil bits. Against the software rasterizers they are edges those multiply or snap to a quarter pixel (rows 4, 5, 7 and 8). The two probes left over have no clip: a draw that ends on a scissor's edge takes the scissor's coverage over its own, on master as here.

### Tests

`tests/clip_shape_wgpu.rs`: coverage against each pixel's exact share inside the shape (turned, skewed, tight corners, one pixel thick); shared edges covered once (a draw inside the clip, a rect a rect clip cuts, a scissor on the clip) and the product for a rounded and a turned twin; draws the clip holds against the same draws without it, to the bit; every kind of draw, nesting, layers, targets and the composite operations that fall back. Unit tests for the fit, coverage map, containment, intersection, the shared rect, the scissor's box and what each draw carries; the OpenGL shader checked against the same shares behind a hidden window ([`gl_clip_check.rs`](https://github.com/rebeckerspecialties/femtovg/tree/demo-assets/harness/clip-bench)).

### Cost

1080p on an M4 Max, master -> PR, medians of paired runs ([pages and scripts](https://github.com/rebeckerspecialties/femtovg/tree/demo-assets/harness/clip-bench)):

| scene | wgpu | OpenGL |
|---|---:|---:|
| 200 cards, each under a rounded-rect clip | 14.2 -> 3.2 ms | 6.5 -> 0.64 ms |
| 200 cards, no clip | 2.97 -> 3.00 ms | 0.46 -> 0.46 ms |
| 40 full-screen fills, no clip | 1.47 -> 1.45 ms | 0.78 -> 0.78 ms |
| 40 full-screen fills under a rect clip | 1.60 -> 1.48 ms | 0.83 -> 0.79 ms |
| 40 full-screen fills under a rounded-rect clip | 1.51 -> 1.52 ms | 0.81 -> 0.94 ms |
| 40 full-screen fills under an ellipse clip | 1.51 -> 1.59 ms | |

The cost moves from the clip to the fragments under it: fill-bound content under a rounded or an elliptical clip pays up to 5 % on wgpu and 15 % on OpenGL, rects under a rect clip are cut to it and cost 6 % less than under the stencil, and a draw the clip holds whole carries none unless the draw before it did - switching shader variants for it cost the clipped cards 28 % on OpenGL.
