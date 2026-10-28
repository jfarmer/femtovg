# Concave fills that taper below a pixel over-ink their tips

femtovg master 06243b80, WGPU, through the demo-assets harness (`_logos_full`, built with `harness/build.sh` from
that master: all cfgs). A concave fill that is wide overall but narrows to a point keeps the stencil-and-fringe
path, because #408's thin-fill masks gate on the whole outline's mean width (`src/clip/fill.rs` `is_thin`: twice
the area over the perimeter, under 2 px for a concave fill). Its last few pixels before each point then carry far more ink
than their area. The sheet is `../../issue-concave-tip-overink.png`.

## Files

| file | what |
|---|---|
| `wedge.svg` | a straight wedge, one segment a side, with the lip's tips (280, 725), (744, 725) and a 6.2 degree point (the lip's is 6.7) |
| `wedge-split.svg` | the same wedge, each side cut into 18 collinear pieces (5.4 to 5.6 px at 2x) |
| `lip.svg` | the lower lip of `corpus/buseybench/gemini-3-1-pro-preview.svg` (line 293) alone, black on white |
| `render.py` | renders with the harness: `master`, `off` (`NO_THIN_FILL_MASKS=1`), `masks` (`FILL_MASKS=1000 FILL_MASKS_MAX=1e9 CLIP_MASK_BUDGET_MB=512`) |
| `measure.py` | ink at the tips against the area reference, pixels more than 20/255 off the browsers, reductions and portraits (also per tip window) |
| `fringe_model.py` | software replay of the WGPU concave fill from the vertices femtovg emits; splits the excess by pass, and replays each fill with its points mitered |
| `cap/`, `void-dump.patch` | the capture tool `fringe_model.py` runs: one path filled with the z2 transform on a Void renderer patched to print vertices and commands; the patch's other hunk lets `FV_NO_INNERBEVEL=1` skip setting `INNERBEVEL` in `calculate_joins` |
| `mean_width.py` | the mean width #408's gate takes, and the bounds it checks, for each crescent |
| `make_sheet.py` | the five-column sheet |

`FILL_MASKS=T` (harness, `fill_through_mask`) draws each fill whose mean width is under T px as a rect over its
bounds under the path as a clip; the library takes that clip as a coverage mask from `src/clip/coverage.rs`, the
exact-area rasterizer #408's thin-fill masks use. T=1000 with the span and budget lifted sends every fill there.

## Reproduce

```sh
cd harness/concave-tip-overink
RUN=~/src/femtovg-wt/runs/issues/concave-tip-overink        # the run directory: frames, references, measure.json
export CORPUS_RUN_OUT=$RUN
# references for the reductions: files.json lists the three SVGs as group ct, keys ct__<name>
python3 -c "import json,os,sys; d=os.getcwd(); json.dump([{'path': f'{d}/{n}.svg', 'key': f'ct__{n}', 'group': 'ct'}
  for n in ('wedge', 'wedge-split', 'lip')], open(sys.argv[1] + '/files.json', 'w'))" $RUN
(cd ../corpus_run && python3 refs.py chromium framings=z2 group=ct && python3 refs.py firefox framings=z2 group=ct \
  && python3 refs_webkit.py framings=z2 group=ct && python3 refs_ideal.py framings=z2 group=ct)
for v in master off masks; do python3 render.py $v z2 $RUN/png/red wedge.svg wedge-split.svg lip.svg; done
C=../../corpus/buseybench
for v in master off masks; do for f in z1 z2 hd; do
  python3 render.py $v $f $RUN/png/port $C/grok-4-5.svg $C/gemini-3-7-flash.svg $C/gemini-3-1-pro-preview.svg \
    $C/gemini-3-1-pro-preview-custom-tools.svg $C/mistral-large-4.svg; done; done
python3 measure.py $RUN ~/src/femtovg-wt/runs/busey/refs   # the BuseyBench run's chr_/ff_/wk_/id_ references
python3 mean_width.py
# the replay: build cap/ against a femtovg checkout (../femtovg from cap/) with void-dump.patch applied
CAP=cap/target/release/cap python3 fringe_model.py $RUN
python3 make_sheet.py $RUN ../../issue-concave-tip-overink.png ~/src/femtovg-wt/runs/busey/refs
```

