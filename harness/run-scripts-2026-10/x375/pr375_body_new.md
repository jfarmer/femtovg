Its own commits are the parity pass, the fusion, the blend's result, the changelog trim and the noise's orientation; the rest are merges of #374's branch and of master.

A filter chain spends no pass on orientation and none on a colour matrix next to a two-draw filter. Every single draw stores its result the other way up from what it read; the chain used to end with an identity pass whenever its draws were odd so the composite could read the result upright. The composite now reads it through FLIP_Y when the plan leaves it stored that way - the flag chosen at `begin_layer`, where the mask and the blend read it the same way - and a blend-mode layer reserves a plain result only when the chain's result reads through FLIP_Y (the capture serves otherwise, as before). The turbulence generator reads nothing, so it sets the orientation outright instead of turning its source's over; a layer whose chain starts with it drew its noise upside down on master. A colour matrix that keeps only alpha (`SourceAlpha` as a chain's start) folds into the first draw of the blur or morphology after it, and any matrix folds into the second draw of the two-draw filter before it; across a pyramid's resample passes the matrices fold into one first. The Sketch spread shadow (`SourceAlpha`, dilate, offset, blur, colour matrix) runs in four passes instead of seven; a lone blur in two instead of three.

### Evidence

Rendering does not change, so the evidence is time. Against master with the same harness the 1,183-file corpus is bit-identical on 4,726 of 4,732 frames; the six that move (the enterprise page at each framing, one portrait at two) differ by at most 2/255, where a fused matrix applies to a filter's float result instead of its stored 8-bit one.

Steady-state frame time summed over every corpus frame that uses a filter - 319 files at four framings, 1,276 frames - master -> this PR, on an M4 Max (`FRAMES=20` after pipeline creation, the builds alternating, [`pass_time.py`](https://github.com/rebeckerspecialties/femtovg/blob/demo-assets/harness/corpus_run/pass_time.py)):

| frames | master | this PR | saved |
|---|---:|---:|---:|
| all 1,276 | 7,345 ms | 6,603 ms | 742 ms (10.1 %) |
| 460 x 260 at the fit (319) | 1,680 ms | 1,497 ms | 10.9 % |
| at 2x (319) | 1,778 ms | 1,592 ms | 10.5 % |
| at 4x (319) | 1,758 ms | 1,597 ms | 9.2 % |
| 1080p (319) | 2,129 ms | 1,917 ms | 10.0 % |
| the 27 portraits of blurred layers (108) | 4,769 ms | 4,107 ms | 13.9 % |
| blur reftests (372) | 776 ms | 743 ms | 4.2 % |
| morphology reftests (200) | 432 ms | 409 ms | 5.3 % |
| offset reftests (200) | 363 ms | 363 ms | 0.0 % |

Two files cost more, each checked again on its own (seven alternating runs, spread under 6 %). A reftest that runs one identity matrix over an image in place is 0.23 ms slower at each framing: master refuses a single-draw chain whose source is its target (`RenderTargetError`), and here it runs through a scratch, two passes. One portrait is 9 % slower between 3x and 4.5x (53 -> 58 ms at 4x) and 12 to 17 % faster at the fit, 2x, 6x and 1080p; at 4x it issues a hundred passes fewer than master's 734, but a lone blur's result now has its capture's size and flags, so sibling layers swap the two in the transient pool and 33 images are drawn into instead of 22, each with its own stencil texture; once a command buffer holds 24 or more, the Metal driver takes four page faults for every pass past its 444th rather than its 800th or so, 780 faults and about 11 ms at 4x, while at the fit and 2x the frame stays under 24 and from 6x master reaches 24 too. The other 107 portrait frames are faster, by up to 32 %.

### Tests

`tests/filter_chain_wgpu.rs`: the matrices fused into a blur match the separate passes (a source that is not flip-symmetric, so a lost orientation would show), and an in-place chain runs through a scratch. `tests/turbulence_wgpu.rs`: a noise chain of one, two and three draws against the specification's reference from an upload, from a render-target image, in place and as a layer's chain, into targets read either way. Unit tests pin how a plan leaves its image stored (a lone blur, a matrix, a matrix before a blur, two matrices, noise before and after a matrix), the fusion (which matrices fold where, and which do not), the reserved images per plan and that a blend-mode layer reserves its plain result for a FLIP_Y chain result.

### Cost

The same measure on three pages built for it and on the enterprise page, at 1080p with peak footprint (`FRAMES=30`, `MEM_PEAKS=1`), master -> this PR, three runs each:

| scene | frame ms | peak footprint |
|---|---:|---:|
| firefox-enterprise-browser-img (ten Sketch spread shadows) | 17.7-18.2 -> 14.1-14.6 | 1.09 GB -> 0.97 GB |
| twenty blurred cards | 18.7-19.1 -> 15.0-15.3 | 1.13 GB -> 1.01 GB |
| twenty Sketch-shadow cards | 27.8-27.9 -> 21.9-22.2 | 1.52 GB -> 1.29 GB |
| twenty colour-matrix cards | 13.3 -> 13.4 | 0.94 GB -> 0.94 GB |

A colour matrix alone was already one pass, so that page does not move; what the others save is render passes, at wgpu's per-pass cost (#368, #367). Images: a blur layer holds one transient fewer (the parity scratch); a blur layer with a blend mode holds the same five as before, since its blend result can no longer live in the capture.

