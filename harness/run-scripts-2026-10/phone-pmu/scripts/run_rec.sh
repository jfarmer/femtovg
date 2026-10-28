#!/bin/zsh
# One soak of one variant on one phone under CPU Counters in manual mode (event set and
# context-switch sampling from tpl/<set>-options-cs.json, passed with --recording-options);
# exports the counters-profile (streamed into a JSON aggregate), the signpost
# intervals and the TOC, then deletes the trace. A watchdog stops the recording if
# the Mac's free space drops under 1.2 GB (a Mac CPU Counters recording of ~15 s
# grew a 3-4 GB temporary store under InstrumentsCLI/path_manager), and dead
# xctrace temp stores are removed afterwards.
# usage: run_rec.sh a12|a14 m|a|b|c|pp|pc set1|set2|set3 <tag> [phases] [passes] [busey_passes]
# Run with the sandbox off (xctrace needs the device services and ktrace).
source ${0:A:h}/common.sh
D=$1; V=$2; S=$3; TAG=$4; PH=${5:-curve,curvehd,buseyhd}; P=${6:-5}; BP=${7:-3}
OUT=$RUNS/$D/rec; mkdir -p $OUT
TR=$RUNS/$D/$TAG.trace
PM=/private/var/folders/_c/krb2zmbx2ss6b1xhpydpxcr80000gn/C/com.apple.dt.InstrumentsCLI/path_manager
wait_disk || exit 1
rm -rf $TR
T0=$(date +%s)
xcrun xctrace record --device ${UDID[$D]} --template "CPU Counters" --recording-options $TPL/$S-options-cs.json --output $TR \
  --time-limit ${TL:-90}s --no-prompt \
  --env SOAK_TAG=$TAG --env SOAK_PHASES=$PH --env SOAK_PASSES=$P --env SOAK_BUSEY_PASSES=$BP --env SOAK_EXIT=1 --env SOAK_DELAY_S=1 \
  --launch -- $(bundle $V) > $OUT/record-$TAG.txt 2>&1 &
XP=$!; low=0
while kill -0 $XP 2>/dev/null; do
  a=$(df -k / | tail -1 | awk '{print $4}')
  if [ $a -lt 1258291 ]; then echo "disk under 1.2 GB: stopping xctrace"; kill -INT $XP; sleep 3; kill -9 $XP 2>/dev/null; low=1; fi
  sleep 1
done
echo "$D $V $S $TAG: recorded in $(( $(date +%s)-T0 )) s, trace $(du -sh $TR 2>/dev/null | cut -f1) low=$low; $(grep -E 'Error|error|ending' $OUT/record-$TAG.txt | head -2 | tr '\n' ' ')"
if [ $low = 0 ] && [ -d $TR ]; then
  X='/trace-toc/run[@number="1"]/data/table'
  xcrun xctrace export --input $TR --toc > $OUT/toc-$TAG.xml 2>/dev/null
  xcrun xctrace export --input $TR --xpath "${X}[@schema=\"OSSignpostIntervals\"]" > $OUT/sp-$TAG.xml 2>/dev/null
  xcrun xctrace export --input $TR --xpath "${X}[@schema=\"counters-profile\"]" 2>/dev/null \
    | python3 $RUNS/scripts/agg_counters.py $OUT/sp-$TAG.xml ${TGT[$V]} femtovg-soak $OUT/agg-$TAG.json
fi
rm -rf $TR
for d in $PM/xrtmp__*(N); do p=${${d:t}#xrtmp__}; p=${p%%.*}; kill -0 $p 2>/dev/null || rm -rf $d; done
for f in soak-$TAG.csv meta-$TAG.txt; do fetch $D $V $f $OUT; done
ls $OUT/soak-$TAG.csv >/dev/null 2>&1 && echo "  $(($(wc -l < $OUT/soak-$TAG.csv)-1)) frames; $(grep -E 'thermal' $OUT/meta-$TAG.txt | tail -1)"
