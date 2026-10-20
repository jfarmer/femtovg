Its own commits are the parity pass, the fusion, the blend's result and the changelog trim; the rest are merges of #374's branch and of master.

A filter chain spends no pass on orientation and none on a colour matrix next to a two-draw filter. Every single draw stores its result the other way up from what it read; the chain used to end with an identity pass whenever its draws were odd so the composite could read the result upright. The composite now reads it through FLIP_Y when the plan's parity says so - the flag chosen at `begin_layer`, where the mask and the blend read it the same way - and a blend-mode layer reserves a plain result only when the chain's result reads through FLIP_Y (the capture serves otherwise, as before). A colour matrix that keeps only alpha (`SourceAlpha` as a chain's start) folds into the first draw of the blur or morphology after it, and any matrix folds into the second draw of the two-draw filter before it; across a pyramid's resample passes the matrices fold into one first. The Sketch spread shadow (`SourceAlpha`, dilate, offset, blur, colour matrix) runs in four passes instead of seven; a lone blur in two instead of three.

### Evidence

Against #374 with the same harness, the 1,163-file corpus renders bit-identically on 4,600 of 4,652 frames. The frames that move are three BuseyBench portraits: a fused matrix applies to the blur's float result instead of its stored 8-bit one, which moves pixels by at most 10/255 (gpt-5-6-sol-pro at 4x, 0.04 % of pixels beyond 8/255), and two layers that no longer run out of transient room at 1080p.

| file | framing | px > 20/255, #374 -> PR | structural | max |
|---|---|---:|---:|---:|
| qwen3-8-2-4t-a95b | 1080p | 1.79 % -> 1.58 % | 1.200 % -> 1.026 % | 161 -> 161 |
| gpt-5-2-pro | 1080p | 3.43 % -> 3.23 % | 2.833 % -> 2.660 % | 146 -> 102 |
| gpt-5-6-sol-pro | 4x | 3.09 % -> 3.24 % | 0.531 % -> 0.589 % | 95 -> 95 |

#374, this PR, Chromium 131 and each build's difference from Chromium (orange 9-20/255, red beyond 20), on a chain-heavy page and the three frames that move:

![#374 and this PR against Chromium 131, each build's difference from it side by side: the enterprise page's Sketch shadows and the three frames that move](https://raw.githubusercontent.com/rebeckerspecialties/femtovg/demo-assets/pr375-chain-passes.png)

What stays red is not the chains'. The two 1080p portraits need more than the default 128 MiB transient-image budget, so layers lose their effects on both builds; with the budget lifted both builds are at 0.11 % with no structural difference (rows 3 and 5). On the third frame the band at the left is the test harness cutting a noise region short at that zoom.

### Tests

`tests/filter_chain_wgpu.rs`: the matrices fused into a blur match the separate passes (a source that is not flip-symmetric, so a lost orientation would show), and an in-place chain runs through a scratch. Unit tests pin the parity rule (a lone blur, a matrix, a matrix before a blur, two matrices), the fusion (which matrices fold where, and which do not), the reserved images per plan and that a blend-mode layer reserves its plain result for a FLIP_Y chain result.

### Cost

Steady-state frame time on an M4 Max (`FRAMES=30`, 1080p, after pipeline creation; `MEM_PEAKS=1` peak footprint), #374 -> this PR, three runs each:

| scene | frame ms | peak footprint |
|---|---:|---:|
| firefox-enterprise-browser-img (ten Sketch spread shadows) | 17.7-18.2 -> 14.1-14.6 | 1.09 GB -> 0.97 GB |
| twenty blurred cards | 18.7-19.1 -> 15.0-15.3 | 1.13 GB -> 1.01 GB |
| twenty Sketch-shadow cards | 27.8-27.9 -> 21.9-22.2 | 1.52 GB -> 1.29 GB |
| twenty colour-matrix cards | 13.3 -> 13.4 | 0.94 GB -> 0.94 GB |

A colour matrix alone was already one pass, so that page does not move; what the others save is render passes, at wgpu's per-pass cost (#368, #367). Images: a blur layer holds one transient fewer (the parity scratch); a blur layer with a blend mode holds the same five as before, since its blend result can no longer live in the capture.

