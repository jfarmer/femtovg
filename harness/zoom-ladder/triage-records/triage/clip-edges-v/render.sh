#!/bin/zsh
# render.sh BIN TAG key svgpath
export FRAME_W=460 FRAME_H=260 BOX=200 BOX_X=130 BOX_Y=30 SKIP_UNSUPPORTED_FILTERS=1 VIEWPORT_CLIP=1 TRANSIENT_BUDGET_MB=1024
bin=$1; tag=$2; key=$3; svg=$4
mkdir -p png/$tag/$key
for z in 0.25 0.33 0.5 0.75 1 1.25 1.5 1.75 2 3 4; do
  $bin $z png/$tag/$key/$z.ppm $svg >/dev/null 2>&1
  python3 -c "from PIL import Image; Image.open('png/$tag/$key/$z.ppm').save('png/$tag/$key/$z.png')" && rm png/$tag/$key/$z.ppm
done
