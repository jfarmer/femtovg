Fixes #367.

## Problem

wgpu opens a Metal command buffer for every render pass of a `CommandEncoder` and commits them together at submit (gfx-rs/wgpu#5738; the standalone reproducer in gfx-rs/wgpu#10494 was closed as its duplicate), and the driver keeps about 2.3 MiB for each until it completes: 800 empty passes on one encoder hold 1,841 MiB in wgpu and 25 MiB as encoders inside one command buffer in pure Metal. A femtovg frame's driver memory therefore grows with its render passes, 2.30 MiB each at the median over 122 corpus frames of more than 100 passes. 1,600 opacity layers failed buffer creation on an M4 Max (`Buffer with '' label is invalid`), and a 176-layer BuseyBench portrait at 460x260 was jetsammed on an iPhone 12 at the 2.2 GiB per-process limit. RSS shows none of it: the memory is graphics-tagged, visible to `footprint(1)`, the task ledgers and jetsam, not to `ru_maxrss`.

## Change

**A render pass begins with its first draw.** Setting a render target began a pass at once, so a target that was set and left again undrawn got one that loaded and stored it for nothing: the target every image filter hands back before the next switch, and the screen ahead of a frame's first switch. That was 28 % of the passes of the BuseyBench frames (849 to 632 for the 178-layer portrait) and 34 % of everything else's. No API and no pixel change; it applies to every frame.

**`WGPURenderer::set_submission_slicing(Some(SubmissionSlicing { passes }))`** submits the frame in slices: the encoder is submitted before the render pass that would exceed `passes` begins, wherever that pass comes from (a layer, a blur chain, a clear), so each submission holds at most that many command buffers and the driver recycles the ones that complete while the rest of the frame is encoded. Default 64 passes. The renderer never polls the device: each slice's submit, like the caller's own, only fires the callbacks of work that has already completed (`device.maintain(Poll)` in `Queue::submit`).

Slicing is off by default, which keeps the one-command-buffer contract of `flush_to_output` / `flush_to_surface`. On, the slices before the returned command buffer are submitted during the flush, so a command buffer the caller submits together with the tail runs after them: work that must precede the frame is submitted before the flush. The docs say so and a test pins it. `Canvas::renderer` / `renderer_mut` reach the renderer; `WGPURenderer::last_frame_slices` reports the passes per command buffer of the last frame, which the tests assert.

Slicing lowers the peak without bounding it. Nothing waits for a slice, so an encoder ahead of the GPU still accumulates unfinished ones: the sliced frames below hold between a quarter and all of the unsliced driver memory, 60 % at the median. A bound takes back-pressure, which this renderer does not apply (the last table column is a build with the wait that was removed here), or the fix in wgpu. That fix is in review as gfx-rs/wgpu#10506: with it under femtovg master the worst frame below holds 522 MiB and the soak 604 MiB, pixels identical. Until a wgpu release with it is what femtovg depends on, this PR is the mitigation; the pass change stays worth having after, since a pass that draws nothing still loads and stores its target.

## Evidence

![peak footprint of the 27 BuseyBench portraits under master, this PR, and this PR with slicing on](https://raw.githubusercontent.com/rebeckerspecialties/femtovg/demo-assets/submission-slices-corpus.png)

The whole corpus on an M4 Max: 711 files (the demo-assets corpus, 300 SVGenius icons, the Ghostscript tiger) at 460x260 under 1x, 2x and 4x zoom and at 1920x1080, one process per frame, peak footprint sampled from the task ledgers. All 2,844 frames are bit-identical between master before #369, master, and this branch with slicing on and off. About 445 MiB of every figure is a pool the driver grows for any first frame, a single rectangle included.

| peak footprint, MiB, median / max | master | this PR | this PR, slicing on | slicing + the removed wait |
|---|---|---|---|---|
| 27 BuseyBench portraits, 460x260 | 1,447 / 4,063 | 1,169 / 2,898 | 895 / 1,106 | 881 / 929 |
| the same at 1920x1080 | 1,727 / 4,192 | 1,433 / 3,061 | 1,044 / 1,453 | 985 / 1,063 |
| the other 684 files, 460x260 | 460 / 772 | 458 / 663 | 458 / 661 | |
| render passes per frame, BuseyBench | 390 / 1,453 | 312 / 991 | | |
| render passes per frame, the other files | 2 / 370 | 1 / 245 | | |

| soak: every file x 3 zooms x 3 passes on one canvas | master | this PR | this PR, slicing on |
|---|---|---|---|
| peak footprint | 4,288 MiB | 3,103 MiB | 1,425 MiB |
| wall time | 17.0 s | 13.8 s | 11.2 s |
| frame p50 / p99 / max, ms | 0.50 / 48.9 / 200 | 0.47 / 32.9 / 161 | 0.47 / 23.2 / 52 |

Outside BuseyBench the median frame is one pass and nothing changes for it; 14 frames still exceed 64 passes, all blur reftests and probes under zoom. Unsliced peaks repeat within 0.1 %, sliced ones within 2 % at the median and 18 % at worst. The transient budget passes layers through on the same 36 frames in every build (BuseyBench under zoom, three shadow probes at 4x). Method, per-framing tables and scripts: [corpus run report](https://github.com/rebeckerspecialties/femtovg/blob/demo-assets/harness/submission-slices-corpus-2026-10-02.md).

Synthetic frames and the phone, measured with slices alone, before passes were made lazy:

![driver memory per frame and the phone outcome](https://raw.githubusercontent.com/rebeckerspecialties/femtovg/demo-assets/submission-slices-footprint.png)

| iPhone 12, efficiency cores, full corpus | one submission | sliced |
|---|---|---|
| the five files that exceeded the 2.2 GiB limit | killed | 187-404 ms at 1x |
| the other 194 files (582 frames), wall p50 / p95 / p99 / max, ms | 4.1 / 173 / 357 / 1,534 | 3.2 / 117 / 194 / 244 |

## Tests

A frame of fills is one pass, an opacity layer three, and a blur into a colour matrix that nothing draws afterwards five: no pass for a target left undrawn. 63/64/65-pass frames slice as `[63]`, `[64]`, `[64, 1]`; 320 one-pixel layers land with their own colours across eleven slices; a mixed scene (nested layers under a rotated scissor, an armed path clip, an image target drawn and restored, blur into colour matrix, a masked multiply layer) renders identically in slices of 1, 3, 4, 7 and 13 passes; the prepass order with and without slicing; and on macOS a child process measures the footprint of the 176-layer portrait in one submission and sliced, and asserts that slicing never costs memory, which also holds on a wgpu with the fix (490 against 492 MiB there).

