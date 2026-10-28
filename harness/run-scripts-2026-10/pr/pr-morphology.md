Builds on #373; its own commits are the ones after #373's.

Adds `ImageFilter::Morphology` and `ImageFilter::Offset`, the SVG `feMorphology` and `feOffset` primitives. A dilation grows the opaque regions of an image by a whole-pixel radius per axis and an erosion shrinks them: the per-channel maximum or minimum within the radius, run as two draws along the axes through the scratch the blur uses, a radius above the 24 pixels one draw covers running as passes whose radii sum to it, which is exact for the rectangle. An offset shifts the image by a device-pixel vector, sampling transparent beyond its edge; a zero one folds away as the identity. A layer pads its store by a morphology's radius - a dilation reaches that far out, an erosion reads that far beyond the store to erode its edge rightly instead of into the transparent outside - and by an offset's shift, as it does by a blur's reach. Radii round to whole device pixels as Skia rounds them (Gecko takes the ceiling).

The motive is the spread shadow Sketch exports on every `<use>` it shadows: `feMorphology dilate` on `SourceAlpha`, `feOffset`, `feGaussianBlur`, `feColorMatrix`, with the shape drawn by a second `<use>`. With `SourceAlpha` as a color matrix that keeps alpha, that chain is one layer filter.

### Evidence

Chromium 131 references at the harness's four framings (460x260 at 1x, 2x, 4x; 1080p): pixels beyond 20/255 of the frame, and the structural share after a 2 px erosion. Against #373 with the same harness, the 763-file corpus renders bit-identically on 3,046 of 3,052 frames: the four frames of the one corpus file whose chains the primitives complete, below, and two BuseyBench frames that differ by at most 0.003 points at 8/255.

![firefox-enterprise-browser-img, a Sketch export from firefox.com: #373, this PR, Chromium 131, and the differences against Chromium (red beyond 20/255, orange 8-20)](https://raw.githubusercontent.com/rebeckerspecialties/femtovg/demo-assets/morphology-evidence.png)

| file | framing | px > 20/255, #373 -> PR | structural | max |
|---|---|---:|---:|---:|
| firefox-enterprise-browser-img (10 shadows, dilate 0.5-1, sigma 4-7.5) | 1x | 1.40 % -> 0.31 % | 0.003 % -> 0.003 % | 175 -> 175 |
| | 2x | 3.55 % -> 0.10 % | 0.000 % -> 0.000 % | 107 -> 107 |
| | 4x | 3.76 % -> 0.10 % | 0.385 % -> 0.000 % | 119 -> 119 |
| | 1080p | 1.47 % -> 0.01 % | 0.640 % -> 0.000 % | 123 -> 123 |

What remains at 1x is the file's thin icon geometry (#358's subject), as before.

On an extracted reftest suite (test/reference pairs modelled on WPT `filter-effects` and the resvg filter tests, Chromium 131 as the arbiter at the same four framings), 48 of the 50 `feOffset` pairs and 47 of the 50 `feMorphology` pairs render within 0.15 % of pixels at every framing, 19 of the erode pairs pixel-exact once a layer padded its store for an erosion as for a dilation. The five that do not are not the primitives': two chains whose intermediates Chromium clips to the primitive subregion (`offset-chained-cancelling`, `morphology-closing-chain`), usvg reading a zero radius on one axis as one user pixel (`morphology-erode-*-only`, 0.5-0.7 % at 4x), and the filter region of a stroked shape (`offset-border-stroke-fill`, 1.5 % at 4x).

### Tests

`tests/morphology_offset_wgpu.rs`: a dilation grows a square by its radius on every side and an erosion shrinks it, to the pixel and with no fringe, per axis, across the per-draw bound (radius 30 as 24 and 6) and with rounding; an offset moves it whichever way up its source is stored - from an upload, after a color-matrix pass, in a layer, in the single pass - and a half-pixel shift lands between pixels; an erosion eats into the image border; and the Sketch chain in a layer renders the spread shadow alone. Unit tests pin the plan (whole pixels, per-axis split, parity, the zero offset folding), the work, the scratch, the chain reach (an erosion's as a dilation's) and the layer padding. 446 GPU and unit tests pass; fmt and clippy clean; the GLSL validates with glslangValidator for every shader variant.

### Cost

A morphology draw taps `2 r + 1` pixels per axis, the blur's loop with min/max in place of weights, and reserves the blur's scratch; an offset is one tap. Blur-only chains plan and render as before: the refactor that lets both drive the two-draw path is covered by the bit-identical corpus. What the shadows cost is passes, not samples: on the enterprise file at 1080p on an M4 Max, the steady-state frame (`FRAMES=30`, after pipeline creation) goes from 3.4 to 18.3 ms for ten shadow chains of seven passes each (the alpha matrix, two morphology draws, two blur draws, the colour matrix and the parity identity), about 0.2 ms per render pass whatever its size, which is wgpu's per-pass cost (#368, wgpu#10506). A synthetic page of twenty such cards measures 31 ms, twenty blur-only groups 21 ms and twenty colour-matrix groups 16 ms, so the lever is passes per chain; folding the matrices into the two-pass draws and dropping the parity pass takes this chain from seven to four, which is #375.
