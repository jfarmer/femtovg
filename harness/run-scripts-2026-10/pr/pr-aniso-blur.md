Fixes #362. `ImageFilter::GaussianBlur` takes `sigma_x` and `sigma_y`: SVG's two-valued `feGaussianBlur stdDeviation` and the canvas layer filter's `stdDeviation: [x, y]`, where the one `sigma` spread the larger value both ways. `ImageFilter::gaussian_blur(sigma)` is the isotropic form. Each axis splits into its own quadrature passes above the per-pass bound and an unblurred axis copies through, a layer pads each axis by its own reach, and both backends drive the horizontal and vertical draws with their own coefficients.

### Evidence

Chromium 131 references at the harness's four framings (460x260 at 1x, 2x, 4x; 1080p): pixels beyond 20/255 of the frame, and the structural share after a 2 px erosion. The whole corpus, 753 files, renders bit-identically to master on 2,979 of 3,012 frames; the 33 that change are every frame of the nine files with a two-valued `stdDeviation`.

![x-only WPT case, the #362 reftest, a motion streak, a light shaft and a ground shadow: master, this PR, Chromium 131, and the differences against Chromium (red beyond 20/255, orange 8-20)](https://raw.githubusercontent.com/rebeckerspecialties/femtovg/demo-assets/aniso-blur-evidence.png)

| file (`stdDeviation`) | px > 20/255 at 1x, master -> PR | worst framing | structural, worst framing | Chromium vs Firefox |
|---|---:|---:|---:|---:|
| WPT 2d.layer.anisotropic-blur.x-only (4 0) | 2.01 % -> 0.00 % | 2x: 7.53 % -> 0.00 % | 6.08 % -> 0.000 % | 0.00 % |
| WPT 2d.layer.anisotropic-blur.y-only (0 4) | 2.01 % -> 0.00 % | 4x: 19.13 % -> 0.00 % | 17.39 % -> 0.000 % | 0.00 % |
| WPT 2d.layer.anisotropic-blur.mostly-x (4 1) | 1.96 % -> 0.00 % | 2x: 6.74 % -> 0.00 % | 3.96 % -> 0.000 % | 0.00 % |
| WPT 2d.layer.anisotropic-blur.mostly-y (1 4) | 1.96 % -> 0.00 % | 4x: 18.26 % -> 0.00 % | 14.78 % -> 0.000 % | 0.00 % |
| blur-axis-zero-directional, the #362 reftest (0 8, 8 0) | 3.90 % -> 0.00 % | 4x: 14.13 % -> 0.00 % | 12.94 % -> 0.000 % | 0.00 % |
| motion-streak (14 0) | 1.47 % -> 0.01 % | 2x: 3.48 % -> 0.00 % | 2.29 % -> 0.000 % | 0.01 % |
| light-shaft (0 28) | 6.57 % -> 0.01 % | 2x: 17.39 % -> 0.00 % | 15.65 % -> 0.000 % | 0.07 % |
| ground-shadow (12 2.5) | 1.42 % -> 0.02 % | 4x: 23.45 % -> 0.05 % | 19.55 % -> 0.000 % | 0.26 % |

The WPT rows are the canvas layer tests `2d.layer.anisotropic-blur.*` as SVG; the three idioms are a speed streak, a vertical light shaft and an elliptical ground shadow (demo-assets `corpus/wpt-layer-blur-reftests`, `corpus/blur-idioms`). The one residual, light-shaft at 1080p (3.61 % -> 1.48 %), is the shaft's sigma-126 blur exceeding the filter work budget and being dropped, which the large-blur PR following this one addresses.

### Tests

`tests/blur_axes_wgpu.rs`: the WPT cases and a split axis against the shader's discrete kernel composed per axis - x blurred while y stays a step and the reverse, sigma 16 by 0 as four passes, the single pass clamping x and copying y - in a layer, a chain and `filter_image`; unit tests for the per-axis plan, work, reach and store padding. 437 GPU and unit tests pass; fmt and clippy clean.

### Cost

Isotropic blurs plan and render as before. A blur along one axis costs that axis's taps plus a one-tap copy per pass instead of two full kernels, and pads its store on that axis only.
