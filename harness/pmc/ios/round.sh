#!/bin/zsh
# round.sh N: the six variants, forward then back (masks off/on for #408, + belt, + image staging), so a drift over the
# round falls alike on all. Stops at the first launch that fails (a locked phone).
S=/Users/matt/src/femtovg-wt/runs/raster/ios; N=$1; i=0; START=${START:-1}
for spec in offpp pp a offa offpc pc pc offpc offa a pp offpp; do
  i=$((i+1)); v=${spec#off}; [ $i -lt $START ] && continue
  if [ "$spec" != "$v" ]; then XENV=NO_THIN_FILL_MASKS=1 $S/${RUN:-run_fast.sh} $v r$N-$i-$spec || exit 1
  else $S/${RUN:-run_fast.sh} $v r$N-$i-$spec || exit 1; fi
  sleep 3
done
echo "round $N done at $(date)"
