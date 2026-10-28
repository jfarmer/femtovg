#!/bin/zsh
# Each file: masks off (image staging build), #408, + belt, + image staging, then back, under the events template.
S=/Users/matt/src/femtovg-wt/runs/raster/m4belt
C=/Users/matt/src/femtovg-wt/da/corpus
for f in dn:$C/firefox/diners.svg p84:$C/svgenius/medium/page_84_食物元素_37310_icon_33.svg; do
  k=${f%%:*}; p=${f#*:}; i=0
  for v in tfmt_off tfmc tfmb tfmt tfmt tfmb tfmc tfmt_off; do
    i=$((i+1)); b=${v%_off}
    if [ "$v" != "$b" ]; then $S/rec.sh $b $p $k-$i-$v off; else $S/rec.sh $b $p $k-$i-$v; fi
  done
done
echo "m4 done at $(date)"
