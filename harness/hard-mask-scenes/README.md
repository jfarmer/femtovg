# Concave fills under a whole-or-nothing clip mask

Canvas 2D scenes for femtovg/femtovg's fix of the winding a concave fill left
in the stencil under a clip mask taken whole or not at all (a composite
operation coverage cannot bound: copy, source-in, source-out, destination-in,
destination-atop). The SVG corpus never draws one - SVG puts no Porter-Duff
operator on a shape - so the scenes are written as canvas calls.

- `scenes.json`: each scene a list of `save`, `restore`, `clip` (a polygon),
  `composite` (a `globalCompositeOperation` name) and `fill` (a colour and a
  polygon) on a 120 x 96 canvas.
- `scenes_chromium.py OUT_DIR`: the scenes on a Chromium 131 canvas, over
  white - the reference.
- `wgpu_scenes.rs`: copied into a femtovg checkout's `tests/`,
  `SCENES=scenes.json SCENES_OUT=DIR cargo test --release --features wgpu
  --test wgpu_scenes` draws them with the WGPU backend on a transparent
  target, as a canvas starts, and writes them over white.
- `../clip-bench/gl_scenes.rs`: the same with the OpenGL backend
  (`GL_EXAMPLES=gl_scenes harness/build.sh --gl TAG:SRC`, then
  `gl_scenes_TAG scenes.json OUT_DIR`).
- `strip.py OUT.png label=REF,BEFORE,AFTER ...`: the five-column strip.

`../../pr-hard-mask-winding.png` (WGPU) and `../../pr-hard-mask-winding-gl.png`
(OpenGL) are master 9f5ad26 against the fix. Pixels more than 20 levels off
Chromium, before / after, WGPU (OpenGL): copy 216 / 30 (225 / 30), source-in
186 / 0 (195 / 0), destination-in 186 / 0 (195 / 0), source-over 0 / 0, star
clip 657 / 72 (657 / 72). What is left is the mask's whole-or-nothing edge,
the same before and after.

`scenes-suite18.json` is the reftest suite's own copy of the scenes
(`18-hard-mask-composite-concave-winding/scenes_hard_mask.json`): these five and
eight more operations (source-out, destination-out, destination-atop,
source-atop, xor, clear, lighter, destination-over). Its 48 SVG pairs cannot
draw the bug - SVG puts no composite operation on a shape, and each test and its
reference draw the same thing - so the canvas scenes are the cross-check. Pixels
more than 20 levels off Chromium over the 13, master 9f5ad26 / #403 305f12d:
WGPU 1,677 / 162, OpenGL 1,722 / 162. The scenes #403 moves are copy (216 / 30),
source-in and destination-in (186 / 0), source-out and destination-atop
(216 / 30) and the star clip (657 / 72); the other seven are 0 before and after.
What is left is the hard mask's whole-or-nothing edge. Both scene programs map
every canvas operation now; they mapped only these five's and drew the rest as
source-over (Chromium's legacy `clear` is drawn as destination-out, the same for
the scenes' opaque fills).

## Three browsers, three scales (2026-10-18, master ad762cd5 against #403 59fbefb9)

- `scenes_browser.py chromium|firefox|webkit OUT_DIR`: the scenes on a canvas in each browser (Chromium 131's
  headless shell, Firefox headless `--screenshot`, the system WebKit through `../corpus_run/wk_shot.swift`);
  `SCENES_SCALE=2` draws them at two device pixels a canvas pixel. `scenes_chromium.py` is its Chromium case at 1x.
- `wgpu_scenes.rs` and `../clip-bench/gl_scenes.rs` take `SCENES_SCALE` too.
- `scenes_score.py`: run in a directory holding `chr-S`, `fir-S`, `web-S`, `wgpu-mst-S`, `wgpu-hm-S`, `gl-m403-S`
  and `gl-h403-S` for S in 1, 2, 4; pixels more than 20 off each browser, master and #403, both backends, and for
  every pixel #403 changes whether it moved toward each browser or away.
- `zz_hm_bench.rs`: copied into a checkout's `tests/`, `HM_BENCH=hard|soft|none` draws 400 concave fills at
  1920x1080 under a star clip with `source-in` (a hard mask), `source-over` (a soft mask) or no clip, and prints the
  render thread's exact instructions and cycles a frame per CPU kind; run it under `taskpolicy -c background`.

The three browsers draw all 13 scenes within 20 levels of each other at every scale. Over the 13, pixels more than 20
off Chromium / Firefox / WebKit, master -> #403, WGPU: 1x 1,677 / 1,677 / 1,682 -> 162 / 162 / 168; 2x 5,733 ->
324 (WebKit 5,742 -> 334); 4x 20,978 -> 650 (WebKit 20,991 -> 664). OpenGL: 1,722, 5,818, 21,143 -> 162, 324, 650.
No pixel #403 changes moves away from any browser, and with it the two backends draw the scenes alike (2 pixels apart
on the star at 4x, as on master; master's leaks differed by 9 to 33). Strips: `../../pr-hard-mask-winding-3.png`,
`-gl-3.png`, `-3-4x.png`.
