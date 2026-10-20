#!/bin/zsh
# wk.sh ZOOM OUT.png SVG
Z=$1; O=$2; S=$3
H=${O%.png}.html
FRAME_W=460 FRAME_H=260 BOX=200 BOX_X=130 BOX_Y=30 python3 ~/src/femtovg-wt/da/harness/make_ref.py $S $Z > $H
~/src/femtovg-wt/bin/wk_shot $H $O 460 260 >/dev/null 2>&1
rm $H
