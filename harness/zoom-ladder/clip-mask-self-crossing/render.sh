#!/bin/zsh
# render.sh BIN OUTDIR SVG...: each SVG at the ladder's eleven zooms, in the ladder's framing (a 200 px box in a
# 460 x 260 frame), to OUTDIR/<svg name>/<zoom>.png. BIN: a harness built from femtovg 06243b80 with all cfgs.
bin=$1; out=$2; shift 2
for svg in "$@"; do
  name=${svg:t:r}
  mkdir -p $out/$name
  for z in 0.25 0.33 0.5 0.75 1 1.25 1.5 1.75 2 3 4; do
    env FRAME_W=460 FRAME_H=260 BOX=200 BOX_X=130 BOX_Y=30 SKIP_UNSUPPORTED_FILTERS=1 VIEWPORT_CLIP=1 \
      TRANSIENT_BUDGET_MB=1024 $bin $z $out/$name/$z.ppm $svg >/dev/null 2>&1
    python3 -c "import sys; from PIL import Image; Image.open(sys.argv[1]).convert('RGB').save(sys.argv[2])" \
      $out/$name/$z.ppm $out/$name/$z.png && rm $out/$name/$z.ppm
  done
done
