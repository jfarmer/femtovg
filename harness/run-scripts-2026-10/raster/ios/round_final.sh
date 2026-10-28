#!/bin/zsh
# round_final.sh N: #408 as pushed (FlatPP, lib-oi 962340a0) and #408 + #409 (FlatA, lib-fin 802b2ded), each with the
# masks off and on, ABCDDCBA, the 20-frame soak, on the device U, into OUT (no console).
S=/Users/matt/src/femtovg-wt/runs/raster/ios; N=$1; i=0; export NOCONSOLE=1
for spec in offpp pp offa a a offa pp offpp; do
  i=$((i+1))
  case $spec in
    offpp) XENV=NO_THIN_FILL_MASKS=1 $S/run_fast.sh pp r$N-$i-offpp || echo "run failed: $spec";;
    pp) $S/run_fast.sh pp r$N-$i-pp || echo "run failed: $spec";;
    offa) XENV=NO_THIN_FILL_MASKS=1 $S/run_fast.sh a r$N-$i-offa || echo "run failed: $spec";;
    a) $S/run_fast.sh a r$N-$i-a || echo "run failed: $spec";;
  esac
  sleep 3
done
echo "round $N done at $(date)"
