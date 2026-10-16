#!/bin/zsh
# ab.sh SET ITERS ROUNDS: alternate the old and the new rasterizer on the E-cores (taskpolicy background) and the
# P-cores, printing each run's exact per-pass instructions and cycles.
S=$1; N=${2:-200}; R=${3:-3}
for r in $(seq $R); do
  for impl in old new; do
    e=$(RASTER_IMPL=$impl RASTER_BENCH=$S.dump RASTER_ITERS=$N /usr/sbin/taskpolicy -c background ./${BIN:-bench_ab} zz_raster_bench --ignored --nocapture 2>&1 | grep COUNTS | sed 's/.*E \([0-9.]*\) M instr \([0-9.]*\) M cycles.*/\1 \2/')
    p=$(RASTER_IMPL=$impl RASTER_BENCH=$S.dump RASTER_ITERS=$N ./${BIN:-bench_ab} zz_raster_bench --ignored --nocapture 2>&1 | grep COUNTS | sed 's/.*P \([0-9.]*\) M instr \([0-9.]*\) M cycles.*/\1 \2/')
    echo "$S $impl E-instr/cycles $e P-instr/cycles $p"
  done
done
