#!/bin/zsh
R=~/src/femtovg-wt/runs/wasmx
( while pgrep -f "run_wk.sh" >/dev/null; do sleep 10; done; $R/run_wk.sh wk-mst4-unsliced wk-mst4-sliced wk-wis-unsliced wk-wis-sliced wk-mst4-webgl ) &
( while pgrep -f "drive_chromium.mjs" >/dev/null; do sleep 10; done; $R/run_chr.sh chr-mst4-unsliced chr-mst4-sliced chr-wis-unsliced chr-wis-sliced chr-mst4-webgl >> $R/chromium-driver.log 2>&1 ) &
wait
