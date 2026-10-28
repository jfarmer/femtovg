# The corpus harness in the browser (2026-10-19)

The demo-assets corpus harness (`../_logos_full.rs`) compiled to wasm32 and run in Chromium and WebKit, against the
same harness built natively: stability, agreement with the native frames (and so with the browser references the
native frames are measured against), memory and compute. Builds: master 06243b80 (`mst4`), #409 at d612b6f0
(`wis`, the staging belt), and branch wgpu-bind-group-cache at cc13e870 (`bgc`). Browsers: Chrome for Testing 151
(Playwright) and the system WebKit of macOS 27.2 in a WKWebView (Safari's engine and its WebGPU), on an M4 Max.

## How it runs

- `crate/`: a cdylib whose `build.rs` includes `_logos_full.rs` unchanged but for its crate attributes, its own doc
  comment, and its environment reads, which go to a map the page fills per frame (`env_shim`). `src/web.rs` is the
  page's entry: one device and one canvas for the whole run, as an app keeps them.
- `build_wasm.sh TAG:SRC`: the crate against a femtovg checkout, with that checkout's `Cargo.lock` and every harness
  cfg its API supports, then `wasm-bindgen --target web` (the CLI of the checkout's wasm-bindgen crate, 0.2.129).
- `server.py JOBS.json`: hands the page one frame at a time (each framing's env and `SWEEP_ENV`, as `accuracy.py`
  sets them), compares the frame with the native build's PNG, keeps the frames that differ by more than 8 levels,
  and samples the browser's processes per frame through `procstat.py` (`proc_pid_rusage`: footprint, its lifetime
  maximum, CPU time, instructions; it reads WebKit's XPC services too) and the GPU's `ioreg` statistics.
- `page/`: the page. `NO_READBACK` measures frames without the readback; `NO_POST_PIXELS` reads back but does not
  upload.
- `drive_chromium.mjs` (playwright-core), `wk_host.swift` (WKWebView; finds its WebContent and GPU process ids
  through `_webProcessIdentifier` and the pool's `_gpuProcessIdentifier`): one browser per job, a watchdog that
  reloads a stalled or crashed page.
- `drive_safari.py`: Safari itself, which cannot be scripted without remote automation: it opens the job page
  (`open -a Safari`, or `xcrun devicectl ... --payload-url` on an iOS device), passes the processes to sample, and
  opens the page again when it stalls. For a device, `server.py ... bind=0.0.0.0 tls=CERT,KEY allow=192.168.7.`
  serves the page over TLS (WebGPU needs a secure context) to the local network only; the certificate is a
  temporary self-signed one, whose warning has to be accepted on the device.
- A probe job (`"probe": "element-upload"`) runs `probe_element_upload` in place of frames: the order of a web image
  source's upload against a frame flushed before it and submitted after it (#409).
- `analyze.py`, `timing.py`, `gpu_memory_chart.py`: the summaries below.

Corpus: the 1,279 demo-assets files, the 780 files of the extracted reftest suite (groups 01-22), 17 synthetic
scenes (`perf`: 0-4,000 rounded rects, stars, lines, gradients, a clipped set, blurred circles), at 460x260 1x and
2x and at 1080p: 6,228 frames a job.

## Stability

Ten correctness jobs, 62,280 frames: master and #409, each unsliced (the library default) and sliced (the harness
default), on WebGPU in both browsers, and master on WebGL2 (wgpu's GL backend) in both. No frame threw, no device
error, no lost device, no frame the page died on. The only reloads were two Chromium renderer crashes, which were the
harness's: Chromium's renderer keeps the body of every large `fetch` POST out of the collector's reach (a forced
`gc()` frees nothing), and the page uploaded every frame's pixels (8 MB at 1080p). The renderer reached 13 GB.
Reading back without uploading keeps it flat (145-194 MiB over 100 1080p frames); the driver now opens a new page
every 600 frames.

## Agreement

Against the native frames, every engine, build and backend gives the same answer: 5,816 to 5,968 frames of 6,177
identical, the rest within 2 levels in WebKit and within 8 in Chromium and on WebGL2 (11 frames at 3-8 levels, shader
compilers' rounding), except 12 frames: the four Babylon captures of
Unicode text, whose fallback glyphs come from system fonts the page does not load (it loads Arial, Times New Roman,
Courier New and Courier, which the corpus's text names). The 21 frames of the seven files with embedded PNGs differed
until the crate took `image`'s PNG and JPEG codecs, which the native harness gets through femtovg's dev-dependencies
(femtovg's `image-loading` takes `image` without codecs); with them they are bit-identical to native.

## Memory

Measured without the readback and upload (the timing jobs: BuseyBench and `perf` at 1x and 1080p, 10 frames each):

- The wasm heap peaks at 34 MiB (WebGPU) and 64-68 MiB (WebGL2, where wgpu-core runs in the page). The corpus's
  largest, Babylon's 65,536-square `vertex-pulling` scene, takes it to 243 MiB on WebGPU and 664 MiB on WebGL2;
  wasm memory does not shrink, so the page keeps that. #409 adds about 7 MiB (39 against 32 MiB over BuseyBench).
- Chromium's GPU process stays at 600-700 MiB and peaks at 2.8 GB, returning; the renderer stays at 200-320 MiB.
- WebKit's GPU process holds about 2 GB while femtovg draws a scene with thousands of draws, and gives it back about
  10 s after the page goes idle: `perf__rects-4000` at 460x260 holds it at 2,077 MiB through four repeats of 10
  frames, then it drops to 17 MiB. The same frames: Chromium's GPU process 573 MiB, native 514 MiB peak footprint
  (472 MiB of it graphics), WebKit's WebGL2 path under 504 MiB. It is WebKit's WebGPU, not a leak in femtovg.

## Compute

Steady state (frames 2-10), summed over the 106 frames (53 files, 1x and 1080p); master run twice to bound the noise
(Chromium 3-6 %, WebKit medians identical):

| 1080p, sum over 53 files | encode (record + flush) | queue wait | GPU process CPU / frame | page process CPU / frame |
|---|---:|---:|---:|---:|
| Chromium, master | 292 ms | 990 ms | 869 ms | 1,482 ms |
| Chromium, bind-group cache | 253 ms (-14 % median) | 951 ms | 819 ms (-7 %) | 1,419 ms |
| Chromium, #409 | 198 ms (-32 %) | 807 ms (-17 %) | 581 ms (-30 %) | 1,161 ms (-20 %) |
| Chromium, master on WebGL2 | 237 ms | 742 ms | 1,096 ms | 1,225 ms |
| WebKit, master | 1,345 ms | 725 ms | 1,749 ms | 1,321 ms |
| WebKit, bind-group cache | 1,176 ms (-11 % median) | 715 ms | 1,540 ms (-11 %) | 1,274 ms |
| WebKit, #409 | 251 ms (-83 %) | 1,142 ms (+64 %) | 1,128 ms (-33 %) | 1,255 ms |
| WebKit, master on WebGL2 | 229 ms | 227 ms | 1,185 ms | 683 ms |

- On WebKit, master's WebGPU path costs five to six times the encode of its WebGL2 path; #409's belt brings the
  encode down to WebGL2's (one mapped staging copy instead of a `writeBuffer` per upload), at about 1.2 ms a frame of
  fixed cost (`perf__rects-50`: 0.3 -> 1.5 ms) and a longer queue wait. On Chromium #409 is cheaper on every count
  but the queue wait of stroked lines (`perf__lines-1000` 8 -> 16 ms).
- Cost per element on `perf__rects-N`, master: GPU process 1.4 ms per 1,000 rects on Chromium, 5.5-6.4 ms on WebKit;
  encode 2.9-3.9 ms per 1,000 in both, as natively (native `rects-4000`: 14.5 ms encode). #305's ~0.5 ms per element
  (Chrome on an NVIDIA GPU, an older femtovg) is not what master costs here.
- First use of a pipeline is slow in WebKit: a frame that first draws through the clip-path pipeline waited 1.9 s.

## Safari itself

Safari 27.2 on macOS, the same page opened as a tab: the 6,252-frame corpus run (the codec-enabled build) has no
error, lost device or reload, and the same 12 Unicode frames off native, nothing else. Its GPU process does what
the WKWebView's does: about 350 MiB through BuseyBench, 1,456 MiB at `perf__grads-1000`, 2.1-2.6 GB at
`perf__rects-4000`, and 3,957 MiB on Babylon's 65,536-square `vertex-pulling` capture at 2x (the WKWebView's
2,859 MiB, Chrome's GPU process 981 MiB, native peak footprint 1,067 MiB). `../../issue-webkit-gpu-memory.png`
plots it.

## Safari on an iPhone 12

iOS 26.5, Safari, the page served over TLS on the local network (the certificate accepted once on the device):
BuseyBench and the clip-path reftests at 1x and 2x (272 frames), BuseyBench and `perf` at 1x and 1080p for ten frames
each (106), and the 1,000-gradient and 4,000-rect scenes four times each. No error, lost device or reload; 239 of the
272 frames identical to native and the rest within 5 levels; no Jetsam event on the device during the runs.
Through the 4,000 rects (Instruments' Activity Monitor, all processes; `ios-am6.trace` in the run directory) Safari's
GPU process stays at 31-43 MiB and its WebContent process at 112-128 MiB: the 2 GB of WebKit's GPU process on macOS
(#420) is not iOS's. The 4,000 rects cost 14 ms of encode and 41 ms of queue wait a frame there.

Instruments on the device hung while saving whenever it ran detached from a terminal, and needed about nine minutes
to save a 90-second recording made while Safari drew; run it in the foreground with a generous time-out.

## Files

`analysis-correctness.json`, `analysis-part1.json`, the jobs' `results.jsonl` / `events.jsonl` / `procs.jsonl` are in
the run directory (`runs/wasmx`); `jobs-full.json` there is the job list.
