#!/bin/zsh
# run.sh SVG OUTPNG FRAMING(z1|z2|hd) [extra env...]
svg=$1; out=$2; fr=$3; shift 3
case $fr in
  z1) F=(FRAME_W=460 FRAME_H=260 BOX=200 BOX_X=130 BOX_Y=30); Z=1;;
  z2) F=(FRAME_W=460 FRAME_H=260 BOX=200 BOX_X=130 BOX_Y=30); Z=2;;
  z4) F=(FRAME_W=460 FRAME_H=260 BOX=200 BOX_X=130 BOX_Y=30); Z=4;;
  hd) F=(FRAME_W=1920 FRAME_H=1080 BOX=1080 BOX_X=420 BOX_Y=0); Z=1;;
esac
env $F SKIP_UNSUPPORTED_FILTERS=1 VIEWPORT_CLIP=1 LAYER_STATS=1 TRANSIENT_BUDGET_MB=1024 "$@" /Users/matt/src/femtovg-wt/bin/_logos_full_mst4 $Z ${out%.png}.ppm $svg 2>${out%.png}.log
python3 -c "from PIL import Image;import sys;Image.open(sys.argv[1]).save(sys.argv[2])" ${out%.png}.ppm $out && rm ${out%.png}.ppm
