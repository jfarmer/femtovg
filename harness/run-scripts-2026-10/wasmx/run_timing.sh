#!/bin/zsh
R=~/src/femtovg-wt/runs/wasmx
$R/run_chr.sh t-chr-mst4 t-chr-bgc t-chr-wis t-chr-mst4b >> $R/chromium-driver.log 2>&1
$R/run_wk.sh t-wk-mst4 t-wk-bgc t-wk-wis t-wk-mst4b
echo timing done
