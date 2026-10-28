Fixes #376.

A filter primitive's result is clipped to its subregion - by default the filter region - before the next primitive reads it, so what an offset, a morphology or a blur pushes out of the region does not come back. `ImageFilter::Crop { x, y, width, height }` says where in a chain: the pass before it draws inside the rectangle only, as a scissor on its last draw, so the crop is no pass of its own; with no pass before it, it is a copy. The rectangle is in the image's pixels for `filter_image_chain` and in root device space for a layer's filters, as a blend's backdrop rect is, and is rounded out to whole pixels.

A matrix after a crop still folds into the cropped pass, or into a blur's second draw, wherever one crop leaves what the two passes would: its own crop lies inside the first, or it leaves transparent black as it is. A pyramid's first halving does not take a cropped matrix over: the rectangle is of full-size pixels.

### Evidence

master, this PR with a crop after every primitive, and each one's difference from Chromium 131 (orange 9-20/255, red beyond 20, a deviating pixel drawn three wide):

![three filter reftests whose intermediate results leave the filter region: master, this PR, Chromium, and each build's difference from Chromium](https://raw.githubusercontent.com/rebeckerspecialties/femtovg/demo-assets/pr-filter-crop.png?v=5b6e8e3)

| pixels beyond 20/255 of Chromium at the fit, 2x, 4x and 1080p | master | PR |
|---|---:|---:|
| `offset-chained-cancelling` | 2.5 / 10.0 / 33.1 / 4.2 % | 0 |
| `morphology-closing-chain` | 1.3 / 5.0 / 9.9 / 2.1 % | 0 |
| `blur-chained-quadrature` | 0.8 / 1.5 / 2.6 / 0.6 % | 0 |

Corpus, a crop after every primitive: 4,772 of 4,784 frames are bit-identical, and the 12 others are these three files. Without a crop in a chain the build renders master's frames to the bit.

### Tests

Unit tests for the plan - a crop rides the pass before it, the scale back up of a blur run down the pyramid included; two crops leave what both hold; a matrix folds across a crop only where one crop is equivalent, and never into a pass at another size - and for the rectangle a command carries: in the rows its pass stores, rounded out, cut to the image, empty when it is no rectangle. `tests/filter_chain_wgpu.rs`: a crop after a draw from an upload, from a render target, on a blur's second draw, alone and between passes, against the source inside the rectangle and nothing outside; content shifted out of the rectangle and back; a crop ahead of a blur wide enough for the pyramid, against the crop and the blur as two chains; a layer's crop in root space under a scissor. The OpenGL backend's scissor checked on the same cases behind a hidden window ([`gl_crop_check.rs`](https://github.com/rebeckerspecialties/femtovg/tree/demo-assets/harness/clip-bench)).

### Cost

No pass, and no time: over the 1,276 frames of the corpus that use a filter, each with a crop after every primitive, the frames take 60,155 render passes with and without, and 7,876 -> 7,839 ms in sum on an M4 Max (-0.5 %, within a run's noise; the median frame 0.2 % less).
