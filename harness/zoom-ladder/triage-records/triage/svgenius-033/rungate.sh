#!/bin/zsh
# rungate.sh ZOOM TAG  -- reads key\tpath lines on stdin, one per call via xargs
z=$1; tag=$2; key=$3; svg=$4
out=$PWD/gate_$tag/$key.png
[[ -f $out ]] && exit 0
env FRAME_W=460 FRAME_H=260 BOX=200 BOX_X=130 BOX_Y=30 SKIP_UNSUPPORTED_FILTERS=1 VIEWPORT_CLIP=1 TRANSIENT_BUDGET_MB=1024 FV_GATE_FIX=1 $PWD/bin/_logos_full_proof $z $PWD/gate_$tag/$key.ppm $svg >/dev/null 2>&1
python3 -c "from PIL import Image;import sys;Image.open(sys.argv[1]).save(sys.argv[2])" $PWD/gate_$tag/$key.ppm $out 2>/dev/null; rm -f $PWD/gate_$tag/$key.ppm
