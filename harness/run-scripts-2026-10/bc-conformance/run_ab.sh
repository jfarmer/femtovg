#!/bin/zsh
export CORPUS_RUN_OUT=~/src/femtovg-wt/runs/pr
C=~/src/femtovg-wt/da/harness/corpus_run
O=~/src/femtovg-wt/runs/bc-conformance
waitdisk() { for i in {1..45}; do avail=$(df -k / | tail -1 | awk '{print $4}'); [ $avail -gt 1572864 ] && return; sleep 20; done; }
for p in "m7 fb" "m7 fc" "m7f fb" "m7 m7f" "fb fc"; do
  set -- ${=p}
  waitdisk
  python3 $C/ab_refs.py $1 $2 refs=id,wk,chg,chr,ff worst=60 > $O/ab_$1_$2.txt 2>&1
  echo "ab $1 $2 exit $?" >> $O/ab_progress.log
done
for p in "m7 fb" "m7 fc" "m7f fb" "m7 m7f"; do
  set -- ${=p}
  python3 $C/vs_area.py $1 $2 > $O/vsarea_$1_$2.txt 2>&1
  echo "vs_area $1 $2 exit $?" >> $O/ab_progress.log
done
for p in "m7 fb" "m7 fc" "m7 m7f"; do
  set -- ${=p}
  python3 $C/reftest_counts.py $1 $2 > $O/reftest_$1_$2.txt 2>&1
  echo "reftest $1 $2 exit $?" >> $O/ab_progress.log
done
echo ALLDONE >> $O/ab_progress.log
