A WGPU frame's uploads (vertices, fan indices, uniforms and image updates) went through `Queue::write_buffer` and `Queue::write_texture`, which wgpu runs before the next command buffer submitted, whichever frame it belongs to: a frame flushed before the previous one was submitted overwrote the data the previous one draws with, and every call allocated a staging buffer of its own. The uploads now go through a `wgpu::util::StagingBelt` and are copied at the start of the frame's own command buffer, in the order they were made; an image upload larger than a megabyte has a buffer of its own, and an image with mipmaps is still written at once. The viewport uniform and bind group of each target size are kept across flushes, the least recently used let go past 128, instead of being made again for every pass that changes size.

**Evidence.** All 11,403 corpus frames render as on master.

| | change |
|---|---|
| encode, layer-heavy BuseyBench pages (kimi-k2-6, gemini-3-1-pro-preview) | -21 to -25 % |
| encode, draw-heavy pages | -2.7 to -6.7 % |
| encode / instructions, a page of full-screen fills | -15 % / -9.8 % |
| #408's thin-fill masks in motion (an atlas update every frame), diners at 1080p, M4 efficiency cores, cycles a frame over the masks off | +52 % -> +25 % |
| the same over eight thin-fill files, iPhone 16 Pro Max efficiency cores: render-thread cycles / process energy | +7.2 / +3.6 % -> +2.6 / +2.5 % |

**Tests:** `frames_flushed_before_a_submit_each_draw_their_own` and `..._draw_the_image_they_were_given` fail on master; `an_upload_larger_than_a_staging_chunk_keeps_its_place_in_order` fails with only small uploads staged; the viewport bind groups' lifetime and eviction. 566 pass.

**Cost:** the belt keeps its chunks (a megabyte, or a frame's uploads) for each frame in flight: +1.5 to 3.6 MiB on ordinary pages; the 65,538-command Babylon page keeps 80 MiB more graphics memory, though its peak footprint falls (1,634 -> 1,545 MiB). wgpu's `std` feature is now asked for: the belt needs it, and a library build for the web did not get it otherwise.
