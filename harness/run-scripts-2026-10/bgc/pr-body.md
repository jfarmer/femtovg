The WGPU backend kept one bind group and made a new one whenever a draw bound a different image, glyph atlas or clip mask than the draw before. Under a soft clip mask a concave fill's winding pass binds no mask and its cover binds one, so every such fill made two bind groups. The pipeline mapper now keeps the flush's bind groups by what they bind (the image or view, the glyph texture, the clip mask) and makes each once; the images and the uniform buffer a bind group refers to do not change within a flush.

Render thread a frame, 400 concave fills at 1080p under a seven-pointed star clip mask ([`zz_hm_bench`](https://github.com/rebeckerspecialties/femtovg/blob/demo-assets/harness/hard-mask-scenes/zz_hm_bench.rs), M4 Max, 60 frames, two runs each):

| | master 06243b80 | this |
|---|---:|---:|
| soft mask (source-over) | 30.3 M instructions, 3.3-3.8 ms | 16.0 M instructions, 1.8 ms |
| hard mask (source-in) | 15.8 M | 15.8 M |
| no clip | 15.2 M | 15.1 M |

In the browser, with the demo-assets harness built for wasm (36 BuseyBench portraits and 17 synthetic scenes at 460x260 and 1080p, frames 2-10 of ten, master run twice to bound the noise at 3-6 %): record and encode -14 % in Chromium 151 and -11 % in WebKit (macOS 27.2), median per frame; GPU-process CPU -7 % and -11 % ([numbers](https://github.com/rebeckerspecialties/femtovg/blob/demo-assets/harness/wasm/README.md#compute)).

Every corpus frame (1,279 files at ten framings, 12,790 frames) renders bit-identically to master. `tests/bind_group_cache_wgpu.rs` counts the bind groups a flush of concave fills under a soft clip mask leaves alive (wgpu's `counters`): one set for the flush, not two per fill.
