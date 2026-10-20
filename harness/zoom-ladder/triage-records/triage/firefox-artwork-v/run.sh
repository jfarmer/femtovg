#!/bin/zsh
# run.sh BIN ZOOM OUTPNG SVG [ENV=VAL...]
B=$1; Z=$2; O=$3; S=$4; shift 4
env FRAME_W=460 FRAME_H=260 BOX=200 BOX_X=130 BOX_Y=30 SKIP_UNSUPPORTED_FILTERS=1 VIEWPORT_CLIP=1 TRANSIENT_BUDGET_MB=1024 "$@" $B $Z ${O%.png}.ppm $S > ${O%.png}.log 2>&1
python3 -c "from PIL import Image; Image.open('${O%.png}.ppm').save('$O')" && rm ${O%.png}.ppm
