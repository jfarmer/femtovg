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
