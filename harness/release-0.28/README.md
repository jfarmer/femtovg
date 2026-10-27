# femtovg 0.28 release-notes strips (2026-10-27)

| strip | scene | before / after (pixels > 20/255 off the reference) |
|---|---|---|
| `femtovg-0.28-buseybench.png` | corpus/buseybench/gpt-6-astra.svg, 1080p frame | 4.4 % -> 0.07 % vs Chromium 131 |
| `femtovg-0.28-solidjs-banner.png` | corpus/banner.svg at 350 x 70, shown 3x | 79.3 % -> 0.35 % vs Chromium 131 |
| `femtovg-0.28-text.png` | `_text028.rs` / `text028.html`, 600 x 400 | 12.9 % -> 2.3 % vs Firefox 158 |

**SVG.** `harness/build.sh v027:<v0.27.0 checkout> v028:<v0.28.0 checkout>`. 0.27 has no layer API, so
build.sh gives it `--cfg harness_no_layers`: every layer is a pass-through (filters, masks and shadows are
dropped), group opacity goes onto each shape through `set_global_alpha` as a 0.27 caller would apply it,
gradient geometry is mapped through `gradientTransform` and a two-point radial gradient is drawn from its
end circle as an ellipse. Frame images are not deleted at the end of a frame (0.27 frees them before the
flush that draws from them). The 0.28 build renders bit for bit as before the shim. Busey: `FRAME_W=1920
FRAME_H=1080 BOX=1080 BOX_X=420 BOX_Y=0`; banner: `FRAME_W=350 FRAME_H=70 BOX=350 BOX_X=0 BOX_Y=0`;
references from `make_ref.py` in the puppeteer chrome-headless-shell 131 (`--disable-gpu`).

**Text.** `_text028.rs` built in each checkout with `--features wgpu,swash`, run as `_text028 out.ppm
<checkout>/examples/assets`. Amiri and Roboto Flex from `examples/assets`; the Arabic lines go through
`fill_glyph_run` (glyphs from `measure_text`), as text shaped by parley or cosmic-text does, right-aligned at
a translated anchor so every glyph is at x < 0. What 0.27 gets wrong: the gradient restarts in each 112 px
glyph (#389), each outline glyph casts its own glow over the glyphs before it and the atlas line casts none
(#395), and swash masks at x < 0 are all rasterized at a whole-pixel offset (#384; stem gaps 5 or 6 px, sd
0.48 px, against 0.33 px on 0.28 and 0.19 px in Firefox). The reference is `text028.html` in Firefox
Developer Edition 158 (`--screenshot`, fonts copied beside the page). Chromium 131's headless shell placed the
Amiri lines 150 px off the anchor (Firefox and femtovg agree within a pixel), so it is not used here. The 2.3 %
left is glyph rasterization (swash vs Core Text).

`strips.py` composes the strips from the renders.
