#!/bin/zsh
# The A14 keeps only the last ~23 s of the app's frame signposts, so round 2 there has the BuseyBench
# phases but not the curve ones: a short ABBA of the two curve phases, one pass each (204 frames a leg).
CL=/Users/matt/src/femtovg-wt/runs/clearload
until grep -q "phone micro done" $CL/micro-phones.log; do sleep 15; done
i=0
for V in pp pc pc pp; do i=$((i+1)); COUNTERS=1 $CL/scripts/run_mst.sh a14 $V r3-$i-$V curve,curvehd 1 1; sleep 10; done
echo "a14 curve done"
