#!/bin/zsh
# counters2.sh: the femtovg-events template on the device U (into OUT), the final build with the masks off and on,
# ABBA, the frame loop's counters apart (pmcf-*).
S=/Users/matt/src/femtovg-wt/runs/raster/ios; i=0
for spec in offpp pp pp offpp; do
  i=$((i+1)); v=${spec#off}
  if [ "$spec" != "$v" ]; then XENV=NO_THIN_FILL_MASKS=1 $S/run_thin.sh $v c$i-$spec; else $S/run_thin.sh $v c$i-$spec; fi
  sleep 3
done
echo "counters done at $(date)"
