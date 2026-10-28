# femtovg#434 review: gradient LUT pads

- `pad.svg`: three 400 x 50 bars, gradient line x = 120..280 (pads either side): sRGB black-white, linearRGB black-white, linearRGB red-blue. Chromium 131, Firefox and WebKit honour `color-interpolation="linearRGB"` here.
- `review434_wgpu.rs.txt`: the same scene through femtovg's API on the wgpu backend (usvg drops `color-interpolation`), as a test in `tests/`: `REVIEW_OUT=dir REVIEW_TAG=name cargo test --release --features wgpu --test review434_wgpu`.
- `shader-fix.patch`: the prototype on top of #434 (6c806522): sample the LUT at `d * 255/256 + 0.5/256` in the linear, conic and two-point radial LUT paths of both shaders, bake texel i at i/255.
- `pr434-pads.png` (`mk_sheet.py`): main 1bca261c, #434, #434 + patch, against Chromium.
