#!/bin/zsh
# round2.sh N: one build with the masks off and on, ABBA (offpp pp pp offpp), on the device U, into OUT.
S=/Users/matt/src/femtovg-wt/runs/raster/ios; N=$1; i=0
for spec in offpp pp pp offpp; do
  i=$((i+1)); v=${spec#off}
  if [ "$spec" != "$v" ]; then XENV=NO_THIN_FILL_MASKS=1 $S/run_fast.sh $v r$N-$i-$spec || exit 1
  else $S/run_fast.sh $v r$N-$i-$spec || exit 1; fi
  sleep 3
done
echo "round $N done at $(date)"
