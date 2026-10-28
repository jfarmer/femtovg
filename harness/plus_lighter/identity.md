# Identity sweeps, 2026-10-24

corpus_run/identity.py over 2,215 files x 16 framings (35,440 frames), wgpu, harness of this commit.

| pair | what moves | frames that differ |
|---|---|---|
| b48 -> b49 (usvg 0.48 -> 0.49, library unchanged) | `wpt-pservers-reftests/gradient-transform-template-inheritance` (14 framings): usvg 0.49 inherits `gradientTransform` through `href` (resvg#1135); 3.55 % -> 2.09 % beyond 20/255 vs Chromium at z1, 6.01 % -> 3.55 % at hd. `blend-plus-lighter-isolated` (4 subpixel framings, both copies): usvg keeps plus-lighter as its own group, which the harness without the mode draws as a normal layer, 6.49 % either way | 22 |
| b49 -> bpl (plus-lighter) | `blend-plus-lighter-isolated`, both copies, every framing: 3.85 % -> 0 vs Chromium at z1, the frame hash equal to its reference file's | 32 |

No frame failed. Residual in the template-inheritance tests: usvg stops inheritance at an empty, whitespace-only or
invalid `gradientTransform`/`patternTransform` (`resolve_attr` checks only that the attribute exists); Chromium and
Firefox inherit, the system WebKit does not. `usvg-invalid-transform-href.png` from `invalid-transform-href.svg`;
`template_inheritance.png` is the femtovg frame.

New lighter tests (corpus/resvg-lighter, plus the WPT test), at z1/z2/z4/hd, beyond 20/255 vs Chromium:

| file | master | plus-lighter |
|---|---|---|
| WPT mix-blend-mode-plus-lighter-svg-basic | 3.85 / 15.4 / 42.1 / 6.49 % | 0 everywhere |
| resvg painting/mix-blend-mode/plus-lighter | 13.3 / 47.7 / 82.5 / 22.2 % | 0.007 / 0 / 0 / 0 % |
| resvg filters/feComposite/operator-lighter (bpl2) | 30.8 / 83.5 / 100 / 52.0 % | 0.007 / 0 / 0 / 0 % |
| resvg filters/feBlend/invalid-mode-plus-lighter | 0.007 % | 0.007 % (usvg: normal) |
