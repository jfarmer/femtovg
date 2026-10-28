#!/bin/zsh
# Frame-loop counters of the masks kept transposed (tfrvt) against the masks as before (tfrvs) and the masks off,
# ABCCBA, on the efficiency cores and then the performance cores.
S=/Users/matt/src/femtovg-wt/runs/raster/m4belt
C=/Users/matt/src/femtovg-wt/da/corpus
for core in e p; do
  for f in p84:$C/svgenius/medium/page_84_食物元素_37310_icon_33.svg dn:$C/firefox/diners.svg; do
    k=${f%%:*}; p=${f#*:}; i=0
    for v in tfrvs_off tfrvs tfrvt tfrvt tfrvs tfrvs_off; do
      i=$((i+1)); b=${v%_off}; pc=; [ $core = p ] && pc=1
      if [ "$v" != "$b" ]; then PCORE=$pc $S/rec.sh $b $p t$core$k-$i-$v off; else PCORE=$pc $S/rec.sh $b $p t$core$k-$i-$v; fi
    done
  done
done
echo "transpose done at $(date)"
