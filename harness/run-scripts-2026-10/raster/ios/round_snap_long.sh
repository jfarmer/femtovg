#!/bin/zsh
# round_snap_long.sh N: as round_snap.sh, but each file moves for 200 frames in one pass (REPEAT=200, PASSES=1) - a
# long pan of the same content, where kept snapped masks can come back - on the device U, into OUT.
S=/Users/matt/src/femtovg-wt/runs/raster/ios; N=$1; i=0; export RUN_TIMEOUT=${RUN_TIMEOUT:-400}
for spec in off exact s4 s8 s8 s4 exact off; do
  i=$((i+1))
  case $spec in
    off) XENV=NO_THIN_FILL_MASKS=1 $S/run_fast.sh pp r$N-$i-off thinhd,thin 1 200 || exit 1;;
    exact) $S/run_fast.sh pp r$N-$i-exact thinhd,thin 1 200 || exit 1;;
    s4) XENV=FEMTOVG_MASK_SNAP=4 $S/run_fast.sh pp r$N-$i-s4 thinhd,thin 1 200 || exit 1;;
    s8) XENV=FEMTOVG_MASK_SNAP=8 $S/run_fast.sh pp r$N-$i-s8 thinhd,thin 1 200 || exit 1;;
  esac
  sleep 3
done
echo "round $N done at $(date)"
