#!/bin/zsh
# One run of the thin-fill phases on the iPhone without Instruments (the phone is on Wi-Fi, where a counters recording
# streams for minutes): the app's CSV row a frame carries the render thread's own instructions and cycles per CPU kind
# (thread_selfcounts), the process's, its energy and the frame's peak footprint.
# usage: run_fast.sh pp|a|pc TAG [phases] [passes] [repeat]; XENV=NAME=VALUE passes one more variable; a run that has
# not exited after RUN_TIMEOUT seconds (default 150) is stopped and said so. NOCONSOLE=1 launches without the console
# stream and polls for the app's exit.
U=${U:-00008140-000859503A2A801C}  # U= another device (XS Max A12 00008020-001C292A2190003A, SE A13 00008030-0005694926D3402E)
V=$1; TAG=$2; PH=${3:-thinhd,thin}; P=${4:-3}; REP=${5:-20}
B=co.rbckr.femtovgpmu.flat$V
OUT=${OUT:-/Users/matt/src/femtovg-wt/runs/raster/ios}; mkdir -p $OUT
T0=$(date +%s)
if [ -n "$NOCONSOLE" ]; then
  # Without --console: the app's stdout goes nowhere, so a stalled host stream (CoreDevice over Wi-Fi stalled both phones
  # at once twice on 2026-10-16, each app blocking on its next print) cannot hold it; the app exits by itself
  # (SOAK_EXIT=1) and is polled for.
  env DEVICECTL_CHILD_SOAK_TAG=$TAG DEVICECTL_CHILD_SOAK_PHASES=$PH DEVICECTL_CHILD_SOAK_PASSES=$P \
    DEVICECTL_CHILD_SOAK_REPEAT=$REP DEVICECTL_CHILD_FRAME_DRIFT=0.37 DEVICECTL_CHILD_MEM_PEAKS=1 DEVICECTL_CHILD_SOAK_EXIT=1 \
    DEVICECTL_CHILD_SOAK_DELAY_S=2 ${XENV:+DEVICECTL_CHILD_$XENV} \
    timeout 60 xcrun devicectl device process launch --terminate-existing --device $U $B > $OUT/launch-$TAG.txt 2>&1
  sleep 5
  while [ $(( $(date +%s)-T0 )) -lt ${RUN_TIMEOUT:-150} ] && timeout 30 xcrun devicectl device info processes --device $U 2>/dev/null | grep -qi "/${B##*.}\.app/"; do sleep 3; done
  [ $(( $(date +%s)-T0 )) -ge ${RUN_TIMEOUT:-150} ] && echo "$V $TAG: no exit after ${RUN_TIMEOUT:-150} s"
else
env DEVICECTL_CHILD_SOAK_TAG=$TAG DEVICECTL_CHILD_SOAK_PHASES=$PH DEVICECTL_CHILD_SOAK_PASSES=$P \
  DEVICECTL_CHILD_SOAK_REPEAT=$REP DEVICECTL_CHILD_FRAME_DRIFT=0.37 DEVICECTL_CHILD_MEM_PEAKS=1 DEVICECTL_CHILD_SOAK_EXIT=1 \
  DEVICECTL_CHILD_SOAK_DELAY_S=2 ${XENV:+DEVICECTL_CHILD_$XENV} \
  timeout ${RUN_TIMEOUT:-150} xcrun devicectl device process launch --console --terminate-existing --device $U $B > $OUT/launch-$TAG.txt 2>&1
[ $? = 124 ] && echo "$V $TAG: no exit after ${RUN_TIMEOUT:-150} s (last: $(grep -v '^$' $OUT/launch-$TAG.txt | tail -1))"
fi
grep -q "Launched application" $OUT/launch-$TAG.txt || { echo "$V $TAG: launch failed: $(grep -iE 'error|locked' $OUT/launch-$TAG.txt | head -2 | tr '\n' ' ')"; exit 1; }
for f in soak-$TAG.csv meta-$TAG.txt; do
  xcrun devicectl device copy from --device $U --domain-type appDataContainer --domain-identifier $B \
    --source Documents/$f --destination $OUT/$f >/dev/null 2>&1
done
if ls $OUT/soak-$TAG.csv >/dev/null 2>&1; then
  echo "$V $TAG: $(( $(date +%s)-T0 )) s, $(($(wc -l < $OUT/soak-$TAG.csv)-1)) frames; $(head -1 $OUT/meta-$TAG.txt | grep -oE 'battery=.*'); $(grep -E 'thermal' $OUT/meta-$TAG.txt | tail -1)"
else echo "$V $TAG: no CSV after $(( $(date +%s)-T0 )) s"; exit 1; fi
