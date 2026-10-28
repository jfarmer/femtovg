#!/bin/zsh
# off, new (growable atlas), old, new, off: CPU counters, per-frame E-core counts and peak footprint.
S=/Users/matt/src/femtovg-wt/runs/raster/tv
XENV=NO_THIN_FILL_MASKS=1 $S/run_thin.sh pc r5-1-off; sleep 3
$S/run_thin.sh pc r5-2-pc; sleep 3
$S/run_thin.sh pp r5-3-pp; sleep 3
$S/run_thin.sh pc r5-4-pc; sleep 3
XENV=NO_THIN_FILL_MASKS=1 $S/run_thin.sh pc r5-5-off
echo "round5 done"
