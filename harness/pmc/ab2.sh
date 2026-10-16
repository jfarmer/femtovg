#!/bin/zsh
# ab2.sh BIN_A BIN_B SET [ITERS] [ROUNDS]: alternate two bench binaries (new rasterizer) on the E-cores and the P-cores,
# printing each run's exact per-pass instructions and cycles, then the medians.
A=$1; B=$2; S=$3; N=${4:-200}; R=${5:-3}
for r in $(seq $R); do
  for b in $A $B; do
    e=$(RASTER_BENCH=$S.dump RASTER_ITERS=$N /usr/sbin/taskpolicy -c background ./$b zz_raster_bench --ignored --nocapture 2>&1 | grep COUNTS | sed 's/.*E \([0-9.]*\) M instr \([0-9.]*\) M cycles.*/\1 \2/')
    p=$(RASTER_BENCH=$S.dump RASTER_ITERS=$N ./$b zz_raster_bench --ignored --nocapture 2>&1 | grep COUNTS | sed 's/.*P \([0-9.]*\) M instr \([0-9.]*\) M cycles.*/\1 \2/')
    echo "$b $e $p"
  done
done | python3 -c "
import sys, statistics as st, collections
d=collections.defaultdict(list)
for l in sys.stdin:
    b,*v=l.split(); d[b].append(list(map(float,v)))
for b,rows in d.items():
    m=[st.median(c) for c in zip(*rows)]
    print(f'$S {b:12s} E {m[0]:7.3f} M instr {m[1]:7.3f} M cycles | P {m[2]:7.3f} M instr {m[3]:7.3f} M cycles  ({len(rows)} runs)')
"
