#!/bin/zsh
# Extra plain rounds on one phone (after run_device.sh): rounds FROM..TO, each round
# all six variants, alternating direction (m a b c pp pc / pc pp c b a m). More rounds
# put more frames of every variant into each E-core clock bin (dvfs.py).
# usage: run_more.sh a12|a14 FROM TO     (sandbox off; phone unlocked, on the cable)
source ${0:A:h}/common.sh
D=$1; FROM=$2; TO=$3; S=${0:A:h}
LOG=$RUNS/$D/run_device.log
exec > >(tee -a $LOG) 2>&1
echo "== $D more $FROM..$TO start $(date +%T)"
for r in $(seq $FROM $TO); do
  if (( r % 2 )); then order=(m a b c pp pc); else order=(pc pp c b a m); fi
  for v in $order; do
    [ -f $RUNS/$D/plain/soak-$v-p$r.csv ] && continue
    zsh $S/run_plain.sh $D $v $v-p$r; sleep 15
  done
done
echo "== $D more $FROM..$TO done $(date +%T)"
