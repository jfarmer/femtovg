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
