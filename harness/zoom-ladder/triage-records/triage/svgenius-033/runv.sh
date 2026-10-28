#!/bin/zsh
# runv.sh ZOOM DIR GATE(0|1) KEY SVG
z=$1; dir=$2; g=$3; key=$4; svg=$5
out=$PWD/$dir/$key.png
[[ -f "$out" ]] && exit 0
extra=(); [[ $g == 1 ]] && extra=(FV_GATE_FIX=1)
env FRAME_W=460 FRAME_H=260 BOX=200 BOX_X=130 BOX_Y=30 SKIP_UNSUPPORTED_FILTERS=1 VIEWPORT_CLIP=1 TRANSIENT_BUDGET_MB=1024 $extra $PWD/bin/_logos_full_proof $z "$PWD/$dir/$key.ppm" "$svg" >/dev/null 2>&1
python3 -c "from PIL import Image;import sys;Image.open(sys.argv[1]).save(sys.argv[2])" "$PWD/$dir/$key.ppm" "$out" 2>/dev/null; rm -f "$PWD/$dir/$key.ppm"
