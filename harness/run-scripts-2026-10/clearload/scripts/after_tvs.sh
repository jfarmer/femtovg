#!/bin/zsh
# Waits for the round-2 TV chain, installs the microbenchmark apps on both Apple TVs, then runs the
# microbenchmarks: the A15 TV with the clear-mode decomposition, then the A10X.
CL=/Users/matt/src/femtovg-wt/runs/clearload
until grep -q "chain atv15 atv10 done" $CL/chain-tvs-r2.log; do sleep 10; done
for u in 4ea8fd2afc064771099439023bf48723efa66ba0 00008110-00015D380283801E; do
  for a in FlatPPTV FlatPCTV FlatATV; do
    echo "install $u $a: $(xcrun devicectl device install app --device $u $CL/apps-v2/$a.app 2>&1 | grep -E 'App installed|rror' | head -1)"
  done
done
DIAG=1 $CL/scripts/run_micro.sh atv15
$CL/scripts/run_micro.sh atv10
echo "tv micro done"
