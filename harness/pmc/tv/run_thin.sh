#!/bin/zsh
# One run of the thin-fill phases on the A15 Apple TV ("team h") under the femtovg-events CPU counters template
# (mispredicts, L1D load/store and TLB misses, L1I misses, instructions, cycles, branches; 1 ms samples with the
# user stacks). The app runs its phases on background QoS - the efficiency cores - and writes a CSV row a frame with
# the render thread's own instructions and cycles per CPU kind and the frame's peak footprint.
# usage: run_thin.sh pp|pc TAG [phases] [passes] [repeat]     (pp = FlatPPTV = old rasterizer, pc = FlatPCTV = new)
# XENV=NAME=VALUE passes one more variable (e.g. NO_THIN_FILL_MASKS=1). Needs the sandbox off for xctrace.
U=00008110-00015D380283801E
V=$1; TAG=$2; PH=${3:-thinhd,thin}; P=${4:-3}; REP=${5:-20}
B=co.rbckr.femtovgpmu.flat$V
OUT=/Users/matt/src/femtovg-wt/runs/raster/tv; mkdir -p $OUT
TR=/tmp/claude-501/tv-$TAG.trace; rm -rf $TR
# An idle device is "offline" to xctrace: wake it with a launch that exits at once.
DEVICECTL_CHILD_SOAK_TAG=wake DEVICECTL_CHILD_SOAK_PHASES=none DEVICECTL_CHILD_SOAK_EXIT=1 \
  xcrun devicectl device process launch --terminate-existing --device $U $B >/dev/null 2>&1
sleep 3
T0=$(date +%s)
xcrun xctrace record --device $U --template /Users/matt/src/femtovg-wt/runs/thin/tools/femtovg-events.tracetemplate \
  --output $TR --time-limit ${TL:-300}s --no-prompt \
  --env SOAK_TAG=$TAG --env SOAK_PHASES=$PH --env SOAK_PASSES=$P --env SOAK_REPEAT=$REP --env FRAME_DRIFT=0.37 --env MEM_PEAKS=1 \
  --env SOAK_EXIT=1 --env SOAK_DELAY_S=2 ${XENV:+--env} ${XENV:+$XENV} \
  --launch -- $B > $OUT/record-$TAG.txt 2>&1
echo "$V $TAG: recorded in $(( $(date +%s)-T0 )) s, trace $(du -sh $TR 2>/dev/null | cut -f1); $(grep -E 'rror|ending|exited' $OUT/record-$TAG.txt | head -2 | tr '\n' ' ')"
if [ -d $TR ]; then
  xcrun xctrace export --input $TR --xpath '/trace-toc/run[@number="1"]/data/table[@schema="counters-profile"]' > /tmp/claude-501/tv-$TAG.xml 2>/dev/null
  LEAVES=${LEAVES:-0} python3 /Users/matt/src/femtovg-wt/runs/thin/tools/pmc_agg.py /tmp/claude-501/tv-$TAG.xml Flat \
    'fill_through_mask|MaskKey::rasterize|Coverage::resolve|upload_fill_masks|render_scene' > $OUT/pmc-$TAG.txt 2>&1
  rm -f /tmp/claude-501/tv-$TAG.xml
fi
rm -rf $TR
TMPD=/private/var/folders/_c/krb2zmbx2ss6b1xhpydpxcr80000gn
for k in $TMPD/T/instruments*.ktrace(N); do lsof $k >/dev/null 2>&1 || rm -f $k; done
for f in soak-$TAG.csv meta-$TAG.txt; do
  xcrun devicectl device copy from --device $U --domain-type appDataContainer --domain-identifier $B \
    --source Library/Caches/$f --destination $OUT/$f >/dev/null 2>&1
done
ls $OUT/soak-$TAG.csv >/dev/null 2>&1 && echo "  $(($(wc -l < $OUT/soak-$TAG.csv)-1)) frames; $(grep -E 'thermal' $OUT/meta-$TAG.txt | tail -1)"
