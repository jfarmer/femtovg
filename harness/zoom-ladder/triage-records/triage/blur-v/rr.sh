#!/bin/zsh
# rr.sh BIN TAG : render the (a) files at zoom 0.5 and the repro at zoom 1 with BIN
B=$1; T=$2; mkdir -p out
for f in wpt-fegaussianblur-reftests/blur-variation-4-4-15 wpt-fegaussianblur-reftests/blur-variation-6-4-11 wpt-layer-blur-reftests/2d.layer.anisotropic-blur.isotropic wpt-fegaussianblur-reftests/blur-variation-6-2-17 wpt-fegaussianblur-reftests/blur-variation-3-3-14 wpt-fegaussianblur-reftests/blur-variation-5-3-22; do
  n=${f:t}
  for z in 0.5 0.75 0.33 0.25; do
    FRAME_W=460 FRAME_H=260 BOX=200 BOX_X=130 BOX_Y=30 SKIP_UNSUPPORTED_FILTERS=1 VIEWPORT_CLIP=1 TRANSIENT_BUDGET_MB=1024 $B $z out/$T.$n.$z.ppm ~/src/femtovg-wt/da/corpus/$f.svg >/dev/null 2>&1
  done
done
FRAME_W=460 FRAME_H=260 BOX=200 BOX_X=130 BOX_Y=30 SKIP_UNSUPPORTED_FILTERS=1 VIEWPORT_CLIP=1 TRANSIENT_BUDGET_MB=1024 $B 3 out/$T.bigblur.3.ppm ~/src/femtovg-wt/da/corpus/probes/bigblur.svg >/dev/null 2>&1
