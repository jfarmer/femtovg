#!/bin/bash
# run.sh BIN ZOOM OUT SVG [extra env]
BIN=$1; Z=$2; OUT=$3; SVG=$4
env FRAME_W=${FRAME_W:-460} FRAME_H=${FRAME_H:-260} BOX=${BOX:-200} BOX_X=${BOX_X:-130} BOX_Y=${BOX_Y:-30} SKIP_UNSUPPORTED_FILTERS=1 VIEWPORT_CLIP=1 TRANSIENT_BUDGET_MB=1024 $BIN $Z $OUT.ppm $SVG >/dev/null 2>&1
python3 -c "from PIL import Image; Image.open('$OUT.ppm').save('$OUT.png')" && rm $OUT.ppm
