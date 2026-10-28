#!/bin/zsh
# run_phase.sh: the Chromium jobs one after another, and beside them the WebKit jobs one after another.
R=~/src/femtovg-wt/runs/wasmx
W=~/src/femtovg-wt/da/harness/wasm
export RUN_DIR=$R PLAYWRIGHT=/Users/matt/src/femtovg-wt/tools/node/node_modules/playwright-core
export CHROMIUM="/Users/matt/Library/Caches/ms-playwright/chromium-1234/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"
chr=(${(s: :)1}); wk=(${(s: :)2})
( for j in $wk; do STALL_S=150 ~/src/femtovg-wt/tools/bin/wk_host http://127.0.0.1:8737 $j >> $R/$j/host.log 2>&1; done ) &
( cd $W && node drive_chromium.mjs http://127.0.0.1:8737 $chr ) >> $R/chromium-driver.log 2>&1 &
wait
echo phase done
