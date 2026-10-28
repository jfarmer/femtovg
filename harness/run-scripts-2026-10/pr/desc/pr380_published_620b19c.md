The analytic tier of #346, and what a clip or a scissor does to a draw that shares an edge with it. A `clip_path` whose path outlines a rectangle (under any transform), a rounded rectangle or an ellipse is fitted to a box with elliptical corners and carried by each draw under it in two more uniform rows; the fragment shader turns it into the pixel's share inside the box. The clip's edge is antialiased, and the clip costs no stencil draws, no replay and no pass. Only a draw under a shape runs the shader variant that evaluates one, scissored to the pixels the shape reaches. Other paths clip on the stencil as before, as do a shape that partly overlaps the one in force, a box thinner than a pixel, and a shape drawn under with a composite operation coverage cannot bound (`Copy`, `SourceIn`, `SourceOut`, `DestinationIn`, `DestinationAtop`).

An edge a draw has in common with the clip is antialiased once where the two can be told to share it: a draw that stays inside the clip is not clipped - by its bounds, or by the points of its outline, as the clip's own path filled under it is -, an upright rect under an upright rect clip is cut to it, one that covers a rounded clip is drawn as the clip, and nested clips that all but coincide count once. Chromium's GPU rasterizer does the same, but for a turned clip filled with its own outline, and a rounded one at some scales, which it and the other browsers cover twice. The scissor is a box like the clip and meets a draw by the same rules, so a draw that ends on the scissor's edge - the viewport of an export - no longer takes the scissor's coverage over its own. Any other clip's coverage multiplies the draw's, as in every browser.

### Evidence

Along a clip's edge the browsers disagree with one another, so the reference is the exact area: Chromium 131 rendering at 8 device pixels a pixel, each block averaged. Whole frames of master and this PR, each one's difference from that area, and for scale the same difference for Chromium's GPU rasterizer and for WebKit (Safari 27) at one device pixel (orange 9-20/255, red beyond 20, a deviating pixel drawn three wide):

