The analytic tier of #346, and what a clip or a scissor does to a draw that shares an edge with it. A `clip_path` whose path outlines a rectangle (under any transform), a rounded rectangle or an ellipse is fitted to a box with elliptical corners and carried by each draw under it in two more uniform rows; the fragment shader turns it into the pixel's share inside the box. The clip's edge is antialiased, and the clip costs no stencil draws, no replay and no pass. Only a draw under a shape runs the shader variant that evaluates one, scissored to the pixels the shape reaches. Other paths clip on the stencil as before, as do a shape that partly overlaps the one in force, a box thinner than a pixel, and a shape drawn under with a composite operation coverage cannot bound (`Copy`, `SourceIn`, `SourceOut`, `DestinationIn`, `DestinationAtop`).

An edge a draw has in common with the clip is antialiased once where the two can be told to share it, as in Chromium's GPU rasterizer: a draw that stays inside the clip is not clipped, an upright rect under an upright rect clip is cut to it, one that covers a rounded clip is drawn as the clip, and nested clips that all but coincide count once. The scissor is a box like the clip and meets a draw by the same rules, so a draw that ends on the scissor's edge - the viewport of an export - no longer takes the scissor's coverage over its own. Any other clip's coverage multiplies the draw's, as in every browser.

### Evidence

Along a clip's edge the browsers disagree with one another, so the reference is the exact area: Chromium 131 rendering at 8 device pixels a pixel, each block averaged. Whole frames of master and this PR, each one's difference from that area, and for scale the same difference for Chromium's GPU rasterizer and for WebKit (Safari 27) at one device pixel (orange 9-20/255, red beyond 20, a deviating pixel drawn three wide):

![whole frames of a circle clip, an app icon under two nested rounded clips, a window mock-up and a fill on the viewport's edge, on master and this PR, each against the exact area, with Chromium's GPU rasterizer and WebKit against the same area](https://raw.githubusercontent.com/rebeckerspecialties/femtovg/demo-assets/pr380-clip-edges.png)

What stays red in the PR's column is not the clip's coverage. The icon's letter and logo are the fills' own edges - curves flattened to a quarter pixel, strokes thinner than one (#327) - the same on master. The lines along the icon's and the window's sides are where fills are stacked under one clip edge, or a clipped group meets a border drawn outside it: each draw takes the edge's coverage for itself, so what lies beneath shows through. At one sample a pixel every browser draws that seam, as the last two columns show; master's whole-pixel clip hides it on the pixels it keeps and drops the rest.

| | master | PR | Chromium GPU | Chromium software | Firefox | WebKit |
|---|---:|---:|---:|---:|---:|---:|
| clip-path reftests (50) within 0.15 % of the area at every framing | 3 | 46 | 27 | 17 | 48 | 50 |
| [edge probes](https://github.com/rebeckerspecialties/femtovg/tree/demo-assets/corpus/clip-probes) (19) within a pixel of the exact area's ink | 3 | 15 | 15 | 3 | 2 | 3 |
| pixels beyond 20/255 of the area, over the 396 changed frames every renderer has | 192,595 | 85,790 | 155,604 | 154,375 | 129,046 | 72,551 |
| circle and ellipse clips against the exact area, largest error of 255 | 165 | 13 | 36 | 70 | 73 | |

The same reftests within 0.15 % of each browser, master -> PR: Chromium GPU 3 -> 37, Chromium software 3 -> 13, Firefox 3 -> 45, WebKit 3 -> 46; on all 19 probes the PR's ink is within a pixel of the GPU rasterizer's. Reftest pairs (290) whose test and reference frames agree within 0.15 %: 163 -> 185.

Corpus: 4,158 of 4,732 frames are bit-identical. On the 574 that change, 316,537 of the 377,396 pixels that differ end nearer the area and 40,855 farther, 65.6 -> 12.9 of 255 from it on average. 27 frames move away from it by more than 0.1 points: 17 are WPT mask and nested-clip tests 4-82 % from it on both builds, and the others are the seam above where master's whole-pixel clip fell on the right side of every pixel of an edge (two window mock-ups at 4x), and a rounded or turned clip filled with its own outline, whose two coverages multiply here as in the browsers.

### Tests

`tests/clip_shape_wgpu.rs`: coverage against each pixel's exact share inside the shape (turned, skewed, tight corners, one pixel thick); shared edges covered once under a clip, a scissor and both (a draw inside, a rect a rect cuts, a rect that covers a rounded box, a scissor on the clip), and the product for a rounded and a turned twin; draws the clip holds against the same draws without it, to the bit; a concave fill under a small shape leaving neither winding nor scissor behind, on the screen and in a layer; every kind of draw, nesting, layers, targets and the composite operations that fall back. Unit tests for the fit, coverage map, reach, containment, intersection, what an upright rect is filled as, the scissor's box, and what each draw carries and is bounded by. The OpenGL shader and scissor are checked behind a hidden window ([`gl_clip_check.rs`](https://github.com/rebeckerspecialties/femtovg/tree/demo-assets/harness/clip-bench)).

### Cost

1080p on an M4 Max, master -> PR, medians of paired runs ([pages and scripts](https://github.com/rebeckerspecialties/femtovg/tree/demo-assets/harness/clip-bench)):

| scene | wgpu | OpenGL |
|---|---:|---:|
| 200 cards, each under a rounded-rect clip | 13.8 -> 3.1 ms | 6.2 -> 0.67 ms |
| 200 cards, no clip | 2.81 -> 2.86 ms | 0.43 -> 0.44 ms |
| 40 full-screen fills, no clip | 1.40 -> 1.41 ms | 0.74 -> 0.74 ms |
| the same under a rect clip | 1.53 -> 1.39 ms | 0.83 -> 0.78 ms |
| under a rounded-rect clip | 1.52 -> 1.43 ms | 0.86 -> 1.02 ms |
| under an ellipse clip | 1.52 -> 1.52 ms | 0.76 -> 1.13 ms |
| under a rounded-rect clip of 400 x 300 | 1.53 -> 0.89 ms | 0.47 -> 0.17 ms |
| 40 full-screen paths under that clip | 1.55 -> 0.96 ms | 0.51 -> 0.16 ms |

The cost moves from the clip to the fragments under it. A draw under a shape is scissored to what the shape reaches, so a clip smaller than its content costs less than its stencil did; rects under a rect clip are cut to it; a draw the clip holds whole carries none unless the draw before it did (switching shader variants for it cost the clipped cards 28 % on OpenGL). Fill-bound content that crosses a clip as large as the target pays per fragment: nothing on wgpu, 17 % under a rounded rect and 47 % under an ellipse on Apple's OpenGL. Recording a fill costs the canvas 5 to 10 ns more than master's 230 to 310, and 600 unclipped fills that a scissor holds take 2 % longer to encode. Over the corpus - every file at the fit and at 1080p, 2,392 frames - the frames take 7,647 -> 7,635 ms in sum and the median frame 1.0 % less.
