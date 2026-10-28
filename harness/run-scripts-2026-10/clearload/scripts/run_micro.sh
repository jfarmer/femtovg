#!/bin/zsh
# After round 2: the clear microbenchmarks on one device. ABBA of #368 head (pp) and the fold (pc) on the
# empty and eight-layer frames, then the diagnostic build (a) in each clear mode, in mirrored order.
# usage: [DIAG=1] run_micro.sh dev   (the clear modes only with DIAG=1)
D=$1; S=/Users/matt/src/femtovg-wt/runs/clearload/scripts
C=1; [[ $D == a12 || $D == atv10 ]] && C=
i=0
for V in pp pc pc pp; do i=$((i+1)); COUNTERS=$C $S/run_mst.sh $D $V m-$i-$V empty,emptyhd 20 1; sleep 10; done
[[ -z $DIAG ]] && exit 0
i=0
for M in quad load fold clearquad clearquad fold load quad; do
  i=$((i+1)); COUNTERS=$C XENV=FEMTOVG_CLEAR_MODE=$M $S/run_mst.sh $D a d-$i-$M empty,emptyhd 20 1; sleep 10
done
