#!/bin/zsh
# ABBA on one phone: #368 head (pp), fold (pc), fold, #368 head; all four soak phases.
# usage: run_abba.sh a12|a13|a14 [round]   (GPU counters on a13/a14; the a12's recording fails with them)
D=$1; R=${2:-1}; S=/Users/matt/src/femtovg-wt/runs/clearload/scripts
C=1; [[ $D == a12 || $D == atv10 ]] && C=
i=0
for V in pp pc pc pp; do
  i=$((i+1))
  COUNTERS=$C $S/run_mst.sh $D $V r$R-$i-$V curve,curvehd,busey,buseyhd 4 4
  sleep 20
done
