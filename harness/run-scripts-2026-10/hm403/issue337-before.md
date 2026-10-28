Filter support on upstream master (0d09c8f) is `feGaussianBlur` plus the color-matrix family (#317, chained by #321), now also as layer effects (#322/#323). A 27-file corpus of AI-generated SVG portraits ([BuseyBench](https://buseybench.com), mirrored at [`corpus/buseybench/`](https://github.com/rebeckerspecialties/femtovg/tree/demo-assets/corpus/buseybench)) puts numbers on what is missing, and on how badly a consumer can go wrong when a filter cannot be run.

## What the corpus asks for

Every one of the 27 files uses `feGaussianBlur`. Beyond that (status as of master 0d09c8f, 2026-09-17):

| primitive | files | supported |
|---|---|---|
| `feGaussianBlur` | 27/27 | yes — a layer filter; sigma above 8 device px composes in quadrature since #340 |
| `feColorMatrix` | 14/27 | yes |
| `feDropShadow` | 14/27 | on a group: the shadow state around `begin_layer`, cast once by the layer (#322, harness rule 4); not as a primitive |
| `feTurbulence` | 13/27 | #338 (open): `ImageFilter::Turbulence` plus `LinearRgbToSrgb` for the chain's end |
| `feComposite` | 7/27 | `operator="in"` against `SourceGraphic`/`SourceAlpha`: a `SourceIn` layer (#322's composites, harness rule 3, on the #338 chain); as a chain's last primitive against the source, `over`/`in`/`out`/`atop`/`xor` are mapped by the harness as Porter-Duff composites of the chain's layer with the group (2026-10-03, below); `arithmetic` no |
| `feBlend` | 7/27 | no — needs separable blend modes, #332 |
| `feMerge` | 5/27 | the source over the chain's result (the glow idiom) yes; more inputs no |
| `feOffset` | 5/27 | #374 (open): `ImageFilter::Offset` |
| `feComponentTransfer` | 2/27 | no (`linear` / two-entry `table` on alpha would fold into a color matrix; not wired, both files end in `feBlend`) |
| `feFlood` | 2/27 | no — both uses are inside the manual drop-shadow idiom (blur of `SourceAlpha` → `feOffset` → `feFlood` → `feComposite in` → `feMerge` with the source), which consumes the source, so rule 1 keeps the subtree and the harness maps the chain to a whole-group blur |
| `feDisplacementMap` | 1/27 | no — a dependent read; the source draws undisplaced |

`feTurbulence` is the striking one: half the corpus reaches for it, always for the same thing - a skin-texture or film-grain overlay. It needs no extra buffers at all, only a noise generator — which is what #338 implements.

## The part that bites a consumer

Skipping an unrunnable filter is not the safe default, and neither is ignoring it. A filter's source graphic is often a shape that was never meant to be seen - for `feTurbulence` it is typically a `<rect>` with no `fill`, which defaults to **black**. Draw it unfiltered and you get a black wash; three portraits rendered 15-18% too dark that way (as reported). Drop it by primitive kind instead and you erase content, because two of the same portraits wrap the whole face in an `feDropShadow` group.

![what an unrunnable filter does](https://raw.githubusercontent.com/rebeckerspecialties/femtovg/demo-assets/busey-filter-integration.png)

The rule that works is to classify by *input*: a chain that never consumes `SourceGraphic` or `SourceAlpha` replaces its source, so the subtree goes with it; anything that does consume the source only decorates it, so the subtree stays. That plus clipping to the SVG viewport took the corpus from 0.73% mean structural difference against Chromium to **0.24%** (as reported on 2026-09-06, on the #322/#323/#324 stack), against a Chromium-vs-Firefox envelope of 0.19% — 26 of 27 files under 0.5%. Both rules and their measurements are written up in [`harness/README.md`](https://github.com/rebeckerspecialties/femtovg/blob/demo-assets/harness/README.md).

One case the input test gets wrong: `feComposite operator="in" in2="SourceGraphic"` uses the source purely as a stencil, so its colour never reaches the output even though the chain consumes it ([`claude-opus-5.svg`](https://github.com/rebeckerspecialties/femtovg/blob/demo-assets/corpus/buseybench/claude-opus-5.svg), 3.65% structural as reported). Deciding that needs the graph evaluated rather than scanned, which is what the #338 harness rule does: `in` is Porter-Duff source-in, so the group gets a layer, the source draws into it, the noise draws over it with `SourceIn`.

## Suggestion

`feTurbulence` is in #338. Of the rest, the corpus says `feBlend` is worth more than `feMerge`/`feOffset`: seven files' chains end in `mode="multiply"` against the source (#332; the effect is a darkening of a few percent, below 20/255, so those files already sit at 0.00–0.31%), and `feDisplacementMap` (ox-alpha's hair) needs a dependent-read pass. Separately, whatever ships, it would help consumers if the docs stated the replace-versus-augment distinction, since every usvg-to-femtovg integration has to make that call and the failure mode is silent and ugly.

## Status on master (2026-09-17)

Merged since this was filed: #322 layers, #323 masks, #340 quadrature blur (with #336/#339). Open: #338 feTurbulence, #324 clip paths. The sheet above is regenerated from master (harness rule 5, invalid filter references, on: 0 dropped in this corpus) with the open PRs as extra columns; same framing and references as before (460x260, 1x, Chromium 131, Firefox DE for the envelope), per-file numbers in `harness/busey-master-metrics.json`.

| build | mean px > 20/255 | mean structural | files under 0.5 % structural |
|---|---|---|---|
| master, drawn raw (no rules) | 2.83 % | 1.149 % | 19/27 |
| master + the two rules | 1.94 % | 0.632 % | 23/27 |
| master + #338 (open) | 1.80 % | 0.527 % | 23/27 |
| master + #338 + #324 (the open stack) | 0.85 % (Firefox 0.74 %) | 0.026 % (Firefox 0.025 %) | 27/27 |
| Chromium vs Firefox | 0.19 % | 0.000 % | — |

The rules do on master what they did on the stack: qwen3-8-flash 5.43 % → 0.18 % structural, claude-fable-5-1 5.13 % → 0.03 %, qwen3-8-2-4t-a95b 2.88 % → 0.21 %. The master-only mean is above the 0.24 % reported because #324 is not merged: kimi-k2-6 (6.19 %), gemini-3-1-pro-preview-custom-tools (1.95 %) and nex-n2-pro (1.49 %) are clip-path files, untouched by the rules or #338 and 0.000 % with #324. `claude-opus-5`, the stencil case: 4.49 % on master (the black rect plus its six clip paths drawn unclipped) → 1.87 % with #338 (the `SourceIn` layer; what is left is the clips) → 0.00 % with #324. `qwen3-8-max` (feTurbulence + `saturate(0)` replacing its rect): 0.31 % → 0.06 % → 0.00 %. With the open stack, the four files above 0.05 % (gemini-3-8-flash 0.119 %, gpt-5-2-pro 0.186 %, gpt-5-6-sol-pro 0.153 %, gpt-5-6-terra-pro 0.193 %) carry exactly the pre-#340 stack's numbers (`harness/busey-all-fixes-metrics.json`); nothing in this issue's scope moves them.

## Reftests (2026-10-03)

An extracted reftest suite (test/reference pairs modelled on WPT `filter-effects` and the resvg filter tests), run on the #372/#373/#374 stack against Chromium 131 at 1x, 2x, 4x and 1080p, sorts the primitives above into three bins.

**Mapped around, not implemented.** `feComposite` of a chain's result with the source graphic under `over`, `in`, `out`, `atop` or `xor` is Porter-Duff, so the harness draws the chain in an inner layer and composites the group with it under that operator (the glow idiom generalized, with an isolating layer around both for anything but `over`): `offset-composite-in`, `offset-composite-out`, `offset-composite-xor` and `morphology-edge-detection` (dilate, then `out` against the source) render pixel-exact. `arithmetic` is no operator and stays unmapped. This is a consumer-side mapping; an `ImageFilter` composite against the source would let a chain continue past the composite, which the mapping cannot.

**Still missing, and visible.** The four `feBlend` chains that reach the blend through a flood or a composite draw their source raw, 100 % of the 4x window: `filter-chain-blur-feblend-sourcealpha` (blur of `SourceAlpha`, flood, `composite in`, `feBlend screen` with the source), `filter-chain-offset-blur-feblend` (the same behind an offset), `filter-chain-colormatrix-feblend-screen` (a color matrix, then `feBlend screen` with a flood) and `filter-subregion-chain-feblend` (two floods with subregions, blended). What `blur_blend` maps is blur-then-`feBlend` with the source as the other input; a blend whose other input is a flood or a composited silhouette needs that second branch as an image, which is `feFlood` and `feComposite` as passes.

![the four feBlend chains at 1x: femtovg draws the source raw (or nothing, for the flood-only chain), Chromium 131 and Firefox the blended result](https://raw.githubusercontent.com/rebeckerspecialties/femtovg/demo-assets/issue337-feblend-chains.png)

**Hidden by the filter region.** `offset-triple-chain-rgb-shadow` (two offsets of the source, `feMerge` of both under it) renders like Chromium only because the default filter region clips the shifted copies to the source's own box, where the source covers them; `feMerge` of anything but the chain and the source is unmapped. The harness now runs an unfinished chain not at all rather than its first passes - the offset alone put that pair 1.3 % off at 1080p, and `offset-composite-out` 16 % off against 13 % for the raw source.

Found by the same suite but not this issue's: intermediates are not clipped to their primitive subregion (`offset-chained-cancelling` 33 %, `morphology-closing-chain` 10 %, both with the suite's own references on femtovg's side), reported with the suite's results.

