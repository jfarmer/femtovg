Fixes #367.

## Problem

wgpu opens a Metal command buffer for every render pass of a `CommandEncoder` and commits them together at submit (gfx-rs/wgpu#5738; the standalone reproducer in gfx-rs/wgpu#10494 was closed as its duplicate), and the driver keeps about 2.3 MiB for each until it completes: 800 empty passes on one encoder hold 1,841 MiB in wgpu and 25 MiB as encoders inside one command buffer in pure Metal. A femtovg frame's driver memory therefore grows with its render passes, 2.30 MiB each at the median over 122 corpus frames of more than 100 passes. 1,600 opacity layers failed buffer creation on an M4 Max (`Buffer with '' label is invalid`), and a 176-layer BuseyBench portrait at 460x260 was jetsammed on an iPhone 12 at the 2.2 GiB per-process limit. RSS shows none of it: the memory is graphics-tagged, visible to `footprint(1)`, the task ledgers and jetsam, not to `ru_maxrss`.

One submission costs time too. Past a number of passes in one command buffer that falls with the stencil textures they attach (the backend gives each image it renders into its own) - about 800 with up to 23, 444 with 24 to 43, 234 with more - every further pass takes four page faults while the GPU runs the frame. On master 30 of the 108 BuseyBench portrait frames take more than 100, 39,311 in all.

## Change

**A render pass begins with its first draw.** Setting a render target began a pass at once, so a target that was set and left again undrawn got one that loaded and stored it for nothing: the target every image filter hands back before the next switch, and the screen ahead of a frame's first switch. That was 28 % of the passes of the BuseyBench frames (849 to 632 for the 178-layer portrait) and 34 % of everything else's. No API and no pixel change; it applies to every frame.

**A pass attaches the stencil only when it draws with it, and keeps it in tile memory.** Every pass on a canvas or layer target attached the target's Stencil8 with `LoadOp::Load` and `StoreOp::Store`. On a tiler (Apple, Adreno, Mali) that reads the whole stencil into tile memory as the pass begins and writes it back as it ends, every pass, and an attached stencil takes tile memory - on Adreno, GMEM per bin - whether the pass draws with it or not. The only stencil content one pass should hand another is a clip plane armed on the target: a concave fill or a stencil stroke zeroes the winding it counts. So a pass now looks at what it will draw before it begins (wgpu fixes the store op then; a pass ends at the next target change or filter). If none of its commands tests or writes the stencil it attaches none; otherwise it clears the stencil on load unless a plane is armed as it begins, and discards it on store unless one is armed as it ends. A target's stencil texture is made by the first pass that needs one. Over the corpus a third of the passes on drawable targets attach a stencil and none loads or stores it, 696 of 1,196 frames attach none, and the most distinct stencils one flush attaches - what sets the fault allowance above - falls from 78 to 45.

**`WGPURenderer::set_submission_slicing(Some(SubmissionSlicing { passes }))`** submits the frame in slices: the encoder is submitted before the render pass that would exceed `passes` begins, wherever that pass comes from (a layer, a blur chain, a clear), so each submission holds at most that many command buffers and the driver recycles the ones that complete while the rest of the frame is encoded. Default 64 passes. The renderer never polls the device: each slice's submit, like the caller's own, only fires the callbacks of work that has already completed (`device.maintain(Poll)` in `Queue::submit`).

Slicing is off by default, which keeps the one-command-buffer contract of `flush_to_output` / `flush_to_surface`. On, the slices before the returned command buffer are submitted during the flush, so a command buffer the caller submits together with the tail runs after them: work that must precede the frame is submitted before the flush. The docs say so and a test pins it. `Canvas::renderer` / `renderer_mut` reach the renderer; `WGPURenderer::last_frame_slices` reports the passes per command buffer of the last frame, which the tests assert.

Slicing lowers the peak without bounding it. Nothing waits for a slice, so an encoder ahead of the GPU still accumulates unfinished ones: the sliced frames below hold between a quarter and all of the unsliced driver memory, 60 % at the median. A bound takes back-pressure, which this renderer does not apply (a build with the wait that was removed here held 881 / 929 MiB on the portraits in the first run), or the fix in wgpu. That fix is in review as gfx-rs/wgpu#10506: with it under femtovg master the worst portrait frame held 522 MiB and the soak 604 MiB, pixels identical. Until a wgpu release with it is what femtovg depends on, this PR is the mitigation; the pass change stays worth having after, since a pass that draws nothing still loads and stores its target.

## Evidence

Measured again with master 9f5ad26 merged in, on an M4 Max: the 1,267-file corpus (the demo-assets corpus and its WPT reftests, 300 SVGenius icons, 66 Babylon.js canvases, the Ghostscript tiger) at 460x260 under 1x, 2x and 4x zoom and at 1920x1080. All 5,068 frames are bit-identical between master and this branch with slicing on and off, and the 1,360 frames of files with a filter also in slices of one pass. A portrait frame is 274 passes at the median and 950 at most; outside BuseyBench a frame is one pass at the median, and four exceed 64.

| steady-state frame time, summed (`FRAMES=20` after pipeline creation, builds alternating) | before | after | |
|---|---:|---:|---:|
| 108 portrait frames, master -> this PR sliced (three runs) | 4,893 ms | 2,523 ms | -48 %, every frame -15 to -67 % |
| the same, this PR unsliced -> sliced (three runs) | 3,972 ms | 2,614 ms | -34 % |
| all 5,068 frames, master -> this PR sliced (two runs) | 17,044 ms | 14,132 ms | -17 %, median frame -2.3 % |

The stencil change, measured on its own (this branch before and after it, the same way):

| steady-state frame time, summed | before | after | |
|---|---:|---:|---:|
| 27 portraits at 1x and 4x, sliced | 1,156 ms | 1,113 ms | -3.8 %, no frame more than 2 % slower |
| the same, unsliced | 1,390 ms | 1,342 ms | -3.4 % |
| 60 random files outside BuseyBench at 1x | 79 ms | 76 ms | -4.0 %, median frame -3.0 % |

Over 11,403 frames (the 1,267 files at nine framings, 1/10x to 1080p) it changes 14 pixels in 9 frames, all below 1x: where a concave fill's cover missed part of the winding it counted - a feature thinner than a pixel - the count no longer reaches the next pass, where the next fill painted it. 11 of the 14 move toward the exact-area reference. #404 stops the cover missing that count in the first place.

The harness waits for each frame, so slices save time two ways: the GPU starts on the first slices while the rest of the frame is encoded - the 92 portrait frames that take no page faults unsliced gain 29 %, less than their encoding time - and no command buffer reaches the fault allowance - the 16 that do gain 46 %, more than their encoding. Sliced, one frame takes more than 100 faults (576 in all, against 16,564 unsliced). An application that encodes a frame while the GPU runs the previous one already has part of the first saving. The 12 frames of 1 to 4 ms that read more than 5 % slower in both runs look like noise: five timed again in seven alternating runs measured -4.7 to +1.1 %.

| peak footprint, MiB, median / max, one process per frame | master | this PR | this PR, slicing on |
|---|---|---|---|
| 27 BuseyBench portraits, 460x260 at 1x, 2x, 4x | 1,372 / 3,766 | 1,172 / 2,785 | 898 / 1,083 |
| the same at 1920x1080 | 1,584 / 4,094 | 1,332 / 3,017 | 1,010 / 1,230 |

About 445 MiB of every figure is a pool the driver grows for any first frame, a single rectangle included. The figure, the soak and the phone are from the first run (master 6a5f15a, 711 files, every frame bit-identical then too; method and scripts in the [corpus run report](https://github.com/rebeckerspecialties/femtovg/blob/demo-assets/harness/submission-slices-corpus-2026-10-02.md)):

![peak footprint of the 27 BuseyBench portraits under master, this PR, and this PR with slicing on](https://raw.githubusercontent.com/rebeckerspecialties/femtovg/demo-assets/submission-slices-corpus.png)

| soak: every file x 3 zooms x 3 passes on one canvas | master | this PR | this PR, slicing on |
|---|---|---|---|
| peak footprint | 4,288 MiB | 3,103 MiB | 1,425 MiB |
| wall time | 17.0 s | 13.8 s | 11.2 s |
| frame p50 / p99 / max, ms | 0.50 / 48.9 / 200 | 0.47 / 32.9 / 161 | 0.47 / 23.2 / 52 |

Synthetic frames and the phone, measured with slices alone, before passes were made lazy:

![driver memory per frame and the phone outcome](https://raw.githubusercontent.com/rebeckerspecialties/femtovg/demo-assets/submission-slices-footprint.png)

| iPhone 12, efficiency cores, full corpus | one submission | sliced |
|---|---|---|
| the five files that exceeded the 2.2 GiB limit | killed | 187-404 ms at 1x |
| the other 194 files (582 frames), wall p50 / p95 / p99 / max, ms | 4.1 / 173 / 357 / 1,534 | 3.2 / 117 / 194 / 244 |

## Tests

A frame of fills is one pass, an opacity layer three, and a blur into a colour matrix that nothing draws afterwards five: no pass for a target left undrawn. 63/64/65-pass frames slice as `[63]`, `[64]`, `[64, 1]`; 320 one-pixel layers land with their own colours across eleven slices; a mixed scene (nested layers under a rotated scissor, an armed path clip, an image target drawn and restored, blur into colour matrix, a masked multiply layer) renders identically in slices of 1, 3, 4, 7 and 13 passes; the prepass order with and without slicing; and on macOS a child process measures the footprint of the 176-layer portrait in one submission and sliced, and asserts that slicing never costs memory, which also holds on a wgpu with the fix (490 against 492 MiB there). A unit test pins which commands take the stencil and what an armed plane keeps across passes, and a debug assertion that no stencil draw lands in a pass without a stencil held over the tests and the 11,403 corpus frames.




