Measured on master 06243b80, which has #302, with the demo-assets corpus harness built for wasm: WebGPU, N static rounded rects in a 460x260 frame, each scene drawn ten times, frames 2-10 counted. Chrome for Testing 151 and the system WebKit (macOS 27.2), on an M4 Max.

| | Chrome | WebKit |
|---|---:|---:|
| GPU-process CPU per 1,000 rects | 1.4 ms | 5.5-6.4 ms |
| record + encode per 1,000 rects | 2.9-3.7 ms | 3.0-3.9 ms |
| queue wait per 1,000 rects | 2.1-2.3 ms | 7.4-9.2 ms |
| 200 rects: encode + queue wait a frame | 0.6 + 0.8 ms | 0.7 + 2.6 ms |

That is about 1.4 µs of GPU-process time per element in Chrome, against the ~0.5 ms per element above: #302 took out the per-draw object creation. #419 trims the encode a little more (-14 % in Chrome, -11 % in WebKit on BuseyBench and these scenes). This is Metal, not the NVIDIA setup above, so it would be good to re-check there before closing. The harness and the numbers: [demo-assets harness/wasm](https://github.com/rebeckerspecialties/femtovg/blob/demo-assets/harness/wasm/README.md#compute), per-scene figures in `results/timing-*.txt`.
