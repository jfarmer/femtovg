#!/bin/zsh
# GPU intervals + Metal GPU Counters + frame signposts on the iPhone 16 Pro Max, 1080p thin-fill phase: masks off,
# masks on (+ image staging), then on, off.
S=/Users/matt/src/femtovg-wt/runs/raster/ios
export COUNTERS=1 TL=400
XENV=NO_THIN_FILL_MASKS=1 $S/run_gpu.sh a18 pc g1-off thinhd 2 2; sleep 5
$S/run_gpu.sh a18 pc g2-pc thinhd 2 2; sleep 5
$S/run_gpu.sh a18 pc g3-pc thinhd 2 2; sleep 5
XENV=NO_THIN_FILL_MASKS=1 $S/run_gpu.sh a18 pc g4-off thinhd 2 2
echo "gpu round done at $(date)"
