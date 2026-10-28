#!/bin/bash
# per-glyph runs: configs x glyph index
T=/Users/matt/src/femtovg-wt/target-inv-glyph/release/deps/glyph_atlas_history_wgpu-511f1bd8d7cd6488
D=/Users/matt/src/femtovg-wt/runs/zoom/investigate/inv-glyph/sweep
CASE="0.5,180,30;0.625,167.5,5"
for cfg in master grid subpx gridsubpx; do
  envs=""
  case $cfg in grid) envs="GLYPH_DEVICE_GRID=1";; subpx) envs="GLYPH_SUBPIXEL_MASK=1";; gridsubpx) envs="GLYPH_DEVICE_GRID=1 GLYPH_SUBPIXEL_MASK=1";; esac
  for g in all 0 1 2 3 4 5 6 7 8 9 10 11 12 13; do
    o=$D/$cfg/$g; mkdir -p $o
    if [ $g = all ]; then only=""; else only="GLYPH_ONLY=$g"; fi
    env $envs $only GLYPH_HISTORY_CASE="$CASE" GLYPH_HISTORY_OUT=$o $T --nocapture 2>&1 | grep "ladder vs" | sed "s/^/$cfg g=$g /"
  done
done
