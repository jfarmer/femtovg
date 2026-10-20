#!/bin/zsh
# One soak of one variant on one phone without Instruments: per-frame thread
# counters + the footprint sampler (MEM_PEAKS=1). Waits for the app to exit.
# usage: run_plain.sh a12|a14 m|a|b|c|pp|pc <tag> [phases] [passes] [busey_passes]
source ${0:A:h}/common.sh
D=$1; V=$2; TAG=$3; PH=${4:-curve,curvehd,busey,buseyhd}; P=${5:-8}; BP=${6:-4}
OUT=$RUNS/$D/plain; mkdir -p $OUT
wait_disk || exit 1
T0=$(date +%s)
DEVICECTL_CHILD_SOAK_TAG=$TAG DEVICECTL_CHILD_SOAK_PHASES=$PH DEVICECTL_CHILD_SOAK_PASSES=$P DEVICECTL_CHILD_SOAK_BUSEY_PASSES=$BP \
DEVICECTL_CHILD_SOAK_EXIT=1 DEVICECTL_CHILD_MEM_PEAKS=1 \
  timeout ${PLAIN_TIMEOUT:-2400} xcrun devicectl device process launch --console --terminate-existing --device ${UDID[$D]} $(bundle $V) > $OUT/console-$TAG.txt 2>&1
echo "$D $V $TAG: exit $? after $(( $(date +%s)-T0 )) s; $(grep -c 'pass .* done' $OUT/console-$TAG.txt) passes logged"
for f in soak-$TAG.csv meta-$TAG.txt sysinfo.txt; do fetch $D $V $f $OUT; done
[ -f $OUT/sysinfo.txt ] && mv $OUT/sysinfo.txt $OUT/sysinfo-$V.txt
ls $OUT/soak-$TAG.csv >/dev/null 2>&1 && echo "  $(($(wc -l < $OUT/soak-$TAG.csv)-1)) frames; $(tr '\n' ' ' < $OUT/meta-$TAG.txt | cut -c1-400)"
