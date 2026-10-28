#!/bin/zsh
# sweep2.sh ZOOM... - per zoom, for master (xm), the PR head (xc) and the head with the pool fix (xf): stencil textures
# and render passes per frame (trace), page faults per frame while the submit is in flight, median frame ms (untraced).
med() { sort -n | awk '{a[NR]=$1} END {print a[int((NR+1)/2)]}'; }
print "zoom build passes stencils faults ms"
for z in "$@"; do
  for b in xm xc xf; do
    rm -f tr_$b.txt; ./run1.sh $b $z 5 PASS_TRACE=$PWD/tr_$b.txt > /dev/null
    counts=$(python3 tl.py tr_$b.txt 3 | sed -e 's/.*passes=\([0-9]*\).*stencils=\([0-9]*\).*/\1 \2/')
    f=(); m=()
    for i in 1 2 3; do
      out=$(./runx.sh $b $z 14 XFAULTS=1)
      f+=($(echo "$out" | grep '^XF' | tail -4 | sed -e 's/.*wait=\([0-9]*\).*/\1/' | med))
      m+=($(echo "$out" | grep '^XF' | tail -8 | sed -e 's/.*ms=\([0-9.]*\).*/\1/' | med))
    done
    print "$z $b $counts $(printf '%s\n' $f | med) $(printf '%s\n' $m | med)"
  done
done
rm -f tr_x?.txt
