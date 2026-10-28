#!/bin/zsh
# off, old, new, new, old, off on the A15 TV, 30 s apart; off = the new build with the masks switched off (master's fills).
S=/Users/matt/src/femtovg-wt/runs/raster/tv
XENV=NO_THIN_FILL_MASKS=1 $S/run_thin.sh pc r2-1-off; sleep 30
i=1
for V in pp pc pc pp; do
  i=$((i+1)); $S/run_thin.sh $V r2-$i-$V; sleep 30
done
XENV=NO_THIN_FILL_MASKS=1 $S/run_thin.sh pc r2-6-off
echo "abba2 done"
