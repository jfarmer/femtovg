Which SVG filter primitives femtovg can run, what a consumer should do with one it cannot, and what is left. Status on master 06243b80 (2026-10-19, after #400); references are Chromium 131, Firefox 159 and WebKit (macOS 27.2).

## Primitives

| primitive | [BuseyBench](https://buseybench.com) files ([`corpus/buseybench/`](https://github.com/rebeckerspecialties/femtovg/tree/demo-assets/corpus/buseybench)) | on master |
|---|---|---|
| `feGaussianBlur` | 36/36 | yes, a layer filter; a deviation per axis (#372), large deviations down a pyramid (#373) |
| `feColorMatrix` | 16/36 | yes (#317) |
| `feDropShadow` | 20/36 | on a group, through the shadow state around `begin_layer` (#322); not as a primitive. Its merge under the source in linearRGB is two lone colour-space conversions, which the layer composite runs since #400 |
| `feTurbulence` | 15/36 | yes (#338) |
| `feComposite` | 9/36 | `over`/`in`/`out`/`atop`/`xor` of a chain with the source graphic, as a Porter-Duff layer composite (consumer-side); between two other inputs, and `arithmetic`: no |
| `feBlend` | 7/36 | yes (#355), and layers with a blend mode (#356); against a flood or a composited input: no (see below) |
| `feMerge` | 7/36 | the source over the chain (the glow idiom); more inputs: no |
| `feOffset`, `feMorphology` | 6/36, 0/36 | yes (#374) |
| `feComponentTransfer` | 2/36 | no |
| `feFlood` | 3/36 | no, as a pass; two files use it in the manual drop-shadow idiom, mapped to a group blur, and grok-4-5 in an inner shadow through `feComposite arithmetic` |
| `feDisplacementMap` | 1/36 | no; ox-alpha's hair is the one effect-chain error BuseyBench shows (below) |

Primitive subregions are cropped with `ImageFilter::Crop` (#385, for #376).

## What a consumer does with a filter it cannot run

Classify by input. A chain that never reads `SourceGraphic` or `SourceAlpha` replaces its source, so the source goes with the chain: the typical `feTurbulence` source is a `<rect>` with no `fill`, which drawn unfiltered is a black wash. A chain that does read the source only decorates it, so the source stays: dropping by primitive kind instead erased faces wrapped in an `feDropShadow` group. `feComposite operator="in"` against the source reads it only as a stencil and needs the graph evaluated rather than scanned. Both rules are in [`harness/README.md`](https://github.com/rebeckerspecialties/femtovg/blob/demo-assets/harness/README.md); femtovg's docs do not state the distinction yet.

## BuseyBench now

36 portraits (five added 2026-10-19: claude-opus-5-5, claude-sonnet-5-5, gpt-6-1-sol, gpt-6-1-sol-pro, pareto), pixels beyond 20/255 and the structural share (beyond 20/255 after a 2 px erosion), mean over the files:

| | 460x260, px > 20 | structural | 1080p, px > 20 | structural |
|---|---:|---:|---:|---:|
| femtovg vs Chromium | 0.303 % | 0.000 % | 0.134 % | 0.000 % |
| femtovg vs Firefox | 0.127 % | 0.000 % | 0.062 % | 0.001 % |
| femtovg vs WebKit | 0.338 % | 0.022 % | 0.197 % | 0.082 % |
| Chromium vs Firefox | 0.210 % | 0.000 % | 0.115 % | 0.001 % |
| Chromium vs WebKit | 0.550 % | 0.023 % | 0.258 % | 0.089 % |

Every file is under 0.5 % structural against Chromium and Firefox. The reference consumer (demo-assets harness) now merges drop shadows under their source in linearRGB by default, as the three browsers do, and reads an `feColorMatrix`'s linearRGB constants as such: the pixels femtovg draws more than 20/255 off all three browsers went from 0.102 % to 0.036 % of the frame at 2x and from 0.034 % to 0.006 % at 1080p. Of what is left, one part is in this issue's scope: ox-alpha's `feDisplacementMap`, which femtovg does not run, so its 13 hair strokes draw smooth where the browsers displace them (888 of the file's 902 px at 1080p). The rest is geometry (#417, #418, #410, below) and pixels the browsers draw differently from one another.

![femtovg, Chromium, Firefox, WebKit, femtovg against all three (red: more than 20/255 off all three; orange: off one or two), and the same with one shadow layer merged in sRGB as in the previous grid: ox-alpha's displaced hair at 1080p, then the previous grid's three shadow rows](https://raw.githubusercontent.com/rebeckerspecialties/femtovg/demo-assets/busey-filter-integration.png?v=20261019b)

Pixels more than 20/255 off all three browsers in the 1080p frame, with one shadow layer merged in sRGB -> as the harness runs now: gpt-5-6-terra-pro 8,230 -> 14, mistral-large-4 3,550 -> 134, gemini-3-1-pro-preview-custom-tools 1,832 -> 164; ox-alpha 902 either way.

## What is left

From BuseyBench (above) and the extracted reftest suite (390 pairs, groups 01-22, at 1x, 2x, 4x and 1080p; below, the pairs femtovg draws more than 0.15 % off all three browsers, worst framing):

![femtovg, Chromium, Firefox and WebKit for six of the pairs below](https://raw.githubusercontent.com/rebeckerspecialties/femtovg/demo-assets/issue337-remaining.png?v=20261019)

1. **`feFlood` and `feComposite` as passes**, so a chain can take an image other than its source as an input. The four `feBlend` chains that reach the blend through a flood or a composite draw the source raw, 100 % off (`filter-chain-blur-feblend-sourcealpha`, `filter-chain-offset-blur-feblend`, `filter-chain-colormatrix-feblend-screen`, `filter-subregion-chain-feblend`), and a flood with a subregion as an input is drawn whole (`resvg-fecomposite-subregion-on-input-2` 36 %, `-1` 87 %, where the suite's own reference also disagrees with all three browsers). The same passes would carry `feMerge` of more inputs and `arithmetic`. No issue yet.
2. **`plus-lighter`** (#379): `blend-plus-lighter-isolated` 42 %. usvg parses it since resvg#1149; femtovg's layers have no blend mode for it.
3. **Masks**: a mask's luminance in `color-interpolation="linearRGB"` (`resvg-mask-color-interpolation-linearrgb` 76 %; #378 is the gradient counterpart) and a mask region under a rotation (`resvg-mask-half-width-region-with-rotation` 68 %). No issues yet.
4. **`feComponentTransfer` and `feDisplacementMap`**: not implemented. ox-alpha's `feDisplacementMap` (an `feTurbulence` displacing its hair strokes, up to 4.7 px at 1080p) is the grid's first row and the last effect-chain error in BuseyBench; the two `feComponentTransfer` files are under 0.3 % structural against every browser without it.
5. **Docs**: the replace-versus-augment rule above.
6. **A filter a small device cannot afford**: #351 (memory accounting and a per-frame degradation policy for filtered layers), #349 (turbulence lattice uploads), #352 (memoryless stencil for layer stores).
7. **Upstream**: usvg turns a zero `feMorphology` radius on one axis into one user unit (resvg#1148): `morphology-erode-horizontal-only` / `-vertical-only` 0.67 % / 0.50 % off Chromium and Firefox. Rotated primitive subregions are resvg#1143.

Done since the last revision: #400 (a shadow coloured after its blur; a lone colour-space conversion run in the layer composite), after which the reference consumer merges drop shadows in linearRGB by default. In flight: #359 (gradient colour spaces, toward #378).

Not femtovg's: on `offset-border-stroke-fill`, `clip-path-concentric-circles-evenodd` and `resvg-clippath-multiple-children` femtovg matches Firefox and WebKit within 0.08 % and Chromium is the odd one out (the suite's references for the first two are off too); `blend-clip-rounded-parent` (0.25 %) is within the browsers' own 0.2-0.46 % spread.

Found by BuseyBench, outside this issue: #418 (concave fills that taper below a pixel over-ink their tips, past #408's mean-width gate) and #417 (dashing starts a new subpath at every vertex a dash crosses); #410's self-crossing lobes in muse-spark-1-3-contributor's hair band and glm-5v-turbo's iris; and, no issues yet, round caps tessellated from the half width (strokes 1-6 px wide end short and pointed), fill corners that cover min(a, b) of a pixel instead of the area, and a 1 px spike at a flattened near-reversal (glm-5v-turbo's ear). Found by the reftest suite, outside this issue, no issues yet: `wpt-2d-line-miter-acute` (50 %, the miter limit's boundary), `resvg-dasharray-0-n-square-caps` / `-round-caps` (11-13 %, zero-length dashes draw no caps), gradient stops at equal or decreasing offsets (`resvg-stops-with-equal-offset-1`, 0.4-0.65 %), and `resvg-clippath-on-children` (1 %, children of a `clipPath` with clip paths of their own).

