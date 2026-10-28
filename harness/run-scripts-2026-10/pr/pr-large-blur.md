Fixes #325. Builds on #372, whose commit is the first of the two here.

A Gaussian blur whose standard deviation on an axis is above the 8 device pixels one shader pass covers ran as `ceil((sigma / 8)^2)` full-size passes: 93 for the sigma-77 blur a `stdDeviation="10"` SVG filter is at 1080p, and twelve corpus frames where that passed the filter work budget drew unblurred. It now runs the way Skia's GPU blur does: identity passes halve the image along that axis until the sigma, halved with it, fits one pass, the blur runs there, and one pass scales the result back up bilinearly. The level is per axis, so a streak halves x alone and y stays whole; the sigma ceiling rises from 128 to 512; blurs within the bound plan and render as before. The blur shader also reads transparent beyond the image it samples, which is what a filter's input is beyond its edge in SVG and Canvas 2D, instead of extending the edge texel: the border half of #325. The kernel half, the browsers' three-box approximation against femtovg's Gaussian, stays below the corpus threshold and is left as that issue concluded.

### Evidence

Chromium 131 references at the harness's four framings (460x260 at 1x, 2x, 4x; 1080p): pixels beyond 20/255 of the frame, and the structural share after a 2 px erosion. Against #372, the 753-file corpus renders bit-identically on 2,861 of 3,012 frames. The 151 that change all carry a blur above sigma 8; 132 of them move by at most 0.09 points, the pyramid's kernel against the quadrature passes', and the rest are below.

![two WPT reftests, the bigblur probe, a Figma-exported Google Workspace icon, a light shaft and a BuseyBench file: #372, this PR, Chromium 131, and the differences against Chromium (red beyond 20/255, orange 8-20)](https://raw.githubusercontent.com/rebeckerspecialties/femtovg/demo-assets/large-blur-evidence.png)

| file (device sigma) | px > 20/255, #372 -> PR | structural | max |
|---|---:|---:|---:|
| WPT blur-edge-mode-transparent-fade, 1080p (43) | 11.15 % -> 0.00 % | 10.77 % -> 0.000 % | 171 -> 6 |
| WPT filter-clip-under-blur, 1080p (77) | 37.68 % -> 0.06 % | 37.09 % -> 0.000 % | 221 -> 26 |
| WPT blur-primitive-subregion-clipping, 1080p (81) | 9.37 % -> 0.00 % | 9.05 % -> 0.000 % | 191 -> 6 |
| WPT blur-element-expansion-vs-child-clip, 1080p (81) | 6.92 % -> 0.00 % | 6.63 % -> 0.000 % | 123 -> 4 |
| bigblur probe, 4x (100) | 65.95 % -> 0.00 % | 62.05 % -> 0.000 % | 116 -> 8 |
| google-workspace-48px, a Figma export, 1080p (54) | 3.81 % -> 0.02 % | 3.48 % -> 0.000 % | 129 -> 129 |
| light-shaft, 1080p (0 by 126) | 1.48 % -> 0.01 % | 1.32 % -> 0.000 % | 223 -> 46 |
| BuseyBench gemini-3-1-pro-preview, 1080p (26, 98 layers) | 3.01 % -> 0.60 % | 1.87 % -> 0.000 % | 196 -> 196 |
| BuseyBench gemini-3-1-pro-preview-custom-tools, 1080p (42) | 0.99 % -> 0.48 % | 0.38 % -> 0.000 % | 108 -> 108 |

The one frame that gets worse is filter-clip-under-blur at 4x, 0.00 % -> 0.87 % (max 13 -> 24): four columns of the blur's tail where the last count of the 8-bit linearRGB intermediate lands differently and the sRGB transfer stretches it to 10-24. A 16-bit scratch would remove it at twice the memory, which the embedded floor does not have to spare.

### Tests

`tests/large_blur_wgpu.rs`: a chain at sigma 16, a layer at 20 and a shadow at 20 follow the analytic Gaussian profile of their sigma within 3/255 where the clamped single pass misses by tens; sigma 3 and 8 chains stay bit-identical to their single pass; a blurred image fades at its border as the erf of a transparent exterior. `tests/blur_axes_wgpu.rs`: a 16 by 0 streak follows the sigma-16 profile along x while y stays a step, in a layer, a chain and the single pass. Unit tests pin the plan per axis, level and scratch sizes, the work per level, a sigma-77 1080p layer under the default budget, and the shadow's pyramid. 439 GPU and unit tests pass; fmt and clippy clean.

### Cost

A sigma-77 blur over its 1600 px padded store at 1080p was 93 passes of 94 taps, 22.4 G samples, five times the 4 Gi work budget, so the layer drew unblurred; the pyramid is 4.0 M samples (four halvings, a 94-tap blur over 100 x 100 px, one copy), and its scratches add a third of the store where the passes held two full-size ones. Over the 160 blur-set frames at 1080p and 4x, one process per frame on an M4: files with a blur between sigma 32 and 128 go from a median 49.5 ms and 777 MiB peak footprint to 24.0 ms and 554 MiB, between 8 and 32 from 36.8 ms and 723 MiB to 31.2 ms and 585 MiB, below 8 nothing changes, and the seven frames above 128, whose blurs were dropped before, pay 18 -> 25 ms to render them.
