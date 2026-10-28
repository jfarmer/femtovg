#!/bin/zsh
# run.sh BIN ZOOM OUT.png SVG [ENV=..]
bin=$1; z=$2; out=$3; svg=$4; shift 4
env FRAME_W=460 FRAME_H=260 BOX=200 BOX_X=130 BOX_Y=30 SKIP_UNSUPPORTED_FILTERS=1 VIEWPORT_CLIP=1 TRANSIENT_BUDGET_MB=1024 "$@" $bin $z ${out:r}.ppm $svg >/dev/null && python3 -c "from PIL import Image;import sys;Image.open(sys.argv[1]).save(sys.argv[2])" ${out:r}.ppm $out && rm ${out:r}.ppm
