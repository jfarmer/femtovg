#!/bin/zsh
# round_snap16_long.sh N: off, exact, 1/8 and 1/16 px (ABCDDCBA) as round_snap_long.sh, but each file moves for 200 frames in one pass (REPEAT=200, PASSES=1) - a
# long pan of the same content, where kept snapped masks can come back - on the device U, into OUT.
S=/Users/matt/src/femtovg-wt/runs/raster/ios; N=$1; i=0; export RUN_TIMEOUT=${RUN_TIMEOUT:-400}
for spec in off exact s8 s16 s16 s8 exact off; do
  i=$((i+1))
  case $spec in
    off) XENV=NO_THIN_FILL_MASKS=1 $S/run_fast.sh pp r$N-$i-off thinhd,thin 1 200 || echo "run failed: $spec";;
    exact) $S/run_fast.sh pp r$N-$i-exact thinhd,thin 1 200 || echo "run failed: $spec";;
    s4) XENV=FEMTOVG_MASK_SNAP=4 $S/run_fast.sh pp r$N-$i-s4 thinhd,thin 1 200 || echo "run failed: $spec";;
    s8) XENV=FEMTOVG_MASK_SNAP=8 $S/run_fast.sh pp r$N-$i-s8 thinhd,thin 1 200 || echo "run failed: $spec";;
    s16) XENV=FEMTOVG_MASK_SNAP=16 $S/run_fast.sh pp r$N-$i-s16 thinhd,thin 1 200 || echo "run failed: $spec";;
  esac
  sleep 3
done
echo "round $N done at $(date)"
