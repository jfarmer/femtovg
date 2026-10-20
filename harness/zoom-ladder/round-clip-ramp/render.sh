#!/bin/zsh
# render.sh BIN TAG KEY SVG ZOOM... : frames of the zoom-ladder framing (460 x 260, the 200-unit box at 130,30) into png/TAG/KEY/ZOOM.png
export FRAME_W=460 FRAME_H=260 BOX=200 BOX_X=130 BOX_Y=30 SKIP_UNSUPPORTED_FILTERS=1 VIEWPORT_CLIP=1 TRANSIENT_BUDGET_MB=1024
bin=$1; tag=$2; key=$3; svg=$4; shift 4
mkdir -p png/$tag/$key
for z in "$@"; do
  $bin $z png/$tag/$key/$z.ppm $svg >/dev/null 2>&1
  python3 -c "from PIL import Image; Image.open('png/$tag/$key/$z.ppm').save('png/$tag/$key/$z.png')" && rm png/$tag/$key/$z.ppm
done
