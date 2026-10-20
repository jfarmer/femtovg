Fixes #377. Fixes #346: its second tier, after #380.

A `clip_path` whose path is no box went to the stencil, where a pixel is inside or outside by its center. It is now rasterized on the CPU into a coverage mask - the exact area of the flattened path in each pixel of its bounds, one byte a pixel - which the fragment shader of each draw under it reads, as it evaluates a clip shape: the clip's edge is antialiased, and the clip costs no stencil draws, no replay and no pass. `Canvas::clip_paths` clips to the union of several paths, each under its own fill rule - the children of an SVG `clipPath` - resolved inside the mask, where children that share an edge leave no seam.

A clip asked for again bit for bit - the same paths under the same transform - has its mask without a path being flattened; one that has moved by whole pixels is found by its outline, to a 256th of a pixel from the mask's own corner; any other is rasterized anew. Masks nest as the product of their coverages and ride beside a clip shape and its cuts; the draws under one are scissored to the pixels it spans. They are kept within a budget (`set_clip_mask_budget`, 32 MiB by default), past which a clip goes to the stencil as before, and a composite operation that coverage cannot bound takes a mask whole or not at all.

### Evidence

Whole frames of master and this PR, each one's difference from the exact area (Chromium 131 at 8 device pixels a pixel, each block averaged), and the same difference for Chromium's GPU rasterizer and for WebKit at one device pixel (orange 9-20/255, red beyond 20, a deviating pixel drawn three wide):

![concentric circles under even-odd, two circles unioned, an even-odd star, a triangle and the clip scene of #346: master, this PR, the exact area, each build's difference from it, and Chromium's GPU rasterizer and WebKit against it](https://raw.githubusercontent.com/rebeckerspecialties/femtovg/demo-assets/pr-clip-masks.png?v=ca9cd38)

The first row is #377: master joins the two circles into one path under even-odd and cuts out the disc the browsers fill. The orange left along the circles is at the reference's own error on a curve: there the masks are within 9/255 of WebKit, which is up to 10/255 from the reference itself. In the clip scene the red that stays is where several fills meet one clip edge, each taking the clip's coverage there as every browser does at one sample a pixel; the frame is at WebKit's level (413 pixels beyond 20/255 of the area at 2x; WebKit 410, Chromium GPU 534, master 834).

| | master | PR | Chromium GPU | Chromium software | Firefox | WebKit |
|---|---:|---:|---:|---:|---:|---:|
| clip-path reftests (50) within 0.15 % of the area at every framing | 46 | 50 | 27 | 17 | 48 | 50 |
| pixels beyond 20/255 of the area, over the 77 changed frames every renderer has | 233,609 | 71,777 | 87,521 | 78,520 | 41,115 | 79,200 |

Corpus: 4,640 of 4,784 frames are bit-identical; on the 144 that change, in 40 files, 226,980 of the 270,534 pixels that differ end nearer the area and 30,255 farther, 146.4 -> 6.8 of 255 from it on average. Eight frames move away by more than 0.1 points, all of the two WPT tests of a mask nested in a panned clip (`mask-nested-clip-path-panning-001`, `-002`), which are 14-60 % from the area on both builds. With the budget at zero and the children joined, the build renders master's 144 frames to the bit.

### Tests

`tests/clip_mask_wgpu.rs`: a mask's coverage against the exact area of a triangle, an arrow and a sliver in each pixel, in place, scaled and turned (within 1.5/255), and of a ring; unions - children that share an edge, that overlap, under each fill rule; nesting as the product, a twin once, a mask beside a shape; every kind of draw; a concave fill under a small mask leaving no winding and no scissor behind, on the screen and in a layer; targets; an operation that takes the mask whole; reuse, the budget and the fallback. The stencil-era clip tests (`path_clip_wgpu.rs`, `wpt_clip_wgpu.rs`) run every scenario both ways and compare the two away from edges. Unit tests for the rasterizer against polygon areas, for keys, nesting, reuse and release, and for what each draw carries. The OpenGL shader checked behind a hidden window ([`gl_mask_check.rs`](https://github.com/rebeckerspecialties/femtovg/tree/demo-assets/harness/clip-bench)).

### Cost

On an M4 Max, master -> PR, medians of paired runs:

| | master | PR |
|---|---:|---:|
| wgpu: 40 full-screen fills under a star clip about a quarter of 1080p | 1.00 ms | 0.79 ms |
| OpenGL: the same under a star as tall as the target | 0.43 ms | 0.62 ms |
| OpenGL: under a star of 300 px | 0.38 ms | 0.12 ms |
| wgpu: the 156 corpus frames the masks change, in sum | 4,077 ms | 4,080 ms |
| wgpu: 600 fills a frame, no clip / under rounded clips | 2.15 / 2.77 ms | 2.17 / 2.81 ms |

The median of those corpus frames is 1.5 % shorter, the clip-path reftests' 14 % and the clip scene's at 1080p 29 %. A mask costs a texel for each fragment under it, which Apple's OpenGL shows on fill-bound content under a clip as large as the target, and which the scissor to the mask's pixels repays under a smaller one; on wgpu the masks are faster than the stencil throughout (the star page 1.03 -> 0.82 ms with the same build and the budget at zero).

On the CPU, a clip that was taken before and a fill under it cost the canvas 0.6 to 0.9 us, where the stencil clip's cost 0.7 to 1.25. A new or changed clip is rasterized: 6 us for a mask of 64 px, 12 us at 200 px, 60 us for a star of 900 px on a performance core, and 2.5 to 3.5 times that on an efficiency core. The masks of a corpus frame hold 0.2 MiB at the median and 2.2 MiB at most, of a budget of 32. A draw under no mask binds no mask texture: on wgpu the draws' bind group is bound again for every draw's uniforms, and the mask's binding in it cost about 1 % of the instructions of 600 unclipped fills, so it has a layout of its own. What is left on draws under none is the mask field each draw's parameters carry: 600 fills take 0.6 % more instructions with no clip and 0.7 % more under rounded clips; master with its parameters padded to the same size takes 0.4 % more.
