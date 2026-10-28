#!/bin/zsh
# round_mem.sh N: #408 (FlatPP, lib-oi 420f070a) with the masks off and on, the memory experiment (FlatA, lib-mem2
# 599fcdb1: no CPU copy of the atlas, started over smaller) and the thin-fill gate at 2 px (FlatPC, lib-gate 8106c327),
# ABCDDCBA, the 20-frame soak, on the device U, into OUT. Launched without the console (NOCONSOLE=1).
S=/Users/matt/src/femtovg-wt/runs/raster/ios; N=$1; i=0; export NOCONSOLE=1
for spec in off t408 mem2 gate gate mem2 t408 off; do
  i=$((i+1))
  case $spec in
    off) XENV=NO_THIN_FILL_MASKS=1 $S/run_fast.sh pp r$N-$i-off || echo "run failed: $spec";;
    t408) $S/run_fast.sh pp r$N-$i-t408 || echo "run failed: $spec";;
    mem2) $S/run_fast.sh a r$N-$i-mem2 || echo "run failed: $spec";;
    gate) XENV=FEMTOVG_THIN_WIDTH=2 $S/run_fast.sh pc r$N-$i-gate || echo "run failed: $spec";;
  esac
  sleep 3
done
echo "round $N done at $(date)"
