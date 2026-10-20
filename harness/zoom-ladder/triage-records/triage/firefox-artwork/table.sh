#!/bin/zsh
# table.sh PREFIX KEY variants...: px > 8/255 off the area reference per zoom (and ink difference)
P=$1; K=$2; shift 2
printf "%-5s" zoom; for v in "$@"; do printf "%14s" $v; done; printf " |%12s%12s%12s\n" chr ff wk
for fr in z025 z033 z05 z075 z1 z125 z15 z175 z2 z3 z4; do
  printf "%-5s" $fr
  for v in "$@"; do python3 cmp.py var/${P}_${v}_$fr.ppm area/id8_${K}_$fr.png | awk '{printf "%7s(%+5.1f)", $5, $11}'; done
  printf " |"
  for b in chr ff wk; do f=~/src/femtovg-wt/runs/zoom/fresh/refs/${b}_${K}_$fr.png; if [ -f $f ]; then python3 cmp.py $f area/id8_${K}_$fr.png | awk '{printf "%5s(%+5.1f)", $5, $11}'; else printf "%12s" -; fi; done
  echo
done
