# Shadows coloured after the blur, conversions in the composite (library, 2026-10-05)

The follow-up to `shadow-merge-2026-10-04.md`. That change merged a group's shadow in linearRGB, as the
filter and both browsers do. It moved three files away from the browsers (claude-opus-5, kimi-k3,
claude-fable-5-1), which its residuals put on femtovg's shadow pass colouring before the blur.
Trying the pass the other way round helped some files and hurt others. This note finds why, and
gets every framing closer to both browsers, at less memory and fewer passes than before.

The baseline throughout is `master_lsm`: upstream master 9d574e0 with the harness of 2026-10-04,
which is what demo-assets has. The library change is `shadow_merge/library.patch`, on 9d574e0.

## What the browsers do (`corpus/shadow-merge/drop-shadow-tint-rounding.svg`)

The probe draws the same shadows over black and over white, so each pixel gives the shadow's alpha
(1 - (white - black)/255) and its colour (black / alpha). It uses the two dark linearRGB shadows of
the files that moved: kimi-k3's `#2b1712` at .42 and claude-opus-5's `#0b0d10` at .6. Premultiplied
at 8 bits in linearRGB, their channels are fractions of a step: 2.6, 0.9, 0.65 and 0.5, 0.6, 0.8.
The colour is listed down the shadow's falloff, at 1x:

