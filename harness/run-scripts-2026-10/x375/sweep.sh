#!/bin/zsh
# sweep.sh - per zoom: wait-phase page faults per frame and median frame time, for master, the PR head and the head
# with its results kept out of the captures' pool bucket (X_TAG).
med() { sort -n | awk '{a[NR]=$1} END {print a[int((NR+1)/2)]}'; }
one() { # build zoom [VAR=VALUE] -> "faults ms"
  local out; out=$(./runx.sh $1 $2 14 XFAULTS=1 $3)
  local faults=$(echo "$out" | grep '^XF' | tail -4 | sed -e 's/.*wait=\([0-9]*\).*/\1/' | med)
  local ms=$(echo "$out" | grep '^XF' | tail -8 | sed -e 's/.*ms=\([0-9.]*\).*/\1/' | med)
  echo "$faults $ms"
}
print "zoom | master faults ms | PR faults ms | PR+tag faults ms"
for z in ${@:-1 2 3 3.6 4 4.5 6}; do
  m=(); c=(); t=()
  for i in 1 2 3; do m+=("$(one xm $z A=1)"); c+=("$(one xc $z A=1)"); t+=("$(one xc $z X_TAG=1)"); done
  pick() { printf '%s\n' "$@" | sort -k2 -n | sed -n 2p; }
  print "$z | $(pick $m) | $(pick $c) | $(pick $t)"
done
