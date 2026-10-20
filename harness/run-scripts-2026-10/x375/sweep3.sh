#!/bin/zsh
# sweep3.sh SVG FRAMING ZOOM... - per zoom, for builds u13 (upstream master) and u13f (master + pool fix), three runs of
# 14 frames: render passes and stencil textures per frame, page faults while the GPU runs it, and the median frame ms.
svg=$1; framing=$2; shift 2
if [ $framing = hd ]; then fenv=(FRAME_W=1920 FRAME_H=1080 BOX=1080 BOX_X=420 BOX_Y=0); else fenv=(FRAME_W=460 FRAME_H=260 BOX=200 BOX_X=130 BOX_Y=30); fi
med() { sort -n | awk '{a[NR]=$1} END {print a[int((NR+1)/2)]}'; }
for z in "$@"; do
  for b in u13 u13f; do
    f=(); m=(); xs=""
    for i in 1 2 3; do
      out=$(env $fenv SKIP_UNSUPPORTED_FILTERS=1 VIEWPORT_CLIP=1 TRANSIENT_BUDGET_MB=1024 FRAMES=14 XFAULTS=1 XSTATS=1 \
            /Users/matt/src/femtovg-wt/bin/_logos_full_$b $z /Users/matt/src/femtovg-wt/runs/x375/o_$b.ppm $svg 2>&1)
      xs=$(echo "$out" | grep '^XS' | tail -1)
      f+=($(echo "$out" | grep '^XF' | tail -4 | sed -e 's/.*wait=\([0-9]*\).*/\1/' | med))
      m+=($(echo "$out" | grep '^XF' | tail -8 | sed -e 's/.*ms=\([0-9.]*\).*/\1/' | med))
    done
    print "$(basename $svg .svg) $framing z$z $b ${xs#XS } faults=$(printf '%s\n' $f | med) ms=$(printf '%s\n' $m | med)"
  done
done
rm -f /Users/matt/src/femtovg-wt/runs/x375/o_*.ppm
