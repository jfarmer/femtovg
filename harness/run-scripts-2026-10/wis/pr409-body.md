A WGPU frame's uploads (vertices, fan indices, uniforms and image updates) went through `Queue::write_buffer` and `Queue::write_texture`, which wgpu runs before the next command buffer submitted, whichever frame it belongs to: a frame flushed before the previous one was submitted overwrote the data the previous one draws with, and every call allocated a staging buffer of its own. The uploads now go through a `wgpu::util::StagingBelt` and are copied at the start of the frame's own command buffer, in the order they were made; an image upload larger than a megabyte has a buffer of its own, and an image or canvas element on the web is copied by the queue into a texture of its own and from there in the same order. An image with mipmaps, or one wrapping a texture of the caller's (`create_image_from_native_texture`), is still written at once. The viewport uniform and bind group of each target size are kept across flushes, the least recently used let go past 128, instead of being made again for every pass that changes size.

**Evidence.** All 11,403 corpus frames render as on master, and in the browser, with the demo-assets corpus harness built for wasm, the 6,228-frame corpus run (at d612b6f) agrees with the native frames exactly as master's does in Chromium 151 and WebKit (macOS 27.2), sliced and unsliced: the same frames identical, the rest within the browsers' shader rounding.

| | change |
|---|---|
| encode, layer-heavy BuseyBench pages (kimi-k2-6, gemini-3-1-pro-preview) | -21 to -25 % |
| encode, draw-heavy pages | -2.7 to -6.7 % |
| encode / instructions, a page of full-screen fills | -15 % / -9.8 % |
| #408's thin-fill masks in motion (an atlas update every frame), diners at 1080p, M4 efficiency cores, cycles a frame over the masks off | +52 % -> +25 % |
| the same over eight thin-fill files, iPhone 16 Pro Max efficiency cores: render-thread cycles / process energy | +7.2 / +3.6 % -> +2.6 / +2.5 % |
| on the web, 53 files at 460x260 and 1080p, frames 2-10: encode, Chromium / WebKit | -32 % / -83 % |
| on the web: GPU-process CPU / queue wait, Chromium / WebKit | -30 % / -33 %, -17 % / +64 % |

On WebKit every `write_buffer` is costly: master's encode there is six times its WebGL2 encode, and this brings it to WebGL2's. ([numbers](https://github.com/rebeckerspecialties/femtovg/blob/demo-assets/harness/wasm/README.md#compute))

**Tests:** `frames_flushed_before_a_submit_each_draw_their_own` and `..._draw_the_image_they_were_given` fail on master; `an_upload_larger_than_a_staging_chunk_keeps_its_place_in_order` fails with only small uploads staged; `an_upload_to_a_callers_texture_lands_before_the_callers_next_write`, `a_callers_texture_destroyed_after_an_upload_leaves_the_next_frame_valid` and `turning_slicing_on_sends_staged_uploads_ahead_of_later_ones` fail without their parts of 55ac393; the viewport bind groups' lifetime and eviction. 641 pass. The element path is wasm-only: a probe in the harness (an image given bytes, frame A flushed and held, the image given a canvas element, frame B flushed, both submitted) draws A from the bytes and B from the element in Chromium and WebKit; queued straight into the image, B drew the bytes.

**Cost:** the belt keeps its chunks (a megabyte, or a frame's uploads) for each frame in flight: +1.5 to 3.6 MiB on ordinary pages; the 65,538-command Babylon page keeps 80 MiB more graphics memory, though its peak footprint falls (1,634 -> 1,545 MiB). On the web the wasm heap's high-water mark is about 7 MiB higher on BuseyBench, and WebKit pays about 1.2 ms a frame of fixed cost (50 rects: 0.3 -> 1.5 ms). wgpu's `std` feature is now asked for: the belt needs it, and a library build for the web did not get it otherwise.
