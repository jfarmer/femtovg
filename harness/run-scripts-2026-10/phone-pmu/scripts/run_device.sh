#!/bin/zsh
# The whole study on one phone: install, PLAINS (default 3) plain runs per variant (order m a b c pp pc,
# reversed, forward again),
# then RECS (default 1) recordings per variant and event set (same alternation per set).
# usage: run_device.sh a12|a14 [plain|rec|all] ; skips runs whose outputs exist (resumable).
# Run with the sandbox off. Before: unlock the phone, Auto-Lock off, keep it on the cable.
source ${0:A:h}/common.sh
D=$1; WHAT=${2:-all}; S=${0:A:h}
LOG=$RUNS/$D/run_device.log; mkdir -p $RUNS/$D
exec > >(tee -a $LOG) 2>&1
echo "== $D $WHAT start $(date +%T)"
if [[ $WHAT == all || $WHAT == plain ]]; then
  k=0; inst=0
  for v in m a b c pp pc pc pp c b a m m a b c pp pc; do
    k=$((k+1)); r=$(( (k-1)/6 + 1 ))
    [ $r -gt ${PLAINS:-3} ] && continue
    [ -f $RUNS/$D/plain/soak-$v-p$r.csv ] && continue
    [ $inst = 0 ] && { zsh $S/install_all.sh $D; inst=1; }
    zsh $S/run_plain.sh $D $v $v-p$r; sleep 15
  done
fi
if [[ $WHAT == all || $WHAT == rec ]]; then
  for set in set1 set2 set3; do
    k=0
    for v in m a b c pp pc pc pp c b a m; do
      k=$((k+1)); r=$(( k <= 6 ? 1 : 2 ))
      [ $r -gt ${RECS:-1} ] && continue
      [ -f $RUNS/$D/rec/agg-$v-$set-r$r.json ] && continue
      zsh $S/run_rec.sh $D $v $set $v-$set-r$r; sleep 10
    done
  done
fi
echo "== $D $WHAT done $(date +%T)"
