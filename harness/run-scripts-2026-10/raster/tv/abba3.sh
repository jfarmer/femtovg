#!/bin/zsh
S=/Users/matt/src/femtovg-wt/runs/raster/tv
$S/run_thin.sh pp r3-1-pp; sleep 5
XENV=NO_THIN_FILL_MASKS=1 $S/run_thin.sh pc r3-2-off; sleep 5
$S/run_thin.sh pp r3-3-pp
echo "abba3 done"
