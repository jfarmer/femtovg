# Issue #337's inventory (2026-10-18)

What is left of femtovg/femtovg#337 once #403 and #408 merge, measured with `s48` = master ad762cd5 + #408 (ed93d4a5)
+ #403 (59fbefb9), built by `../build.sh s48:<checkout>`.

- `busey_score.py`: BuseyBench (27 files, `accuracy.py s48 group=buseybench framings=z1,hd png=busey_png` with
  `CORPUS_RUN_OUT=runs/thin`) against Chromium 131, Firefox 159, WebKit (macOS 27.2) and the 8x area reference: mean
  px > 20/255 and structural share, with the browsers' envelopes (`busey_score.json`).
- `fail_score.py`: the 23 reftest pairs (groups 01-22, `../corpus_run/wpt22_report.py`-style self-reftests) that s48
  draws more than 0.15 % off Chromium, against each browser and each browser against the suite's reference
  (`fail_score.json`; Firefox and WebKit references made for those pairs with `refs.py firefox` / `refs_webkit.py`
  `keys=`).
- `sheet337.py`: `../../issue337-remaining.png`, s48 | Chromium | Firefox | WebKit | s48 vs Chromium.

## 2026-10-19: current master, 31 portraits, and the shadow merge

`mst2` = master 09f5174c; `mst2lin` = the same binary run through a wrapper that unsets `SINGLE_SHADOW_LAYER`
(`#!/bin/sh` / `unset SINGLE_SHADOW_LAYER` / `exec .../_logos_full_mst2 "$@"`), so the harness's rule 4a merges each
drop shadow under its source in linearRGB as the browsers do. Run directory `runs/busey` (files.json of the 31
BuseyBench portraits, refs symlinked from the corpus run plus new ones for the four added portraits).

- `score.py BUILD`: px > 20 and structural against Chromium, Firefox, WebKit and the area reference at z1, z2, hd.
- `consensus.py BUILD FRAMING`: per portrait, the pixels BUILD draws more than 20/255 off all three browsers, and
  of those the ones where the browsers agree (`consensus_*.json`).
- `triage_sheet.py`: per-portrait sheets cropped to those pixels; `busey_triage_2026-10-19.json` is the root-cause
  triage of the seven worst (each cause reduced and re-rendered, each main cause checked by a second investigator).
- `grid.py mst2 grid_rows.json ../../busey-filter-integration.png mst2lin "..."`: the #337 grid.
- `fail_score_mst2.py`, `sheet337_mst2.py`: the reftest gaps and `../../issue337-remaining.png` on master 09f5174c
  (the same numbers as on s48).

Pixels off all three browsers, summed over the 31 portraits, `mst2` -> `mst2lin`: z2 3.574 -> 1.232 % (-66 %), hd
1.230 -> 0.250 % (-80 %). The grid's rows at hd: gpt-5-6-terra-pro 8,033 -> 14 (its shadow colour: linearRGB
feColorMatrix constants read as sRGB on the single-layer path), mistral-large-4 3,560 -> 134, gpt-5-6-sol-pro
2,754 -> 15, gemini-3-1-pro-preview-custom-tools 1,823 -> 167.

## 2026-10-19 (evening): the linear merge by default, 36 portraits

`mst4` = master 06243b80 with the harness's own defaults, which since this day are rule 4a's merge in linearRGB
(`corpus_run/common.py`); `mst4o_single` = the same master with the harness of the morning and one shadow layer, as
every earlier build ran. Five portraits added (claude-opus-5-5, claude-sonnet-5-5, gpt-6-1-sol, gpt-6-1-sol-pro, pareto).

- `consensus_mst4_*.json`, `consensus_mst4o_single_*.json`, `score_mst4.json`: pixels off all three browsers, mean over
  the 36 portraits, `mst4o_single` -> `mst4`: z2 0.103 -> 0.036 %, hd 0.035 -> 0.006 % (gpt-6-astra's references
  regenerated after the `make_ref.py` fix below).
- `busey_triage_r2_2026-10-19.json`: the root causes of what is left in the portraits the morning's triage did not
  reach (gpt-6-astra, ox-alpha, muse-spark-1-3-contributor, gemini-3-8-flash, glm-5v-turbo, the five new ones), each
  checked by a second investigator. In #337's scope only ox-alpha's `feDisplacementMap` (hairRough, 888 px at 1080p,
  98 % of that file's red). gpt-6-astra's 785 of 815 px at 1080p were `make_ref.py` dropping the root's
  `stroke-linecap`/`stroke-linejoin` (fixed: every root presentation attribute is carried, by its full name). The rest is
  geometry: sliver tips, dashes, round caps tessellated from the half width, fill corners at min(a, b) instead of the
  area, #410's self-crossing lobes, and browser disagreement.
- `grid.py mst4 grid_rows_mst4.json ../../busey-filter-integration.png mst4o_single ...`: the #337 grid, with the
  previous harness default as its last column.
- Reftests on master 06243b80 are those of `s48` but for `resvg-fedropshadow-with-offset-clipped` (the merge), so
  `issue337-remaining.png` stands.
