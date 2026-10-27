# Old issues re-checked on 0.28.0 (2026-10-27)

- **#132 `realloc_image`** — `gl_realloc_check.rs` (copy to `examples/`, `cargo run --example gl_realloc_check`):
  an `Rgb8` image target filled, realloc'ed, filled again, read back. 0.27.0 loses all 40 stars after every
  realloc (the GL renderer kept the image id's framebuffer on the old texture); 0.28.0 keeps them (13347641).
- **#233 text at a fractional scale** — `_dpr233.rs` (wgpu, `--features wgpu,swash`; `_dpr233 out.ppm
  <checkout>/examples/assets 1.566667 dpr|slint [ratio]`) and `dpr233.html` (`?s=1`, beside
  `RobotoFlex-VariableFont.ttf`). `strip.py` makes `issue-233-dpr-1.5667.png`:
  0.20.0 3.92 % vs Chromium 131, 0.28.0 2.06 %; Firefox vs Chromium 0.31 %. Ink centroid: 0.20 off by 0.38 px
  both ways, 0.28 by 0.03 / 0.16 px. 0.28 is byte-identical for set_size ratios 1, 1.566667 and 2; 0.27 and 0.28
  with swash are identical on this scene. femtovg puts down 12 % less ink than either browser in every version.
