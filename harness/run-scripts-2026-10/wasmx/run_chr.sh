#!/bin/zsh
R=~/src/femtovg-wt/runs/wasmx
export RUN_DIR=$R PLAYWRIGHT=/Users/matt/src/femtovg-wt/tools/node/node_modules/playwright-core
export CHROMIUM="/Users/matt/Library/Caches/ms-playwright/chromium-1234/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"
cd ~/src/femtovg-wt/da/harness/wasm && node drive_chromium.mjs http://127.0.0.1:8737 "$@"
