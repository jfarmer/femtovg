#!/bin/zsh
# Per-frame geometry counts (anatomy probe, master cc0d841 + probe patch, FEMTOVG_TESS_TOL)
# for every focused-corpus file at each framing and tolerance; one process per frame.
D=/Users/matt/src/femtovg-wt/runs/phone-pmu/macdrv/macdrv_probe
OUT=/Users/matt/src/femtovg-wt/runs/phone-pmu/points/probe.tsv
: > $OUT
for f in /Users/matt/src/femtovg-pmu/corpus-focus/*.svg; do
  echo $f > one.txt; n=${f:t:r}
  for tol in 0.25 0.125 0.0625; do
    for spec in "small 1" "small 2" "small 4" "hd 1"; do
      set -- ${=spec}
      if [ $1 = small ]; then geo=(460 260 200 130 30); else geo=(1920 1080 1080 420 0); fi
      line=$(FEMTOVG_PROBE=1 FEMTOVG_TESS_TOL=$tol $D $1 one.txt /dev/null $2 1 $geo 2>&1 | grep '^PROBE')
      echo "$n\t$1\t$2\t$tol\t$line" >> $OUT
    done
  done
done
wc -l $OUT
