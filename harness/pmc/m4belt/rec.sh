#!/bin/zsh
# rec.sh BUILD FILE TAG [off]: one harness run of FILE at 1080p in motion (600 frames, FRAME_DRIFT=0.37) on the M4's
# efficiency cores under the femtovg-events template; prints the counters per core kind and per function.
# BUILD = tfmc (#408) | tfmb (+ frame-setup belt) | tfmt (+ image staging); off = NO_THIN_FILL_MASKS=1.
# PCORE=1 runs it at its default QoS, on the performance cores, instead of clamped to the efficiency cores.
BIN=/Users/matt/src/femtovg-wt/bin/_logos_full_$1; F=$2; L=$3
OUT=/Users/matt/src/femtovg-wt/runs/raster/m4belt; TR=/tmp/claude-501/m4_$L.trace; rm -rf $TR
CLAMP=(/usr/sbin/taskpolicy -c background); [ -n "$PCORE" ] && CLAMP=()
xcrun xctrace record --template /Users/matt/src/femtovg-wt/runs/thin/tools/femtovg-events.tracetemplate --output $TR --no-prompt \
  --env FRAME_W=1920 --env FRAME_H=1080 --env BOX=1080 --env BOX_X=420 --env BOX_Y=0 --env SKIP_UNSUPPORTED_FILTERS=1 \
  --env VIEWPORT_CLIP=1 --env LAYER_STATS=1 --env TRANSIENT_BUDGET_MB=1024 --env SINGLE_SHADOW_LAYER=1 --env FRAMES=600 \
  --env FRAME_DRIFT=0.37 --env MEM_PEAKS=1 ${4:+--env} ${4:+NO_THIN_FILL_MASKS=1} \
  --launch -- $CLAMP $BIN 1 /tmp/claude-501/m4_$L.ppm $F > $OUT/record-$L.txt 2>&1
TMPD=/private/var/folders/_c/krb2zmbx2ss6b1xhpydpxcr80000gn
echo "$L: trace $(du -sh $TR 2>/dev/null | cut -f1), ktrace temp $(du -ch $TMPD/T/instruments*.ktrace(N) 2>/dev/null | tail -1 | cut -f1)"
xcrun xctrace export --input $TR --xpath '/trace-toc/run[@number="1"]/data/table[@schema="counters-profile"]' > /tmp/claude-501/m4_$L.xml 2>/dev/null
P='fill_through_mask|MaskKey::rasterize|Coverage::resolve|upload_fill_masks|write_texture|write_buffer|StagingBelt|submit|update_image|flush'
for proc in _logos_full taskpolicy; do
  LEAVES=${LEAVES:-10} python3 /Users/matt/src/femtovg-wt/runs/thin/tools/pmc_agg.py /tmp/claude-501/m4_$L.xml $proc "$P" > $OUT/pmc-$L.txt 2>&1
  [ -s $OUT/pmc-$L.txt ] && break
done
# The frame loop alone (render_scene, the flush, the submit), without the start-up.
ONLY='render_scene|flush_to_output|::submit' LEAVES=${LEAVES:-10} python3 /Users/matt/src/femtovg-wt/runs/thin/tools/pmc_agg.py /tmp/claude-501/m4_$L.xml $proc "$P" > $OUT/pmcf-$L.txt 2>&1
rm -rf $TR /tmp/claude-501/m4_$L.xml /tmp/claude-501/m4_$L.ppm
for k in $TMPD/T/instruments*.ktrace(N); do lsof $k >/dev/null 2>&1 || rm -f $k; done
