Its own commits are the parity pass, the fusion, the blend's result, the changelog trim and the noise's orientation; the rest are merges of #374's branch and of master.

A filter chain spends no pass on orientation and none on a colour matrix next to a two-draw filter. Every single draw stores its result the other way up from what it read; the chain used to end with an identity pass whenever its draws were odd so the composite could read the result upright. The composite now reads it through FLIP_Y when the plan leaves it stored that way - the flag chosen at `begin_layer`, where the mask and the blend read it the same way - and a blend-mode layer reserves a plain result only when the chain's result reads through FLIP_Y (the capture serves otherwise, as before). The turbulence generator reads nothing, so it sets the orientation outright instead of turning its source's over; a layer whose chain starts with it drew its noise upside down on master. A colour matrix that keeps only alpha (`SourceAlpha` as a chain's start) folds into the first draw of the blur or morphology after it, and any matrix folds into the second draw of the two-draw filter before it; across a pyramid's resample passes the matrices fold into one first. The Sketch spread shadow (`SourceAlpha`, dilate, offset, blur, colour matrix) runs in four passes instead of seven; a lone blur in two instead of three.

### Evidence

Rendering does not change. Against master with the same harness the 1,183-file corpus is bit-identical on 4,726 of 4,732 frames; the six that move (the enterprise page at each framing, one portrait at two) differ by at most 2/255, where a fused matrix applies to a filter's float result instead of its stored 8-bit one, and none moves by more than 0.004 points of pixels beyond 8/255 from Chromium or Firefox.

master, this PR, Chromium 131 and each build's difference from Chromium (orange 9-20/255, red beyond 20):

![master and this PR against Chromium 131, each build's difference from it side by side: the enterprise page's Sketch shadows, a noise chain and a portrait of blurred layers](https://raw.githubusercontent.com/rebeckerspecialties/femtovg/demo-assets/pr375-chain-passes.png)

### Tests

`tests/filter_chain_wgpu.rs`: the matrices fused into a blur match the separate passes (a source that is not flip-symmetric, so a lost orientation would show), and an in-place chain runs through a scratch. `tests/turbulence_wgpu.rs`: a noise chain of one, two and three draws against the specification's reference from an upload, from a render-target image, in place and as a layer's chain, into targets read either way. Unit tests pin how a plan leaves its image stored (a lone blur, a matrix, a matrix before a blur, two matrices, noise before and after a matrix), the fusion (which matrices fold where, and which do not), the reserved images per plan and that a blend-mode layer reserves its plain result for a FLIP_Y chain result.

### Cost

Steady-state frame time on an M4 Max (`FRAMES=30`, 1080p, after pipeline creation; `MEM_PEAKS=1` peak footprint), master -> this PR, three runs each:

| scene | frame ms | peak footprint |
|---|---:|---:|
| firefox-enterprise-browser-img (ten Sketch spread shadows) | 17.7-18.2 -> 14.1-14.6 | 1.09 GB -> 0.97 GB |
| twenty blurred cards | 18.7-19.1 -> 15.0-15.3 | 1.13 GB -> 1.01 GB |
| twenty Sketch-shadow cards | 27.8-27.9 -> 21.9-22.2 | 1.52 GB -> 1.29 GB |
| twenty colour-matrix cards | 13.3 -> 13.4 | 0.94 GB -> 0.94 GB |

A colour matrix alone was already one pass, so that page does not move; what the others save is render passes, at wgpu's per-pass cost (#368, #367). Images: a blur layer holds one transient fewer (the parity scratch); a blur layer with a blend mode holds the same five as before, since its blend result can no longer live in the capture.
