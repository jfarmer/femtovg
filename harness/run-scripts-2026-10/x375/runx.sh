#!/bin/zsh
# runx.sh BUILD ZOOM FRAMES [VAR=VALUE ...] - like run1.sh but prints every stderr line that starts with XF or MEM
b=$1; z=$2; n=$3; shift; shift; shift
f=${SVG:-/Users/matt/src/femtovg-wt/da/corpus/buseybench/glm-5-3.svg}
env FRAME_W=${FRAME_W:-460} FRAME_H=${FRAME_H:-260} BOX=${BOX:-200} BOX_X=${BOX_X:-130} BOX_Y=${BOX_Y:-30} SKIP_UNSUPPORTED_FILTERS=1 VIEWPORT_CLIP=1 TRANSIENT_BUDGET_MB=1024 MEM_PEAKS=1 MEM_SETTLE_MS=0 FRAMES=$n "$@" /Users/matt/src/femtovg-wt/bin/_logos_full_$b $z /Users/matt/src/femtovg-wt/runs/x375/out_$b.ppm $f 2>&1 | grep -E '^XF|frame_ms' | sed -e 's/^MEM.*frame_ms=\([0-9.]*\).*/frame_ms=\1/'
