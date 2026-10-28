#!/bin/zsh
R=~/src/femtovg-wt/runs/wasmx
for j in "$@"; do mkdir -p $R/$j; STALL_S=${STALL_S:-120} ~/src/femtovg-wt/tools/bin/wk_host http://127.0.0.1:8737 $j >> $R/$j/host.log 2>&1; done