| `#2b1712` at .42, alpha | Chromium | Firefox | femtovg, colour before | femtovg, colour after |
|---|---|---|---|---|
| `feDropShadow` .39 | 48 25 25 | 39 0 0 | 50 27 27 | 50 27 27 (Skia's rounding, below) |
| `feDropShadow` .22 | 54 36 36 | 36 0 0 | 54 36 36 | 54 36 36 |
| written-out chain .39 | 38 25 25 | 39 0 0 | 50 27 27 | 40 27 27 |
| written-out chain .31 | 46 29 0 | 42 0 0 | 44 30 30 | 44 30 0 |
| written-out chain .22 | 36 0 0 | 36 0 0 | 54 36 36 | 36 0 0 |

| `#0b0d10` at .6 (`feDropShadow`), alpha | Chromium | Firefox | femtovg, colour before |
|---|---|---|---|
| .56 | 20 20 20 | 0 0 0 | 20 20 20 |
| .32 | 28 28 28 | 0 0 0 | 28 28 28 |

The colour is 43, 23, 18 and 11, 13, 16. Neither browser comes out at it.
`shadow-tint-rounding-evidence.png` shows each renderer's shadow colour, eight times as bright,
below each shape (`shadow_merge/tint_sheet.py`). They take the shadow apart in three different
ways:

- **Chromium's `feDropShadow` colours before the blur, in 8 bits.** Skia's drop shadow blurs its input
  coloured: the flood's 8-bit premultiplied value, 3, 1, 1 over 107 for the first colour. The ratio
  survives the blur, so the shadow keeps a rounded-up colour down its falloff. The near-black comes out
  a flat grey. femtovg's shadow pass did the same and matches it to two levels.
- **Chromium's written-out chain colours after the blur, rounding once.** `feFlood` with
  `feComposite operator="in"` multiplies the blurred alpha, and a channel rounds away where it falls
  below half a step. That is a shadow coloured after the blur.
- **Firefox colours after the blur and truncates.** Its green and blue are 0 even at the core.

The residuals of 2026-10-04 said both browsers colour after the blur. That holds for Firefox and for
Chromium's written-out chains, not for Chromium's `feDropShadow`. kimi-k3, claude-opus-5, gemini and
nex-n2-pro use `feDropShadow`. claude-fable-5-1, gpt-5-2-pro and gpt-5-6-terra-pro write the chain out.
Turning the pass round alone moved the first group off Chromium onto Firefox and the second group
onto Chromium. That is the "helped some, hurt others".

## The change

**Library (`shadow_merge/library.patch`).**

- **A shadow takes its colour after its blur** (`src/shadow.rs`). The coverage pass draws the source
  and fills it opaque white under `SourceIn`, so the image holds the source's alpha in every channel.
  The blur runs on that. The composite tints it by the shadow colour as it lands, rounded once. That is
  Canvas 2D's order: copy the alpha, blur it, then set the colour and multiply the alpha.
- **A layer whose chain is one colour-space conversion runs it in its composite**
  (`LayerEffects::composite_transfer`). This covers `LinearRgbToSrgb` or `SrgbToLinearRgb` alone,
  without a blend mode, whose pass reads the chain's result. The image paint converts each texel as it
  samples it and rounds it to 8 bits, as the pass would have stored it. The layer reserves no result
  image and no filter work, and the pass is gone. Rule 4a's merge is two such layers, so each merged
  shadow loses two full-layer images and two passes.
- **One transfer curve per shader language** (`transferColor`), shared by the pass and the image
  paint in WGSL and in GLSL.

**Harness (rule 4b).** An `feDropShadow` hands the library the flood colour's 8-bit premultiplied
value, the one Skia blurs. A written-out chain gets the colour as it is. `EXACT_DROP_SHADOW=1` passes
every colour unrounded.

**Tried and dropped: more precision in the linear merge.** The merge layer was tried at 16-bit float
and, separately, as `Rgba8UnormSrgb`, which keeps linear light at sRGB's resolution and blends it in
linear. Both are exact where the browsers round. Both browsers keep the linear intermediates at 8 bits:
the opaque darks of `linear-merge-swatches` band the same way in each. An exact merge stops banding
and moves off both. Against `master_lsm`, 60 and 59 of 156 frames came out worse on the mean.

## Corpus A/B (`shadow-merge-library-ab-2026-10-05.txt`, `shadow_merge/ab.py`)

The 39 files of the 2026-10-04 runs at 1x, 2x, 4x and hd, 156 frames: the 13 with `feTurbulence`, the
21 other corpus files with a merged shadow, and the probes. Each frame is scored against `master_lsm`
on px > 8/255 and the mean max-channel delta, against both browsers. A frame counts as worse when
either metric rises by more than 0.02 points (px > 8) or 0.005 (mean) against either browser.

| build (all against `master_lsm`) | better | level | worse |
|---|---|---|---|
| colour after the blur, as passes | 16 | 121 | 19 |
| + linear merge at 16-bit float, conversions in the composite | 19 | 77 | 60 |
| + linear merge as `Rgba8UnormSrgb` | 17 | 80 | 59 |
| conversions in the composite alone, rounding to 8 bits | 4 | 152 | 0 |
| colour after the blur, float merge, rounding conversions | 21 | 112 | 23 |
| the same with rule 4b | 19 | 114 | 23 |
| **colour after the blur, 8-bit merge, rounding conversions, rule 4b** | **26** | **119** | **11** |

The conversions in the composite alone are a pure optimization. 136 of the 156 frames come out
byte-identical, and the rest differ by at most 2 levels, from tie rounding.

The last row is the change. Per framing, means over the 156 frames:

| framing | vs Chromium px > 8 | mean delta | vs Firefox px > 8 | mean delta |
|---|---|---|---|---|
| z1 | 0.831 → 0.830 % | 0.417 → 0.415 | 0.712 → 0.711 % | 0.402 → 0.400 |
| z2 | 1.377 → 1.372 % | 0.869 → 0.863 | 1.284 → 1.284 % | 0.880 → 0.877 |
| z4 | 1.497 → 1.472 % | 1.097 → 1.084 | 1.275 → 1.264 % | 1.033 → 1.025 |
| hd | 0.293 → 0.287 % | 0.378 → 0.374 | 0.419 → 0.415 % | 0.430 → 0.428 |

Structural (px > 20 after a 2-px erosion) stays 0.003 % at z1 and 0.000 % elsewhere. 124 frames
change.

The three files that moved away on 2026-10-04 move back:

- claude-opus-5 4x: px > 8 2.35 → 2.03 % against Chromium and 2.81 → 2.49 % against Firefox. At hd,
  0.38 → 0.31 % and 0.44 → 0.37 %.
- kimi-k3 4x: 4.21 → 4.01 % against Chromium, under master's 4.10. Against Firefox, 2.15 → 2.16 %.
- claude-fable-5-1 hd: 0.48 → 0.37 % and 0.40 → 0.28 %, under master's 0.43 and 0.32. At 4x,
  1.81 → 1.36 % against Chromium.

**The eleven frames that move away**, and why:

- gpt-5-6-terra-pro hd, 2x, 4x, claude-fable-5-1 2x and gpt-5-2-pro 4x (written-out chains), and
  drop-shadow-flood-linear hd, 2x (an `feDropShadow` in mid blue). Firefox's truncation. Against
  Chromium they come closer or stay level: terra-pro 4x mean 1.428 → 1.387, drop-shadow-flood-linear
  2x 0.415 → 0.371, claude-fable-5-1 2x px > 8 1.57 → 1.46 %. Against Firefox they move away by
  0.007 to 0.036 levels of mean, and by up to 0.03 points of px > 8. Where Chromium rounds and
  Firefox floors, no single 8-bit value matches both.
- gemini-3-1-pro-preview 2x, 4x and its custom-tools variant at 4x: `feDropShadow` shadows. Their
  mean rises 0.005 to 0.011 levels against both browsers. Rule 4b gives the library Skia's rounded
  colour, but the library rounds once after the blur where Skia rounds the coloured source before it.
  Their px > 8 against Chromium improves slightly (7.04 → 7.01 % at 2x).
- linear-merge-swatches 4x: the mean against Chromium rises 0.244 → 0.261. Pixels at the swatch edges
  move by one level, from Chromium's 149 to Firefox's 150.

## Cost (`shadow-merge-library-cost-2026-10-05.txt`, `shadow_merge/cost.py`)

The transient pool's bytes at flush are what the budget bounds. These are taken at 1080p over the 36
files whose layer log shows a merged shadow, on lavapipe. `master` is the harness of before
2026-10-04, `master_lsm` that of 2026-10-04 (two layers per merged shadow), `master_sab` this change.

| 1080p, 36 frames | master | master_lsm | master_sab |
|---|---|---|---|
| pool at flush, mean / max | 69.5 / 179.3 MiB | 85.8 / 205.1 MiB | 75.1 / 187.7 MiB |
| frames over 128 MiB | 6 | 12 | 7 |
| frames the default budget changes | 7 | 13 | 8 |
| layers passed through at the default budget | 82 | 180 | 105 |

Running the conversions in the composite takes back two thirds of what the two-layer merge added.
The mean pool sits 5.6 MiB over master where it sat 16.3 over it.

- **Kept again at the default budget:** five frames that `master_lsm` lost come out whole again:
  fugu-ultra, gemini-3-1-pro-preview-custom-tools, glm-5v-turbo, nex-n2-pro and qwen3-8-max.
- **Still lost:** one frame that master kept, gemini-3-1-pro-preview: 126.9 MiB on master, 145.9 now.
- **Pass-throughs at the default budget fall back toward master:** gpt-5-2-pro passes 6 layers
  through where `master_lsm` passed 35 and master 1; qwen3-8-2-4t-a95b passes 10, against 39 and 7.
- **At 4x:** the mean pool goes from 17.9 to 16.4 MiB, and no frame reaches the budget in either
  build.

**Frame time.** Over the 18 portraits at 1080p, taking the faster of two runs of three frames each
with the builds alternating, frame time goes 33.4 → 32.7 s summed (-2.1 %), and 11 of the 18 get
faster. The per-file ratios run from 0.92 to 1.04, which is about lavapipe's run-to-run spread. On a
GPU, the passes saved are two full-layer fills and two render-target switches per merged shadow.

## Upstream (2026-10-14)

The change is rebased on upstream master 9f5ad26 (#386) as `shadow-after-blur` (6ad8709), the branch of the
upstream PR. Upstream's clip coverage (#390) took `frag[13].y`, where the image paint's transfer sat, and the rows
after it. The transfer now rides in `paint_mat[0].w` (`frag[3].w`), which no image paint reads, so the uniform block
stays at 256 bytes; it is written only for a paint that has one, since a filter pass keeps its own values there.
The half-level mip bias upstream gave image sampling stays on both paths through `paintTexel`.

`m9` is master and `sab` the branch, built with `harness/build.sh m9:<9f5ad26> sab:<shadow-after-blur>`, with every
cfg, crop and clip_paths included. The harness is the same for both, so the A/B measures the library alone (`shadow-merge-library-ab-upstream-2026-10-14.txt`). With
rule 4a's merge layers (`ab.py builds=m9,sab`), on the same 156 frames: 26 better, 119 level, 11 with something
worse, the same frames and reasons as above.

| framing | vs Chromium px > 8 | mean delta | vs Firefox px > 8 | mean delta |
|---|---|---|---|---|
| z1 | 0.807 → 0.807 % | 0.411 → 0.409 | 0.668 → 0.667 % | 0.391 → 0.390 |
| z2 | 1.357 → 1.352 % | 0.863 → 0.857 | 1.218 → 1.219 % | 0.862 → 0.860 |
| z4 | 1.425 → 1.400 % | 1.081 → 1.068 | 1.165 → 1.155 % | 1.008 → 1.000 |
| hd | 0.284 → 0.278 % | 0.376 → 0.371 | 0.407 → 0.403 % | 0.427 → 0.425 |

In demo-assets' default of one shadow layer (`SINGLE_SHADOW_LAYER=1`, the merge in sRGB), the merge layers never
form, so only the shadow's colouring changes: 16 better, 131 level, 9 worse, every framing slightly closer to both
browsers. The largest move away is gpt-5-2-pro at 4x, px > 8 against Chromium 5.07 → 5.23 %. There the sRGB merge
already lays the shadow 1.8 levels darker than Chromium over the pixels that change, and the shadow coloured after
its blur keeps the 0.3 levels of alpha the old pass lost blurring the pre-scaled coverage. With the merge layers the
same frame sits within 0.2 levels of Chromium either way.

`pr-shadow-after-blur-probe.png` is the probe at 1x from the two builds. In both `feDropShadow` rows the branch
follows Chromium's bands where master's are blocky: master rounds the coloured coverage at every blur pass, and the
branch rounds once. In the `feFlood` + `feComposite` row master keeps its rounded-up colour, (50, 27, 27) down to
(67, 0, 0), and the branch follows Chromium's chain: (40, 27, 27), (44, 30, 0), (36, 0, 0), (0, 0, 0).
`pr-shadow-after-blur-corpus.png` (`shadow_merge/pr_sheet.py`) holds the three portraits at 1080p that come back
inside the browsers' range the most:

| 1080p | vs Chromium px > 8 | vs Firefox px > 8 | outside both by > 8 |
|---|---|---|---|
| claude-fable-5-1 | 0.46 → 0.35 % | 0.35 → 0.24 % | 0.20 → 0.12 % |
| claude-opus-5 | 0.30 → 0.23 % | 0.38 → 0.31 % | 0.22 → 0.16 % |
| kimi-k3 | 0.74 → 0.68 % | 0.30 → 0.31 % | 0.09 → 0.09 % |

With rule 4a's merge layers, over the 18 portraits at 1080p (`shadow-merge-library-cost-2026-10-05.txt`):

| 1080p, 18 portraits | m9 | sab |
|---|---|---|
| pool at flush, mean / max | 143.5 / 205.9 MiB | 127.6 / 188.5 MiB |
| frames the default budget changes | 13 | 8 |
| layers passed through at the default budget | 549 | 318 |

Frame time on lavapipe is level, within its run-to-run spread. Summed over the 18, it goes from 24.8 to 25.1 s
(+1.1 %), with 7 of the 18 faster and per-file ratios of 0.90 to 1.10. On 9d574e0 it had gone 2.1 % the other way.
With one shadow layer no lone-conversion layer forms, so the cost does not move.

On lavapipe, the branch passes 552 tests and fails the same 12 as master: `restore_underflow_is_a_no_op`, seven
`layer_state_wgpu` tests and four new clip and mask tests, all exact values that lavapipe rounds differently.
Upstream's CI matrix passes, including the wasm demo with wgpu and the `debug_inspector` tests, and so do fmt and
clippy, with master's 11 warnings and no new one. The headless GL check passes too (Mesa's software EGL device,
GLES 2 and 3).

## Validation

- **Library tests on lavapipe.** 441 pass and 8 fail. The 8 fail on master too:
  `restore_underflow_is_a_no_op` and seven `layer_state_wgpu` tests, exact values that lavapipe
  rounds differently. Three tests are new: `shadow_is_coloured_after_its_blur` (`shadow_wgpu`, which
  fails on master's pass), `a_layer_of_one_conversion_composites_as_its_pass_would`
  (`color_transfer_wgpu`), and `a_lone_conversion_runs_in_the_layer_composite` (unit).
- **OpenGL, headless on Mesa's software EGL device, GLES 2 and GLES 3.** Every shader program compiles
  and links. A lone-conversion layer lands within 0.40 of the pass's 8-bit arithmetic in both
  directions, exactly at alpha 1.
- **CI's matrix.**
  - `cargo build` passes with default features, with `--no-default-features`, for wasm32, and for
    wasm32 with wgpu.
  - The examples build natively, with wgpu, and as the wasm demo.
  - The swash unit tests pass with and without default features.
  - `cargo fmt --check` is clean. Clippy with all features gives master's 11 warnings and no new
    one.
- **Corpus sweep, 898 files at 1x.** 35 change and none fail. They are the 34 merged-shadow files that
  changed on 2026-10-04, and the new probe.
- **The library as committed** renders all 156 A/B frames byte-identical to the experiment build scored
  above.

## Reproducing

    git -C <femtovg checkout of 9d574e0> apply <demo-assets>/harness/shadow_merge/library.patch
    harness/build.sh master_sab:<that checkout>
    harness/build.sh m9:<checkout of upstream 9f5ad26> sab:<checkout of shadow-after-blur>   # the upstream PR
    export CHROMIUM=<headless shell> FIREFOX=<firefox>
    python3 harness/shadow_merge/ab.py out.json builds=master_lsm,master_sab
    python3 harness/shadow_merge/ab.py out.json builds=master_lsm,master_sab list=harness/shadow_merge/merged_shadow_files.json
    python3 harness/shadow_merge/cost.py cost.json builds=master_lsm,master_sab
    python3 harness/shadow_merge/tint_sheet.py CHR.png FF.png BEFORE.ppm AFTER.ppm shadow-tint-rounding-evidence.png
    python3 harness/shadow_merge/ab.py out.json builds=m9,sab    # and list=..., as above
    python3 harness/shadow_merge/pr_sheet.py pr-shadow-after-blur-corpus.png m9=master sab="this PR" \
        --panels=refs,builds,chr,outside claude-fable-5-1:hd:size=200x130:zoom=2 claude-opus-5:hd:size=200x130:zoom=2 \
        kimi-k3:hd:size=200x130:zoom=2

`merged_shadow_files.json` lists the 26 files after the 13 with `feTurbulence`. `cost.py` finds the
files with a merged shadow on its own. The sheet takes the probe's frames at 1x. The numbers above
come from Chromium 141 and Firefox 157 on Linux, with lavapipe in place of a GPU.
