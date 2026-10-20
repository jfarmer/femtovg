#!/bin/zsh
# round_snap.sh N: the snapping build with the masks off, exact, snapped to 1/4 and to 1/8 of a pixel, ABCDDCBA, on
# the device U, into OUT.
S=/Users/matt/src/femtovg-wt/runs/raster/ios; N=$1; i=0
for spec in off exact s4 s8 s8 s4 exact off; do
  i=$((i+1))
  case $spec in
    off) XENV=NO_THIN_FILL_MASKS=1 $S/run_fast.sh pp r$N-$i-off || exit 1;;
    exact) $S/run_fast.sh pp r$N-$i-exact || exit 1;;
    s4) XENV=FEMTOVG_MASK_SNAP=4 $S/run_fast.sh pp r$N-$i-s4 || exit 1;;
    s8) XENV=FEMTOVG_MASK_SNAP=8 $S/run_fast.sh pp r$N-$i-s8 || exit 1;;
  esac
  sleep 3
done
echo "round $N done at $(date)"