Frames: z2 is 460 x 260 with the 1024-unit viewBox fitted to a 200 px box at 2x (0.390625 px a unit), hd 1920 x
1080 with a 1080 px box, z1 the 200 px box at 1x. References: Chromium 131, Firefox 159.0b3, WebKit (macOS 27.2,
`wk_shot`), and the area reference `id_` (Chromium at 8x, averaged). A tip window is 28 x 28 px centred on the tip.
Ink is the summed darkness of black on white, (255 - grey) / 255, in pixels.

## Numbers (2026-10-19)

Reductions at z2, both tip windows (`measure.py`):

| | femtovg master | exact-area masks | Chromium 131 | Firefox 159 | WebKit | area |
|---|---:|---:|---:|---:|---:|---:|
| `wedge.svg` ink / area | 1.11 | 0.99 | 0.99 | 0.99 | 0.98 | 26.2 px |
| `wedge-split.svg` | 1.78 | 0.99 | 1.02 | 1.02 | 0.99 | 26.0 px |
| `lip.svg` | 1.32 | 1.00 | 1.00 | 1.00 | 1.00 | 47.7 px |
| px > 20/255 off the area (wedge, split, lip) | 12, 50, 38 | 0, 0, 0 | 0, 2, 4 | 0, 2, 4 | 0, 0, 0 | |
| px > 20/255 off all three browsers | 12, 50, 38 | 0, 0, 0 | | | | |

Per tip, master puts down +1.44 px of ink over the area on the wedge, +10.17 on the split wedge, +7.68 on the lip.
femtovg's pixels off the area are the same pixels as those off all three browsers, all inside the tip windows.
`NO_THIN_FILL_MASKS=1` renders all three bit-identically to master. Over the whole frame Chromium and Firefox are
65 and 64 px off the area on the split wedge, along its long edges at the added vertices; at the tips 2.

