#!/bin/zsh
# Waits for the round-2 phone chain, installs the microbenchmark apps on the three iPhones, then runs the
# microbenchmarks: the A13 with the clear-mode decomposition, then the A14 and the A12.
CL=/Users/matt/src/femtovg-wt/runs/clearload
until grep -q "chain a13 a14 a12 done" $CL/chain-phones-r2.log; do sleep 10; done
for u in 00008030-0005694926D3402E 00008101-000A044A3C28801E 00008020-001C292A2190003A; do
  for a in FlatPP FlatPC FlatA; do
    echo "install $u $a: $(xcrun devicectl device install app --device $u $CL/apps-v2/$a.app 2>&1 | grep -E 'App installed|rror' | head -1)"
  done
done
DIAG=1 $CL/scripts/run_micro.sh a13
$CL/scripts/run_micro.sh a14
$CL/scripts/run_micro.sh a12
echo "phone micro done"
