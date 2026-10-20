# Round clip edges: the distance ramp

Evidence for the femtovg issue "Round clip edges take a distance ramp: up to 13/255 off each pixel's area on the
diagonals", from the zoom ladder (`../../corpus_run/zoom_ladder.py`).

Builds, from one revision of `_logos_full.rs` with every cfg: `_logos_full_master_v` (femtovg master 06243b80,
bit-identical to the ladder's frames on all 165 frames of the 15 files) and `_logos_full_area_v` (the same with
`corner-area-on-06243b80.patch`). `render.sh` draws a file at the ladder's framing (460 x 260, the 200-unit box at
130,30) and zooms. Browser frames are the ladder's: Chromium 131 in software, Firefox 159, WebKit (macOS 27.2).
Chromium 131 rasterizing on the GPU was taken at one device pixel per CSS pixel, and the 8x area references are
Chromium 131 on the GPU at 8x, averaged; the exact disc is computed (`measure.py`).

- `corner-area-on-06243b80.patch`: the prototype, fork commit 48b9284 (branch `clip-corner-area`, 2026-10-05) rebased
  onto 06243b80. The WGSL hunk is what was measured; the GLSL hunk is neither compiled nor run.
- `repro.svg`: clip-path-variation-28 without its reftest link; both builds draw it as that file at 3x.
- `v28_16.svg`: the same circle as 16 arcs; master draws it bit-identically at all 11 zooms.
- `measure.py`, `measure.txt`: clip-path-variation-28 at the 11 zooms, every renderer against the exact disc; master
  against the ramp; the 16-arc check; the signs where master and WebKit are apart.
- `pairs.py`, `pairs.txt`: the 78 failing (file, zoom) pairs of the 15 files, master -> prototype, and what is left.
- `sheet.py`, `sheet.txt`: the issue's sheet (`zoom-ladder/round-clip-ramp/sheet.png`) and the numbers its captions quote.
- `strip.py`: the ladder strip (`zoom-ladder/round-clip-ramp/strip.gif` and `.webp`).
