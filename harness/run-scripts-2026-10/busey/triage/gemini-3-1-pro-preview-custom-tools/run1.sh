#!/bin/zsh
# run1.sh SVG OUT.png [extra env...] : the mst2 binary at z2 with the sweep env, WITHOUT the forced SINGLE_SHADOW_LAYER unless passed
svg=$1; out=$2; shift 2
env FRAME_W=460 FRAME_H=260 BOX=200 BOX_X=130 BOX_Y=30 SKIP_UNSUPPORTED_FILTERS=1 VIEWPORT_CLIP=1 LAYER_STATS=1 TRANSIENT_BUDGET_MB=1024 "$@" \
  /Users/matt/src/femtovg-wt/bin/_logos_full_mst2 2 ${out%.png}.ppm $svg
python3 -c "from PIL import Image;import sys;Image.open(sys.argv[1]).save(sys.argv[2])" ${out%.png}.ppm $out && rm ${out%.png}.ppm
