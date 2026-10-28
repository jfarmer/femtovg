#!/bin/zsh
# One PMU recording of the arclen kernel on the A14 (CPU Counters, manual event set, 1 ms time sampling), exported and
# aggregated per signpost interval, trace deleted. A watchdog stops xctrace if the Mac's free space drops under LIMIT_KB.
# usage: rec.sh set1|set2|set3 <tag> <kinds> <variants> <rounds> <inner>
D=/Users/matt/src/femtovg-wt/runs/arclen; RP=/Users/matt/src/femtovg-wt/runs/phone-pmu
U=00008101-000A044A3C28801E; B=co.rbckr.arclenbench
S=$1; TAG=$2; KINDS=$3; VARS=$4; ROUNDS=$5; INNER=$6
OUT=$D/a14/rec; TR=$OUT/$TAG.trace; LIMIT_KB=${LIMIT_KB:-900000}
PM=/private/var/folders/_c/krb2zmbx2ss6b1xhpydpxcr80000gn/C/com.apple.dt.InstrumentsCLI/path_manager
rm -rf $TR; T0=$(date +%s); VENV=''; [ -n "$VARS" ] && VENV="--env ARC_VARIANTS=$VARS"
xcrun xctrace record --device $U --template "CPU Counters" --recording-options $RP/tpl/$S-options-cs.json --output $TR \
  --time-limit ${TL:-60}s --no-prompt \
  --env ARC_TAG=$TAG --env ARC_KINDS=$KINDS ${=VENV} --env ARC_ROUNDS=$ROUNDS --env ARC_INNER=$INNER \
  --env ARC_SIGNPOSTS=1 --env ARC_EXIT=1 --env ARC_DELAY_S=1 --env ARC_EXIT_DELAY_S=2 \
  --launch -- $B > $OUT/record-$TAG.txt 2>&1 &
XP=$!; low=0; minfree=99999999
while kill -0 $XP 2>/dev/null; do
  a=$(df -k / | tail -1 | awk '{print $4}'); [ $a -lt $minfree ] && minfree=$a
  if [ $a -lt $LIMIT_KB ]; then echo "disk under limit ($a KB): stopping xctrace"; kill -INT $XP; sleep 3; kill -9 $XP 2>/dev/null; low=1; fi
  sleep 1
done
echo "$S $TAG: recorded in $(( $(date +%s)-T0 )) s, trace $(du -sh $TR 2>/dev/null | cut -f1), min free $((minfree/1024)) MiB, low=$low; $(grep -E 'Error|error|ending' $OUT/record-$TAG.txt | head -2 | tr '\n' ' ')"
if [ $low = 0 ] && [ -d $TR ]; then
  X='/trace-toc/run[@number="1"]/data/table'
  xcrun xctrace export --input $TR --xpath "${X}[@schema=\"OSSignpostIntervals\"]" > $OUT/sp-$TAG.xml 2>/dev/null
  xcrun xctrace export --input $TR --xpath "${X}[@schema=\"counters-profile\"]" 2>/dev/null \
    | python3 $RP/scripts/agg_counters.py $OUT/sp-$TAG.xml ArclenBench arclen-bench $OUT/agg-$TAG.json
fi
rm -rf $TR
for d in $PM/xrtmp__*(N); do p=${${d:t}#xrtmp__}; p=${p%%.*}; kill -0 $p 2>/dev/null || rm -rf $d; done
xcrun devicectl device copy from --device $U --domain-type appDataContainer --domain-identifier $B --source Documents/arclen-$TAG.csv --destination $OUT/arclen-$TAG.csv >/dev/null 2>&1
df -h / | tail -1
