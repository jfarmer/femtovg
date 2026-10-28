#!/bin/zsh
# The same study on the M4 Max efficiency cores (background QoS) with the Mac drivers
# (macdrv/macdrv_<v>, the phone library linked into a C main): plain runs (thread
# counters + MEM_PEAKS) and Instruments recordings with the three event sets.
# usage: run_mac.sh plain|rec ; resumable (skips existing outputs). Needs the sandbox off for xctrace.
source ${0:A:h}/common.sh
WHAT=$1; M=$RUNS/macdrv; C=/Users/matt/src/femtovg-pmu/corpus-focus
OUT=$RUNS/mac; mkdir -p $OUT/plain $OUT/rec
ls $C/c_*.svg > $OUT/list-c.txt; ls $C/b_*.svg > $OUT/list-b.txt
args() { # passes busey_passes
  echo curve $OUT/list-c.txt 1,2,4 $1 460 260 200 130 30 curvehd $OUT/list-c.txt 1 $1 1920 1080 1080 420 0 \
       busey $OUT/list-b.txt 1,2,4 $2 460 260 200 130 30 buseyhd $OUT/list-b.txt 1 $2 1920 1080 1080 420 0
}
# Recordings: the curve phases only plus one 1080p pass of the portraits (short traces: the disk is tight).
recargs() {
  echo curve $OUT/list-c.txt 1,2,4 6 460 260 200 130 30 curvehd $OUT/list-c.txt 1 6 1920 1080 1080 420 0 \
       buseyhd $OUT/list-b.txt 1 2 1920 1080 1080 420 0
}
if [[ $WHAT == plain ]]; then
  k=0
  for v in m a b c pp pc pc pp c b a m m a b c pp pc; do
    k=$((k+1)); r=$(( (k-1)/6 + 1 )); f=$OUT/plain/soak-$v-p$r.csv
    [ -f $f ] && continue
    wait_disk || exit 1
    T0=$(date +%s)
    MEM_PEAKS=1 $M/macdrv_$v $f $OUT/plain/sysinfo-$v.txt ${=$(args 10 4)} 2> $OUT/plain/console-$v-p$r.txt
    echo "mac plain $v p$r: rc $? in $(( $(date +%s)-T0 )) s, $(($(wc -l < $f)-1)) frames; load $(sysctl -n vm.loadavg)"
  done
fi
if [[ $WHAT == rec ]]; then
  for set in set1 set2 set3; do
    k=0
    for v in m a b c c b a m; do
      k=$((k+1)); r=$(( k <= 4 ? 1 : 2 )); TAG=$v-$set-r$r
      [ -f $OUT/rec/agg-$TAG.json ] && continue
      wait_disk || exit 1
      TR=$OUT/$TAG.trace; rm -rf $TR; T0=$(date +%s)
      xcrun xctrace record --template "CPU Counters" --recording-options $TPL/$set-options-cs.json --output $TR --time-limit 120s \
        --launch -- $M/macdrv_$v $OUT/rec/soak-$TAG.csv - ${=$(recargs)} > $OUT/rec/record-$TAG.txt 2>&1
      echo "mac rec $TAG: exit $? in $(( $(date +%s)-T0 )) s, trace $(du -sh $TR | cut -f1)"
      X='/trace-toc/run[@number="1"]/data/table'
      xcrun xctrace export --input $TR --xpath "${X}[@schema=\"OSSignpostIntervals\"]" > $OUT/rec/sp-$TAG.xml 2>/dev/null
      xcrun xctrace export --input $TR --xpath "${X}[@schema=\"counters-profile\"]" 2>/dev/null \
        | python3 $RUNS/scripts/agg_counters.py $OUT/rec/sp-$TAG.xml macdrv_$v "Main Thread" $OUT/rec/agg-$TAG.json
      rm -rf $TR
    done
  done
fi
