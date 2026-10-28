Which SVG filter primitives femtovg can run, what a consumer should do with one it cannot, and what is left. Status on master ad762cd5 with #403 and #408 merged (2026-10-18); references are Chromium 131, Firefox 159 and WebKit (macOS 27.2).

## Primitives

| primitive | [BuseyBench](https://buseybench.com) files ([`corpus/buseybench/`](https://github.com/rebeckerspecialties/femtovg/tree/demo-assets/corpus/buseybench)) | on master |
|---|---|---|
| `feGaussianBlur` | 27/27 | yes, a layer filter; a deviation per axis (#372), large deviations down a pyramid (#373) |
| `feColorMatrix` | 14/27 | yes (#317) |
| `feDropShadow` | 14/27 | on a group, through the shadow state around `begin_layer` (#322); not as a primitive |
| `feTurbulence` | 13/27 | yes (#338) |
| `feComposite` | 7/27 | `over`/`in`/`out`/`atop`/`xor` of a chain with the source graphic, as a Porter-Duff layer composite (consumer-side); between two other inputs, and `arithmetic`: no |
| `feBlend` | 7/27 | yes (#355), and layers with a blend mode (#356); against a flood or a composited input: no (see below) |
| `feMerge` | 5/27 | the source over the chain (the glow idiom); more inputs: no |
| `feOffset`, `feMorphology` | 5/27, 0/27 | yes (#374) |
| `feComponentTransfer` | 2/27 | no |
| `feFlood` | 2/27 | no, as a pass; both corpus uses are the manual drop-shadow idiom, mapped to a group blur |
| `feDisplacementMap` | 1/27 | no |

Primitive subregions are cropped with `ImageFilter::Crop` (#385, for #376).

## What a consumer does with a filter it cannot run

Classify by input. A chain that never reads `SourceGraphic` or `SourceAlpha` replaces its source, so the source goes with the chain: the typical `feTurbulence` source is a `<rect>` with no `fill`, which drawn unfiltered is a black wash. A chain that does read the source only decorates it, so the source stays: dropping by primitive kind instead erased faces wrapped in an `feDropShadow` group. `feComposite operator="in"` against the source reads it only as a stencil and needs the graph evaluated rather than scanned. Both rules are in [`harness/README.md`](https://github.com/rebeckerspecialties/femtovg/blob/demo-assets/harness/README.md); femtovg's docs do not state the distinction yet.

![what an unrunnable filter does](https://raw.githubusercontent.com/rebeckerspecialties/femtovg/demo-assets/busey-filter-integration.png)

## BuseyBench now

27 portraits, pixels beyond 20/255 and the structural share (beyond 20/255 after a 2 px erosion), mean over the files:

| | 460x260, px > 20 | structural | 1080p, px > 20 | structural |
|---|---:|---:|---:|---:|
| femtovg vs Chromium | 0.345 % | 0.000 % | 0.147 % | 0.011 % |
| femtovg vs Firefox | 0.200 % | 0.000 % | 0.265 % (5 files) | 0.109 % |
| femtovg vs WebKit (26 files) | 0.368 % | 0.026 % | 0.205 % | 0.099 % |
| Chromium vs Firefox | 0.192 % | 0.000 % | 0.067 % (5 files) | 0.000 % |
| Chromium vs WebKit (26 files) | 0.521 % | 0.025 % | 0.241 % | 0.090 % |

Every file is under 0.5 % structural against Chromium and Firefox; the worst against Chromium is gpt-5-6-terra-pro at 1080p (0.263 %). femtovg is as far from each browser as the browsers are from each other.

## What is left once #403 and #408 merge

From the extracted reftest suite (390 pairs, groups 01-22, at 1x, 2x, 4x and 1080p), the pairs femtovg draws more than 0.15 % off all three browsers, worst framing:

![femtovg, Chromium, Firefox and WebKit for six of the pairs below](https://raw.githubusercontent.com/rebeckerspecialties/femtovg/demo-assets/issue337-remaining.png)

1. **`feFlood` and `feComposite` as passes**, so a chain can take an image other than its source as an input. The four `feBlend` chains that reach the blend through a flood or a composite draw the source raw, 100 % off (`filter-chain-blur-feblend-sourcealpha`, `filter-chain-offset-blur-feblend`, `filter-chain-colormatrix-feblend-screen`, `filter-subregion-chain-feblend`), and a flood with a subregion as an input is drawn whole (`resvg-fecomposite-subregion-on-input-2` 36 %, `-1` 87 %, where the suite's own reference also disagrees with all three browsers). The same passes would carry `feMerge` of more inputs and `arithmetic`. No issue yet.
2. **`plus-lighter`** (#379): `blend-plus-lighter-isolated` 42 %. usvg parses it since resvg#1149; femtovg's layers have no blend mode for it.
3. **Masks**: a mask's luminance in `color-interpolation="linearRGB"` (`resvg-mask-color-interpolation-linearrgb` 76 %; #378 is the gradient counterpart) and a mask region under a rotation (`resvg-mask-half-width-region-with-rotation` 68 %). No issues yet.
4. **`feComponentTransfer` and `feDisplacementMap`**: not implemented; the three corpus files that use them are under 0.3 % structural against every browser without them.
5. **Docs**: the replace-versus-augment rule above.
6. **A filter a small device cannot afford**: #351 (memory accounting and a per-frame degradation policy for filtered layers), #349 (turbulence lattice uploads), #352 (memoryless stencil for layer stores).
7. **Upstream**: usvg turns a zero `feMorphology` radius on one axis into one user unit (resvg#1148): `morphology-erode-horizontal-only` / `-vertical-only` 0.67 % / 0.50 % off Chromium and Firefox. Rotated primitive subregions are resvg#1143.

In flight: #400 (a shadow coloured after its blur; a lone colour-space conversion run in the layer composite), #406 (`Canvas::blur_rect`), #359 (gradient colour spaces, toward #378).

Not femtovg's: on `offset-border-stroke-fill`, `clip-path-concentric-circles-evenodd` and `resvg-clippath-multiple-children` femtovg matches Firefox and WebKit within 0.08 % and Chromium is the odd one out (the suite's references for the first two are off too); `blend-clip-rounded-parent` (0.25 %) is within the browsers' own 0.2-0.46 % spread.

Found by the same suite, outside this issue, no issues yet: `wpt-2d-line-miter-acute` (50 %, the miter limit's boundary), `resvg-dasharray-0-n-square-caps` / `-round-caps` (11-13 %, zero-length dashes draw no caps), gradient stops at equal or decreasing offsets (`resvg-stops-with-equal-offset-1`, 0.4-0.65 %), and `resvg-clippath-on-children` (1 %, children of a `clipPath` with clip paths of their own).
