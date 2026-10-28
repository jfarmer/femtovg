#!/bin/zsh
# GPU intervals + Metal GPU Counters + frame signposts on the A15 TV: off, new, old, new, off.
S=/Users/matt/src/femtovg-wt/runs/raster/tv
export COUNTERS=1 TL=200
XENV=NO_THIN_FILL_MASKS=1 $S/run_gpu.sh atv15 pc g1-off thinhd,thin 2 2; sleep 5
$S/run_gpu.sh atv15 pc g2-pc thinhd,thin 2 2; sleep 5
$S/run_gpu.sh atv15 pp g3-pp thinhd,thin 2 2; sleep 5
$S/run_gpu.sh atv15 pc g4-pc thinhd,thin 2 2; sleep 5
XENV=NO_THIN_FILL_MASKS=1 $S/run_gpu.sh atv15 pc g5-off thinhd,thin 2 2
echo "gpu round done"
