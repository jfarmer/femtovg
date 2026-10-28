<!-- Draft additions to #368's description, for Matt to review before anything is posted. -->

## Change (new paragraph, after the stencil one)

**A clear of the whole target is the pass's load op.** Every frame that begins with `clear_rect`, and every layer, shadow, mask and backdrop pass, began by loading its target and drawing a quad of the clear colour over all of it. Where no draw has begun the target's pass, no clip plane has to survive the clear and its rect covers the target, the clear is now the pass's `LoadOp::Clear`, to the premultiplied colour the quad wrote. On a tiler the quad was the expensive part: its geometry lands in every tile, so every tile was read into tile memory and shaded, where a tile the pass clears is neither. Over the corpus every clear qualifies - the 1,267 frame clears and 3,836 layer, shadow, mask and backdrop clears in 487 frames - and all 11,403 frames are bit-identical. On the 8-bit formats the load op writes the bytes the quad did (686 colours on and around 8-bit levels, unorm and sRGB, RGBA and BGRA); on `Rgba16Float` Apple GPUs round a shader's output to half toward zero and a clear value to nearest, so the clear on load is the nearer of the two by one unit in the last place.

## Evidence (new table, after the stencil table)

The clear on load on its own (this branch before and after it), on devices: Instruments' GPU intervals and GPU read and write bandwidth counters, four recordings per device in the order before, after, after, before; steady frames (each file's second and third), each frame's median over its passes and recordings, then the median frame:

| GPU time, median frame | 1080p, 17 curve-heavy files | 1080p, 5 BuseyBench portraits | 460x260, the portraits at 1x/2x/4x | 460x260, the curve files |
|---|---|---|---|---|
| iPhone XS Max (A12) | 9.81 -> 6.19 ms (-37 %) | 90.8 -> 69.3 ms (-24 %) | 30.6 -> 22.1 ms (-28 %) | 0.92 -> 0.68 ms (-26 %) |
| iPhone SE 2 (A13) | 5.04 -> 3.42 ms (-32 %) | 59.9 -> 45.3 ms (-24 %) | 19.1 -> 15.0 ms (-21 %) | 0.51 -> 0.40 ms (-22 %) |
| iPhone 12 (A14) | 5.84 -> 4.02 ms (-31 %) | 58.1 -> 47.2 ms (-19 %) | 19.7 -> 15.4 ms (-22 %) | 0.57 -> 0.45 ms (-21 %) |
| Apple TV 4K 3rd gen (A15) | 3.97 -> 2.74 ms (-31 %) | 54.0 -> 42.2 ms (-22 %) | 14.3 -> 11.8 ms (-17 %) | 0.42 -> 0.33 ms (-21 %) |
| Apple TV 4K (A10X), from the end of encoding to completion | 6.38 -> 5.36 ms (-16 %) | 65.2 -> 59.0 ms (-10 %) | 38.3 -> 37.5 ms (-2 %) | 2.49 -> 2.44 ms (-2 %) |

| GPU reads, median frame | 1080p curve files | 1080p portraits |
|---|---|---|
| A13 | 1.43 -> 0.45 MB | 67.7 -> 54.9 MB |
| A14 | 1.47 -> 0.51 MB | 61.6 -> 48.4 MB |
| A15 | 1.31 -> 0.41 MB | 59.9 -> 44.8 MB |

At 1080p writes fall 6 to 19 %. Every steady frame takes less GPU time after but one A13 portrait frame at 1080p (9 of 10); no partial renders before or after. The A12 records no bandwidth counters and the A10X no GPU intervals in Instruments 27.

Where the time goes, with a diagnostic build that can load without drawing the quad, or draw the quad over a clear on load: a frame that is only its 1080p clear took 1.31 ms of GPU time and read 0.92 MB before, and takes 0.04 ms and reads nothing after (A15 TV; A13: 1.91 -> 0.07 ms, 0.88 -> 0.06 MB). Loading the target without the quad costs next to nothing (0.02 / 0.05 ms), the quad over a clear on load 1.24 / 1.52 ms: the cost was the quad, whose geometry lands in every tile, more than the load under it (0.07 / 0.32 ms of it). Eight opacity layers of 1088x1088 on top: 19.9 -> 12.8 ms (A13: 24.4 -> 18.1 ms); their own fills cover the layers, so there loading shows too, 4.7 / 4.9 MB and 0.3 / 0.8 ms of it.

No Adreno or Mali device was available; wgpu-hal maps `LoadOp::Clear` to `VK_ATTACHMENT_LOAD_OP_CLEAR` and to a clear at the start of the pass on GLES, where `Load` is a GMEM restore per bin.

## Tests (append)

A clear of the whole target on load writes the bytes its quad would on Rgba8Unorm, Rgba8UnormSrgb, Bgra8Unorm and Bgra8UnormSrgb for 686 colours on and around 8-bit levels, within a unit on Rgba16Float, and a clear of part of the target stays a quad.

## Title (suggestion)

Skip undrawn render passes, clear on load, keep the stencil in tile memory, and submit frames in slices on WGPU
