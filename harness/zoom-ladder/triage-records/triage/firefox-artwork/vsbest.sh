#!/bin/zsh
# vsbest.sh PREFIX KEY variants...: px > 8/255 off the best browser (min of chr/ff/wk) per zoom
P=$1; K=$2; shift 2
printf "%-5s" zoom; for v in "$@"; do printf "%16s" $v; done; echo
for fr in z025 z033 z05 z075 z1 z125 z15 z175 z2 z3 z4; do
  printf "%-5s" $fr
  for v in "$@"; do
    best=99999; bb=-
    for b in chr ff wk; do f=~/src/femtovg-wt/runs/zoom/fresh/refs/${b}_${K}_$fr.png; [ -f $f ] || continue; n=$(python3 cmp.py var/${P}_${v}_$fr.ppm $f | awk '{print $5}'); if [ $n -lt $best ]; then best=$n; bb=$b; fi; done
    printf "%12s %-3s" $best $bb
  done; echo
done
