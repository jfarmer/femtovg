#!/bin/zsh
# One soak of one variant on one device under the GPU and Points of Interest instruments (+ Metal GPU Counters
# with COUNTERS=1): no template, so no resource-event signposts flood the device's log buffer (the Metal System
# Trace template lost the A14's first 42 s of frame signposts). Wakes the device first (an idle one is "offline"
# to xctrace: "Timed out waiting for device to boot"), exports the frame signposts, the GPU intervals and the
# counters, fetches the soak CSV, and deletes the trace and xctrace's temporary files (each recording leaves a
# 1.6-2.6 GB $TMPDIR/instruments*.ktrace behind, even a good one).
# usage: [COUNTERS=1] run_gpu.sh a18 pp|a|pc <tag> [phases] [passes] [busey_passes]
# pp = #368 head (be84a9a), pc = the clear-on-load fold, a = the diagnostic build (XENV=FEMTOVG_CLEAR_MODE=...).
# XENV=NAME=VALUE passes one more variable to the app. Run with the sandbox off.
source /Users/matt/src/femtovg-wt/runs/phone-pmu/scripts/common.sh
UDID[a18]=00008140-000859503A2A801C  # iPhone 16 Pro Max (A18 Pro), paired over Wi-Fi
# A tvOS app writes its results to Library/Caches.
fetch() { # dev variant name dir
  local src=Documents; [[ $1 == atv* ]] && src=Library/Caches
  xcrun devicectl device copy from --device ${UDID[$1]} --domain-type appDataContainer --domain-identifier $(bundle $2) \
    --source $src/$3 --destination $4/$3 >/dev/null 2>&1
}
D=$1; V=$2; TAG=$3; PH=${4:-curve,curvehd,buseyhd}; P=${5:-4}; BP=${6:-4}
CL=/Users/matt/src/femtovg-wt/runs/raster/ios
OUT=$CL/gpu-$D; mkdir -p $OUT
TR=$OUT/$TAG.trace
wait_disk || exit 1
rm -rf $TR
EXTRA=(); [[ -n $COUNTERS ]] && EXTRA=(--instrument 'Metal GPU Counters')
DEVICECTL_CHILD_SOAK_TAG=wake DEVICECTL_CHILD_SOAK_PHASES=none DEVICECTL_CHILD_SOAK_EXIT=1 \
  xcrun devicectl device process launch --terminate-existing --device ${UDID[$D]} $(bundle $V) >/dev/null 2>&1
sleep 3
T0=$(date +%s)
xcrun xctrace record --device ${UDID[$D]} --instrument 'GPU' --instrument 'Points of Interest' $EXTRA \
  --output $TR --time-limit ${TL:-150}s --no-prompt \
  --env SOAK_TAG=$TAG --env SOAK_PHASES=$PH --env FRAME_DRIFT=0.37 --env SOAK_REPEAT=${REP:-20} --env SOAK_PASSES=$P --env SOAK_BUSEY_PASSES=$BP --env SOAK_EXIT=1 --env SOAK_DELAY_S=2 \
  ${XENV:+--env} ${XENV:+$XENV} \
  --launch -- $(bundle $V) > $OUT/record-$TAG.txt 2>&1
echo "$D $V $TAG: recorded in $(( $(date +%s)-T0 )) s, trace $(du -sh $TR 2>/dev/null | cut -f1); $(grep -E 'rror|ending|exited' $OUT/record-$TAG.txt | head -2 | tr '\n' ' ')"
if [ -d $TR ]; then
  X='/trace-toc/run[@number="1"]/data/table'
  xcrun xctrace export --input $TR --toc > $OUT/toc-$TAG.xml 2>/dev/null
  for s in os-signpost metal-gpu-intervals; do
    xcrun xctrace export --input $TR --xpath "${X}[@schema=\"$s\"]" > $OUT/$s-$TAG.xml 2>/dev/null
  done
  if [[ -n $COUNTERS ]]; then
    xcrun xctrace export --input $TR --xpath "${X}[@schema=\"gpu-counter-value\"]" > $OUT/gpu-counter-value-$TAG.xml 2>/dev/null
    xcrun xctrace export --input $TR --xpath "${X}[@schema=\"gpu-counter-info\"]" > $OUT/gpu-counter-info-$TAG.xml 2>/dev/null
  fi
  gzip -f $OUT/*-$TAG.xml
fi
rm -rf $TR
TMPD=/private/var/folders/_c/krb2zmbx2ss6b1xhpydpxcr80000gn
for k in $TMPD/T/instruments*.ktrace(N); do lsof $k >/dev/null 2>&1 || rm -f $k; done
for d in $TMPD/C/com.apple.dt.InstrumentsCLI/path_manager/xrtmp__*(N); do p=${${d:t}#xrtmp__}; p=${p%%.*}; kill -0 $p 2>/dev/null || rm -rf $d; done
for f in soak-$TAG.csv meta-$TAG.txt; do fetch $D $V $f $OUT; done
ls $OUT/soak-$TAG.csv >/dev/null 2>&1 && echo "  $(($(wc -l < $OUT/soak-$TAG.csv)-1)) frames; $(grep -E 'thermal' $OUT/meta-$TAG.txt | tail -1)"
