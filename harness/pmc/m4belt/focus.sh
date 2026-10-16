#!/bin/zsh
# Frame-loop counters (ONLY render_scene|flush_to_output|::submit): masks off and on with image staging, ABBA, per file.
S=/Users/matt/src/femtovg-wt/runs/raster/m4belt
C=/Users/matt/src/femtovg-wt/da/corpus
for f in dn:$C/firefox/diners.svg p84:$C/svgenius/medium/page_84_食物元素_37310_icon_33.svg; do
  k=${f%%:*}; p=${f#*:}; i=0
  for v in tfmt_off tfmt tfmt tfmt_off; do
    i=$((i+1)); b=${v%_off}
    if [ "$v" != "$b" ]; then $S/rec.sh $b $p f$k-$i-$v off; else $S/rec.sh $b $p f$k-$i-$v; fi
  done
done
echo "focus done at $(date)"
