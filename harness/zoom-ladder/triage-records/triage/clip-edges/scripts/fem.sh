#!/bin/zsh
# fem.sh BIN ZOOM OUT.png SVG [ENV=..]
B=$1; Z=$2; O=$3; S=$4; shift 4
env FRAME_W=460 FRAME_H=260 BOX=200 BOX_X=130 BOX_Y=30 SKIP_UNSUPPORTED_FILTERS=1 VIEWPORT_CLIP=1 TRANSIENT_BUDGET_MB=1024 "$@" $B $Z ${O%.png}.ppm $S >/dev/null 2>&1
python3 -c "from PIL import Image; import sys; Image.open(sys.argv[1]).convert('RGB').save(sys.argv[2])" ${O%.png}.ppm $O && rm ${O%.png}.ppm
