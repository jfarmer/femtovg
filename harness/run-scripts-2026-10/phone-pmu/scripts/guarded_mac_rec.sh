#!/bin/zsh
# One short Mac recording with a disk watchdog: kills xctrace if free space drops
# under 1.2 GB, removes the trace and dead xctrace temp dirs afterwards.
# usage: guarded_mac_rec.sh <variant> <set> <tag>
source ${0:A:h}/common.sh
V=$1; S=$2; TAG=$3; M=$RUNS/macdrv; OUT=$RUNS/mac; TR=$OUT/$TAG.trace
PM=/private/var/folders/_c/krb2zmbx2ss6b1xhpydpxcr80000gn/C/com.apple.dt.InstrumentsCLI/path_manager
wait_disk || exit 1
rm -rf $TR
xcrun xctrace record --template "CPU Counters" --recording-options $TPL/$S-options-cs.json --output $TR --time-limit ${TL:-15}s \
  --launch -- $M/macdrv_$V $OUT/rec/soak-$TAG.csv - curve $OUT/list-c.txt 1,2,4 ${CP:-6} 460 260 200 130 30 curvehd $OUT/list-c.txt 1 ${HP:-10} 1920 1080 1080 420 0 \
  > $OUT/rec/record-$TAG.txt 2>&1 &
XP=$!; low=0
while kill -0 $XP 2>/dev/null; do
  a=$(df -k / | tail -1 | awk '{print $4}')
  if [ $a -lt 1258291 ]; then echo "disk under 1.2 GB: stopping xctrace"; kill -INT $XP; sleep 3; kill -9 $XP 2>/dev/null; low=1; fi
  sleep 1
done
echo "rec $TAG: trace $(du -sh $TR 2>/dev/null | cut -f1) low=$low"
if [ $low = 0 ] && [ -d $TR ]; then
  X='/trace-toc/run[@number="1"]/data/table'
  xcrun xctrace export --input $TR --xpath "${X}[@schema=\"OSSignpostIntervals\"]" > $OUT/rec/sp-$TAG.xml 2>/dev/null
  xcrun xctrace export --input $TR --xpath "${X}[@schema=\"counters-profile\"]" 2>/dev/null \
    | python3 $RUNS/scripts/agg_counters.py $OUT/rec/sp-$TAG.xml macdrv_$V "Main Thread" $OUT/rec/agg-$TAG.json
fi
rm -rf $TR
for d in $PM/xrtmp__*(N); do p=${${d:t}#xrtmp__}; p=${p%%.*}; kill -0 $p 2>/dev/null || rm -rf $d; done
df -h / | tail -1
