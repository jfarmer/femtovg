#!/bin/zsh
# rec.sh BIN SET ITERS LABEL [patterns]: record the bench on the E-cores with the events template, print the totals.
B=$1; S=$2; N=$3; L=$4; P=${5:-'Coverage::resolve|sort|alloc|memset|memmove'}
rm -rf /tmp/claude-501/rec_$L.trace
xcrun xctrace record --template ~/src/femtovg-wt/runs/thin/tools/femtovg-events.tracetemplate --output /tmp/claude-501/rec_$L.trace --env RASTER_IMPL=${IMPL:-new} --env RASTER_BENCH=$S.dump --env RASTER_ITERS=$N --launch -- /usr/sbin/taskpolicy -c background $PWD/$B zz_raster_bench --ignored --nocapture 2>&1 | grep -E "RASTER [0-9]" | sed "s/^/$L: /"
xcrun xctrace export --input /tmp/claude-501/rec_$L.trace --xpath '/trace-toc/run[@number="1"]/data/table[@schema="counters-profile"]' 2>/dev/null > /tmp/claude-501/rec_$L.xml
LEAVES=${LEAVES:-0} python3 ~/src/femtovg-wt/runs/thin/tools/pmc_agg.py /tmp/claude-501/rec_$L.xml taskpolicy "$P" | sed "s/^/$L /"
rm -rf /tmp/claude-501/rec_$L.trace /tmp/claude-501/rec_$L.xml
