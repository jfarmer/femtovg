#!/bin/zsh
# A14 follow-up after run_device.sh a14 rec: the set2b event set (set2 is refused on
# the A14), retries of recordings that failed (device connection), extra plain rounds.
source ${0:A:h}/common.sh
S=${0:A:h}; D=a14
exec > >(tee -a $RUNS/$D/run_device.log) 2>&1
echo "== a14 followup start $(date +%T)"
for v in m a b c pp pc; do
  [ -f $RUNS/$D/rec/agg-$v-set2b-r1.json ] || { zsh $S/run_rec.sh $D $v set2b $v-set2b-r1; sleep 10; }
done
for set in set1 set3; do for v in m a b c pp pc; do
  [ -f $RUNS/$D/rec/agg-$v-$set-r1.json ] || { zsh $S/run_rec.sh $D $v $set $v-$set-r1; sleep 10; }
done; done
echo "== a14 followup recs done $(date +%T)"
zsh $S/run_more.sh $D 4 ${MORE_TO:-6}