Portraits, pixels more than 20/255 off all three browsers (whole frame / tip windows; master per window in brackets,
in `measure.py`'s `PORTRAITS` order):

| | master | NO_THIN_FILL_MASKS | exact-area masks |
|---|---:|---:|---:|
| grok-4-5 z2, lower hair spikes (lines 153/169) | 134 / 72 [36, 36] | 269 / 72 | 16 / 0 |
| grok-4-5 hd | 365 / 76 [38, 38] | 651 / 76 | 0 / 0 |
| grok-4-5 z1 (#408 takes the spikes at 1x) | 54 / 0 | 585 / 101 | 0 / 0 |
| gemini-3-7-flash z2, lip crescent (line 562) | 191 / 38 [19, 19] | 461 / 38 | 88 / 2 |
| gemini-3-7-flash hd | 161 / 3 [3, 0] | 585 / 3 | 93 / 0 |
| gemini-3-1-pro-preview z2, mouth corners (line 293) | 241 / 46 [24, 22] | 596 / 46 | 133 / 0 |
| gemini-3-1-pro-preview hd | 109 / 26 [12, 14] | 1073 / 26 | 15 / 0 |
| gemini-3-1-pro-preview z1 (the lip is 3.8 px at 1x, over the gate) | 127 / 39 [19, 20] | 415 / 39 | 59 / 1 |
| gemini-3-1-pro-preview-custom-tools z2, eye-top shadows (lines 279/280, four windows) and lips (411/416, two) | 87 / 56 [7, 4, 4, 5, 21, 15] | 89 / 56 | 36 / 3 |
| gemini-3-1-pro-preview-custom-tools hd | 164 / 17 [0, 0, 0, 0, 7, 10] | 164 / 17 | 136 / 0 |
| mistral-large-4 z2, eyebrow spike, teeth and tongue corners (windows also hold strokes) | 51 / 25 [11, 5, 6, 6, 8] | 51 / 25 | 35 / 8 |
| mistral-large-4 hd | 134 / 20 [16, 1, 1, 1, 1] | 134 / 20 | 123 / 16 |

The whole-frame columns move for other reasons too (the masks route every fill; master's #408 masks take other
thin fills). In every tip window master and `NO_THIN_FILL_MASKS` are identical at z2 and hd, and in
gemini-3-1-pro-preview's at z1 (its whole z1 frame is not: 1,830 px differ elsewhere).

Mean widths (`mean_width.py`), z1 / z2 / hd: the lip 3.81 / 7.62 / 20.57 px, the wedge 2.68 / 5.36 / 14.48,
gemini-3-7-flash's crescent 1.37 / 2.75 / 7.42, grok-4-5's spike 1.40 / 2.81 / 7.58,
gemini-3-1-pro-preview-custom-tools' eye-top shadow 1.21 / 2.43 / 6.56 and lips 1.29 / 2.58 / 6.96 and
1.77 / 3.53 / 9.54. Their bounds at hd span 3,366 to 60,001 px, within `THIN_FILL_SPAN` (65,536).

The replay (`fringe_model.py`). The capture tool behind these numbers was built from 09f5174c with
`void-dump.patch` applied; 09f5174c's `src/path`, `src/clip` and `src/renderer/void.rs` are those of 06243b80, the
patch applies to either, and the replay is checked against the 06243b80 frames:

| | wedge | split wedge | lip |
|---|---:|---:|---:|
| largest difference from the frame | 0.86/255 | 0.84/255 | 0.90/255 |
| excess ink in the tip windows | +2.9 | +20.3 | +15.3 |
| of which the cover pass (stencil != 0) | +0.1 | +0.1 | +0.1 |
| of which the fringe pass (stencil 0) | +2.8 | +20.3 | +15.2 |
| px > 20/255 off the area, all with stencil 0 | 12 | 50 | 38 |
| each pixel blended once (strips merged by max) | 12 | 40 | 32 |
| ramps' inner halves dropped (u < 0.5 zeroed in today's strips) | 12 | 10 | 6 |
| both | 12 | 10 | 6 |
| distinct strip inner vertices within 15 px of a tip that the pieces or flattening add, outside the shape | 0 of 0 | 8 of 8 | 4 of 8 |
| the tips' own inner-bevel vertices (1.5 px off each edge at the point), outside the shape | none (mitered) | 4 of 4 | 4 of 4 |
| tip strip's outer vertex, past the point | 9.21 px (mitered) | 0.03 px (beveled) | 0.06 px (beveled) |
| points mitered (`FV_NO_INNERBEVEL=1`): excess a tip, px > 20/255 off the area | +1.44, 12 | +10.00, 49 | +7.81, 39 |
| as built: excess a tip (replay) | +1.44 | +10.17 | +7.65 |

The wedge's tips are mitered: `expand_fill` bevels a point's fringe only when the point has both `BEVEL` and
`INNERBEVEL` (`src/path/cache.rs` L998, an all-of test; `expand_stroke` at L1078 takes either), and the wedge's
~100 px sides leave `INNERBEVEL` unset, so its strip's outer vertex lies 9.2 px past each point and the inner one
27.6 px in. Its 12 px are that faint point past each tip, (137, 212) at 0.29, and none of the counterfactuals that
act on the strips' overlap or inner halves move them. With neighbours 5.4 px (split wedge) and 4.9 px (lip) from the
point, their tips get `INNERBEVEL` and a beveled strip. Mitering them as the wedge's are leaves the split wedge at +10.00 px a tip
and the lip at +7.81: the excess comes from the vertices the pieces and the flattening add, not from the tip join.
`FV_NO_INNERBEVEL` changes only the two tips' joins here (12 fewer strip vertices, 6 a tip).

One edge alone: at the lip's (140, 213), area 0.00, the far edge's strip gives 0.61 (frame 0.61); the pixel's
centre is 0.92 px from that edge and 0.83 px from the near one, whose strip gives 0.00. On the split wedge,
(140, 214) gets 0.68 the same way.

The "inner halves dropped" rows zero the u < 0.5 part of today's strips. That is what re-extruding the concave
strips with the convex half fringe's `lw = woff, lu = 0.5` draws on straight edges; on flattened curves and in the
narrow part the two differ slightly, and that change itself was not built.