![whole frames of a circle clip, an app icon under two nested rounded clips, a window mock-up, a fill on the viewport's edge and a rounded clip filled with its own outline, on master and this PR, each against the exact area, with Chromium's GPU rasterizer and WebKit against the same area](https://raw.githubusercontent.com/rebeckerspecialties/femtovg/demo-assets/pr380-clip-edges.png?v=620b19c)

What stays red in the PR's column is not the clip's coverage. The icon's letter and logo are the fills' own edges - curves flattened to a quarter pixel, strokes thinner than one (#327) - the same on master. The lines along the icon's and the window's sides are where fills are stacked under one clip edge, or a clipped group meets a border drawn outside it: each draw takes the edge's coverage for itself, so what lies beneath shows through. At one sample a pixel every browser draws that seam, as the last two columns show; master's whole-pixel clip hides it on the pixels it keeps and drops the rest. In the last row the browsers multiply the clip's coverage with that of its own outline filled under it, and the PR draws the fill once; the orange left along the curves here and in the first row is at the level of the reference's own error.

| | master | PR | Chromium GPU | Chromium software | Firefox | WebKit |
|---|---:|---:|---:|---:|---:|---:|
| clip-path reftests (50) within 0.15 % of the area at every framing | 3 | 46 | 27 | 17 | 48 | 50 |
| [edge probes](https://github.com/rebeckerspecialties/femtovg/tree/demo-assets/corpus/clip-probes) (19) within a pixel of the exact area's ink | 3 | 16 | 15 | 3 | 2 | 3 |
| pixels beyond 20/255 of the area, over the 397 changed frames every renderer has | 192,756 | 80,961 | 155,839 | 154,522 | 129,200 | 72,657 |
| circle and ellipse clips against the exact area, largest error of 255 | 165 | 13 | 36 | 70 | 73 | |

The same reftests within 0.15 % of each browser, master -> PR: Chromium GPU 3 -> 37, Chromium software 3 -> 13, Firefox 3 -> 45, WebKit 3 -> 46; on 17 of the 19 probes the PR's ink is within a pixel of the GPU rasterizer's, the other two being the rounded and the turned clip under their own outline. Reftest pairs (290) whose test and reference frames agree within 0.15 %: 163 -> 185.

Corpus: 4,157 of 4,732 frames are bit-identical. On the 575 that change, 316,134 of the 374,436 pixels that differ end nearer the area and 38,377 farther, 66.0 -> 12.5 of 255 from it on average. 24 frames move away from it by more than 0.1 points: 17 are WPT mask and nested-clip tests 4-82 % from it on both builds; five are the seam above, where master's whole-pixel clip fell on the right side of every pixel of an edge (two window mock-ups at 4x, a blur reftest, a wallpaper and a mascot); and two are a file whose clipped boxes Chromium does not paint (`context-fill`), so that their antialiased edge counts against the reference.

### Tests

`tests/clip_shape_wgpu.rs`: coverage against each pixel's exact share inside the shape (turned, skewed, tight corners, one pixel thick); shared edges covered once under a clip, a scissor and both (a draw inside, a rect a rect cuts, a rect that covers a rounded box, a scissor on the clip; a rounded, a turned and an elliptical clip filled with its own outline and a stroke set in from the clip's edge, as without the clip to the bit), and the product for a fill that shares part of the clip's edge; draws the clip holds against the same draws without it, to the bit; a concave fill under a small shape leaving neither winding nor scissor behind, on the screen and in a layer; every kind of draw, nesting, layers, targets and the composite operations that fall back. Unit tests for the fit and how far an outline strays from it, coverage map, reach, containment, intersection, what an upright rect is filled as, the scissor's box, and what each draw carries and is bounded by. The OpenGL shader and scissor are checked behind a hidden window ([`gl_clip_check.rs`](https://github.com/rebeckerspecialties/femtovg/tree/demo-assets/harness/clip-bench)).

### Cost

1080p on an M4 Max, master -> PR, medians of paired runs ([pages and scripts](https://github.com/rebeckerspecialties/femtovg/tree/demo-assets/harness/clip-bench)):

| scene | wgpu | OpenGL |
|---|---:|---:|
| 200 cards, each under a rounded-rect clip | 11.7 -> 2.8 ms | 6.9 -> 0.64 ms |
| 200 cards, no clip | 2.22 -> 2.24 ms | 0.40 -> 0.41 ms |
| 40 full-screen fills, no clip | 1.08 -> 1.10 ms | 0.77 -> 0.77 ms |
| the same under a rect clip | 1.20 -> 1.09 ms | 0.78 -> 0.76 ms |
| under a rounded-rect clip | 1.20 -> 1.14 ms | 0.81 -> 0.96 ms |
| under an ellipse clip | 1.19 -> 1.19 ms | 0.79 -> 1.13 ms |
| under a rounded-rect clip of 400 x 300 | 1.14 -> 0.64 ms | 0.37 -> 0.18 ms |
| 40 full-screen paths under that clip | 1.14 -> 0.68 ms | 0.48 -> 0.17 ms |

The cost moves from the clip to the fragments under it. A draw under a shape is scissored to what the shape reaches, so a clip smaller than its content costs less than its stencil did; rects under a rect clip are cut to it; a draw the clip holds whole carries none unless the draw before it did (switching shader variants for it cost the clipped cards 28 % on OpenGL). Fill-bound content that crosses a clip as large as the target pays per fragment: nothing on wgpu, 19 % under a rounded rect and 45 % under an ellipse on Apple's OpenGL. Recording a fill costs the canvas 5 to 10 ns more than master's 230 to 310, 600 unclipped fills that a scissor holds take 2 % longer to encode, and a rect that a scissor or a rect clip cuts is flattened a second time, 0.3 us. Over the corpus - every file at the fit and at 1080p, 2,392 frames - the frames take 5,980 -> 5,957 ms in sum and the median frame as long as it did (+0.1 %).

