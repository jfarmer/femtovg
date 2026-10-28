Which SVG filter primitives femtovg can run, what a consumer should do with one it cannot, and what is left. Status on master 09f5174c (2026-10-19); references are Chromium 131, Firefox 159 and WebKit (macOS 27.2).

## Primitives

| primitive | [BuseyBench](https://buseybench.com) files ([`corpus/buseybench/`](https://github.com/rebeckerspecialties/femtovg/tree/demo-assets/corpus/buseybench)) | on master |
|---|---|---|
| `feGaussianBlur` | 31/31 | yes, a layer filter; a deviation per axis (#372), large deviations down a pyramid (#373) |
| `feColorMatrix` | 14/31 | yes (#317) |
| `feDropShadow` | 17/31 | on a group, through the shadow state around `begin_layer` (#322); not as a primitive. The shadow merges under its source in linearRGB, which the shadow state does not (see below) |
| `feTurbulence` | 13/31 | yes (#338) |
| `feComposite` | 7/31 | `over`/`in`/`out`/`atop`/`xor` of a chain with the source graphic, as a Porter-Duff layer composite (consumer-side); between two other inputs, and `arithmetic`: no |
| `feBlend` | 7/31 | yes (#355), and layers with a blend mode (#356); against a flood or a composited input: no (see below) |
| `feMerge` | 6/31 | the source over the chain (the glow idiom); more inputs: no |
| `feOffset`, `feMorphology` | 5/31, 0/31 | yes (#374) |
| `feComponentTransfer` | 2/31 | no |
| `feFlood` | 2/31 | no, as a pass; both corpus uses are the manual drop-shadow idiom, mapped to a group blur |
| `feDisplacementMap` | 1/31 | no |

Primitive subregions are cropped with `ImageFilter::Crop` (#385, for #376).

## What a consumer does with a filter it cannot run

Classify by input. A chain that never reads `SourceGraphic` or `SourceAlpha` replaces its source, so the source goes with the chain: the typical `feTurbulence` source is a `<rect>` with no `fill`, which drawn unfiltered is a black wash. A chain that does read the source only decorates it, so the source stays: dropping by primitive kind instead erased faces wrapped in an `feDropShadow` group. `feComposite operator="in"` against the source reads it only as a stencil and needs the graph evaluated rather than scanned. Both rules are in [`harness/README.md`](https://github.com/rebeckerspecialties/femtovg/blob/demo-assets/harness/README.md); femtovg's docs do not state the distinction yet.

## BuseyBench now

31 portraits (four added 2026-10-19: gpt-6-sol, muse-wonder, mistral-large-4, gemini-4-argon), pixels beyond 20/255 and the structural share (beyond 20/255 after a 2 px erosion), mean over the files:

| | 460x260, px > 20 | structural | 1080p, px > 20 | structural |
|---|---:|---:|---:|---:|
| femtovg vs Chromium | 0.366 % | 0.000 % | 0.155 % | 0.013 % |
| femtovg vs Firefox | 0.193 % | 0.001 % | 0.122 % | 0.023 % |
| femtovg vs WebKit | 0.420 % | 0.029 % | 0.240 % | 0.111 % |
| Chromium vs Firefox | 0.223 % | 0.000 % | 0.097 % | 0.001 % |
| Chromium vs WebKit | 0.606 % | 0.027 % | 0.294 % | 0.103 % |

Every file is under 0.5 % structural against Chromium and Firefox. Most of what is left is pixels the browsers draw differently from each other; the pixels femtovg draws more than 20/255 off all three where the three agree come mostly from one effect chain, a drop shadow merged under its source in sRGB where the browsers merge in linearRGB (item 1 below). The four portraits furthest from all three browsers, at 1080p, each cropped to where it is furthest:

![the four BuseyBench portraits femtovg master draws furthest from all three browsers: femtovg, Chromium, Firefox, WebKit, femtovg against all three (red: more than 20/255 off all three; orange: off one or two), and the same with the linearRGB shadow merge](https://raw.githubusercontent.com/rebeckerspecialties/femtovg/demo-assets/busey-filter-integration.png?v=20261019)

Pixels more than 20/255 off all three browsers in the 1080p frame, master as the reference consumer runs it today and with its linearRGB shadow merge: gpt-5-6-terra-pro 8,033 -> 14, mistral-large-4 3,560 -> 134, gpt-5-6-sol-pro 2,754 -> 15, gemini-3-1-pro-preview-custom-tools 1,823 -> 167. Over all 31 portraits the linear merge removes 66 % of them at 2x and 80 % at 1080p. Of the new portraits, mistral-large-4 is row 2; gpt-6-sol, muse-wonder and gemini-4-argon are within 0.05 % of all three browsers and raise nothing new.

## What is left

From BuseyBench (above) and the extracted reftest suite (390 pairs, groups 01-22, at 1x, 2x, 4x and 1080p; below, the pairs femtovg draws more than 0.15 % off all three browsers, worst framing):

![femtovg, Chromium, Firefox and WebKit for six of the pairs below](https://raw.githubusercontent.com/rebeckerspecialties/femtovg/demo-assets/issue337-remaining.png?v=20261019)

1. **Drop shadows merged in linearRGB.** `feDropShadow` and the written-out shadow chain merge the shadow under their source in linearRGB, the default `color-interpolation-filters`, and Chromium, Firefox and WebKit all do. The reference consumer (demo-assets harness) runs with `SINGLE_SHADOW_LAYER=1`, the shadow state around the group's one layer, which merges in sRGB, so translucent and anti-aliased pixels over their own shadow come out 15-40 levels dark (grid rows 2-4). Its rule 4a merges in linearRGB at the cost of a layer and two conversion passes per shadow on master; #400 runs those conversions in the layer composite, after which rule 4a can be the default (the last grid column). Also in the harness, a few lines: the single-layer path reads `feColorMatrix` constants computed in linearRGB as sRGB, which turns gpt-5-6-terra-pro's teal shadow near-black (row 1).
2. **`feFlood` and `feComposite` as passes**, so a chain can take an image other than its source as an input. The four `feBlend` chains that reach the blend through a flood or a composite draw the source raw, 100 % off (`filter-chain-blur-feblend-sourcealpha`, `filter-chain-offset-blur-feblend`, `filter-chain-colormatrix-feblend-screen`, `filter-subregion-chain-feblend`), and a flood with a subregion as an input is drawn whole (`resvg-fecomposite-subregion-on-input-2` 36 %, `-1` 87 %, where the suite's own reference also disagrees with all three browsers). The same passes would carry `feMerge` of more inputs and `arithmetic`. No issue yet.
3. **`plus-lighter`** (#379): `blend-plus-lighter-isolated` 42 %. usvg parses it since resvg#1149; femtovg's layers have no blend mode for it.
4. **Masks**: a mask's luminance in `color-interpolation="linearRGB"` (`resvg-mask-color-interpolation-linearrgb` 76 %; #378 is the gradient counterpart) and a mask region under a rotation (`resvg-mask-half-width-region-with-rotation` 68 %). No issues yet.
5. **`feComponentTransfer` and `feDisplacementMap`**: not implemented; the three corpus files that use them are under 0.3 % structural against every browser without them.
6. **Docs**: the replace-versus-augment rule above.
7. **A filter a small device cannot afford**: #351 (memory accounting and a per-frame degradation policy for filtered layers), #349 (turbulence lattice uploads), #352 (memoryless stencil for layer stores).
8. **Upstream**: usvg turns a zero `feMorphology` radius on one axis into one user unit (resvg#1148): `morphology-erode-horizontal-only` / `-vertical-only` 0.67 % / 0.50 % off Chromium and Firefox. Rotated primitive subregions are resvg#1143.

In flight: #400 (a shadow coloured after its blur; a lone colour-space conversion run in the layer composite, which item 1 waits on), #359 (gradient colour spaces, toward #378).

Not femtovg's: on `offset-border-stroke-fill`, `clip-path-concentric-circles-evenodd` and `resvg-clippath-multiple-children` femtovg matches Firefox and WebKit within 0.08 % and Chromium is the odd one out (the suite's references for the first two are off too); `blend-clip-rounded-parent` (0.25 %) is within the browsers' own 0.2-0.46 % spread.

Found by BuseyBench, outside this issue, no issues yet: concave fills that taper below a pixel over-ink at the tip, where an edge's fringe reaches across the opposite edge (#408's thin-fill masks gate on the whole path's mean width, so wide crescents with sub-pixel tips keep their fringes; gemini-3-7-flash's lip corners, grok-4-5's hair spikes); and dashes split at every flattened vertex, each piece with its own caps, so gemini-3-7-flash's dashed iris rings carry 1.65-1.9x the browsers' ink, with dashes shorter than the fringe over-inking besides. Found by the reftest suite, outside this issue, no issues yet: `wpt-2d-line-miter-acute` (50 %, the miter limit's boundary), `resvg-dasharray-0-n-square-caps` / `-round-caps` (11-13 %, zero-length dashes draw no caps), gradient stops at equal or decreasing offsets (`resvg-stops-with-equal-offset-1`, 0.4-0.65 %), and `resvg-clippath-on-children` (1 %, children of a `clipPath` with clip paths of their own).

