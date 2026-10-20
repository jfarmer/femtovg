To investigate after the release. In Safari 27.2 on macOS (and in a WKWebView, though not in Safari on iOS), the WGPU backend's draw-heavy frames make WebKit's GPU process step up and hold its memory while the page keeps drawing: 1.4 GB on a scene of 1,000 gradient-filled rects, 2.1-2.6 GB on 4,000 rounded rects in a 460x260 frame, 3.96 GB on Babylon's 65,536-square `vertex-pulling` capture at 2x. Repeating a scene does not grow it further, and in a WKWebView it returns to about 17 MiB some 10 s after the page goes idle, so it is a high-water mark, not a leak. The same frames cost Chrome 151's GPU process 573-981 MiB, the native renderer a peak footprint of 461 MiB-1.1 GB, and WebKit's own WebGL2 path under 504 MiB.

![WebKit's GPU process footprint after each set of ten frames: Safari and a WKWebView stay near 350 MiB through 36 BuseyBench portraits, then step to 1.4 GB at 1,000 gradients and 2.5 GB at 4,000 rects and stay there; Chrome's sawtooths with each portrait and returns; WebKit on WebGL2 stays under 500 MiB](https://raw.githubusercontent.com/rebeckerspecialties/femtovg/demo-assets/issue-webkit-gpu-memory.png)

| master 06243b80, WebGPU | Safari / WKWebView GPU process | Chrome GPU process | native peak footprint | WebKit on WebGL2 |
|---|---:|---:|---:|---:|
| 4,000 rounded rects, 460x260 | 2,154 / 2,115 MiB | 669 MiB | 514 MiB | 463 MiB |
| 1,000 gradient-filled rects | 1,456 / 1,419 MiB | 645 MiB | 461 MiB | 339 MiB |
| Babylon `vertex-pulling`, 2x | 3,957 / 2,859 MiB | 981 MiB | 1,067 MiB (1x) | |

The queue wait follows it: 33 ms a frame for the 4,000 rects in Safari, 8.7 ms in Chrome, 3.2 ms on WebKit's WebGL2.

What is known:
- It is the GPU process's own memory. WebKit charges a page's textures and buffers to its WebContent process, which carries BuseyBench's filter-heavy peaks instead (1.0-1.4 GB) while the GPU process stays near 350 MiB.
- It tracks draws, not pixels or layers: the 1080p portraits do not move it, the thousand-element scenes do.
- #409's staging belt and #419's bind-group cache leave it where it is.
- Safari on an iPhone 12 (iOS 26.5) does not do it. Through the same 4,000 rects its GPU process stays at 31-43 MiB and its WebContent process at 112-128 MiB (Instruments' Activity Monitor, all processes), with a 41 ms queue wait, and no Jetsam event in any of the runs. It is WebKit on macOS.

To do: find what macOS WebKit's WebGPU allocates per draw and keeps that iOS WebKit does not (the encoders and argument buffers its Metal backend builds for each `setBindGroup` with dynamic offsets and draw), and whether femtovg's draws per fill (stencil, fringe, cover) can be merged or their rebinding cut.

Harness and data: [demo-assets harness/wasm](https://github.com/rebeckerspecialties/femtovg/blob/demo-assets/harness/wasm/README.md#safari-itself).
