## Problem

Under a clip taken as a coverage mask (#390), a composite operation that coverage cannot bound - `Copy`, `SourceIn`, `SourceOut`, `DestinationIn`, `DestinationAtop` - takes the mask whole or not at all: each draw discards the pixels the mask covers by less than half. A concave fill's cover did, but its winding pass carried no mask and counted there anyway. A discarded fragment keeps its stencil, so the count outlived the fill, and the next concave fill whose cover reached those pixels painted them outside its own shape. Both backends, within the clip's bounds.

## Change

The winding pass reads the same mask when it is hard (`Params::with_hard_clip_mask`), so it discards the pixels its cover discards and counts nothing there. A soft mask discards nothing and stays off the winding pass.

## Evidence

The reftest suite's 13 canvas scenes (`18-hard-mask-composite-concave-winding/scenes_hard_mask.json`: a clip, one of the operations, a concave L reaching past the clip, then a concave U whose cover takes in part of the L outside it) on Chromium 131, Firefox 159 and WebKit (macOS 27.2) canvases at 1x, 2x and 4x, and with femtovg master ad762cd5 against this PR. The three browsers draw every scene within 20 levels of each other, so the reference column below is Chromium's; red marks pixels more than 20 levels off it:

![master, this PR, Chromium, and each against Chromium: the five operations this PR moves, the star clip, and two controls](https://raw.githubusercontent.com/rebeckerspecialties/femtovg/demo-assets/pr-hard-mask-winding-3.png)

| pixels more than 20 off the browser, WGPU | Chromium | Firefox | WebKit |
|---|---:|---:|---:|
| 1x, 13 scenes | 1,677 -> 162 | 1,677 -> 162 | 1,682 -> 168 |
| 2x | 5,733 -> 324 | 5,733 -> 324 | 5,742 -> 334 |
| 4x | 20,978 -> 650 | 20,978 -> 650 | 20,991 -> 664 |

Every pixel this PR changes moves toward all three browsers, on both backends at every scale; none moves away. The scenes it moves are copy, source-out and destination-atop (216 -> 30 each at 1x), source-in and destination-in (186 -> 0), and the star clip (657 -> 72); the other seven are 0 before and after. What is left is the hard mask's whole-or-nothing edge, the same before. OpenGL counts 1,722 -> 162 at 1x (5,818 -> 324, 21,143 -> 650) and now draws the scenes pixel for pixel as WGPU does, where master's leaks differed between the backends by 9 to 33 pixels ([OpenGL strip](https://raw.githubusercontent.com/rebeckerspecialties/femtovg/demo-assets/pr-hard-mask-winding-gl-3.png), [4x](https://raw.githubusercontent.com/rebeckerspecialties/femtovg/demo-assets/pr-hard-mask-winding-3-4x.png)).

None of the corpus's 12,690 frames (1,269 files at ten framings, from a tenth of the fit to 4x, 1080p and 240p) and none of the reftest suite's 7,800 (390 pairs of groups 01-22, both files, the same framings) changes: SVG puts no compositing operator on a shape, so neither fills a concave path under a hard mask.

**Cost.** Content without a hard mask runs the same code, one `Option::filter` a concave fill more. Ten corpus files at 1080p in motion on an M4 Max's efficiency cores, the process's instructions and cycles a frame (a 250-frame run less a 50-frame one), median of five alternating rounds:

| file, 1080p, moving | instructions a frame | this PR: instructions | cycles |
|---|---:|---:|---:|
| firefox/diners | 6.85 M | -0.3 % | -2.4 % |
| tiger | 28.5 M | -0.1 % | -0.1 % |
| banner (SolidJS) | 30.2 M | -0.1 % | -3.7 % |
| buseybench/kimi-k2-6 (clip paths) | 221 M | -0.0 % | -0.1 % |
| buseybench/gemini-3-1-pro-preview-custom-tools (clip paths) | 526 M | +0.3 % | +0.4 % |
| babylon/dynamic-texture-context-clip | 2.14 M | +3.6 % | -1.9 % |
| babylon/show-multiple-guis | 27.8 M | -0.5 % | -3.6 % |
| babylon/pointers | 4.55 M | +0.0 % | -4.3 % |
| nyt/enterprise-nyt-evenodd | 1.36 M | +0.1 % | -3.2 % |
| firefox-com/Kit_Keyhole_Landscape_Light | 6.45 M | -0.3 % | +1.0 % |

The same master binary run twice moves by as much (dynamic-texture-context-clip, a 2 M-instruction frame: +2.7 % / -3.2 %; gemini: +0.0 % / -0.7 %), and the build run second in a round tends to come out a few percent lower in cycles. Peak footprint is within 2.5 MiB on nine files (banner 630 -> 615 MiB). Under a hard mask the winding pass and the cover now carry the same mask, so on WGPU they share one bind group where the backend made a new one for each pass of every fill: a 1080p frame of 400 concave fills under a star clip with `source-in` takes 15.7 M instructions and 6.5 M cycles of the render thread where master takes 30.4 M and 13.5 M (-48 % and -52 %; 11.8 -> 5.7 ms a frame, efficiency cores, five alternating rounds). With `source-over` (a soft mask) it is 30.4 M on both, and with no clip 15.2 M against 15.4 M, inside the rounds' 1.5 % spread. The soft mask's doubling - the winding pass carries no mask, so the bind group still changes twice a fill - is outside this PR.

The scenes, the scripts that draw them in each browser (`scenes_browser.py`), at each scale (`SCENES_SCALE`) and with each backend, and the bench are in [demo-assets](https://github.com/rebeckerspecialties/femtovg/tree/demo-assets/harness/hard-mask-scenes).

## Tests

`a_concave_fill_under_a_whole_or_nothing_mask_leaves_no_winding_behind` in `tests/clip_mask_wgpu.rs` draws the L and the U under `Copy`, `SourceIn` and `DestinationIn` and checks that the U's gap stays white; on master it is blue. 577 tests pass.
