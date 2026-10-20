#!/bin/zsh
# render.sh NAME ZOOM : femtovg harness + Chromium DSF1 + Chromium DSF8 (box-downsampled)
set -e
N=$1; Z=$2
CH=~/.cache/puppeteer/chrome-headless-shell/mac_arm-131.0.6778.204/chrome-headless-shell-mac-arm64/chrome-headless-shell
export FRAME_W=460 FRAME_H=260 BOX=200 BOX_X=130 BOX_Y=30
python3 ~/src/femtovg-wt/da/harness/make_ref.py $PWD/$N.svg $Z > $N.$Z.html
$CH --headless --disable-gpu --hide-scrollbars --force-device-scale-factor=1 --window-size=460,260 --screenshot=$PWD/$N.$Z.chr.png file://$PWD/$N.$Z.html >/dev/null 2>&1
$CH --headless --disable-gpu --hide-scrollbars --force-device-scale-factor=8 --window-size=460,260 --screenshot=$PWD/$N.$Z.chr8.png file://$PWD/$N.$Z.html >/dev/null 2>&1
python3 -c "
from PIL import Image; import numpy as np, sys
a=np.asarray(Image.open('$N.$Z.chr8.png').convert('RGB')).astype(float)
h,w=a.shape[0]//8,a.shape[1]//8
Image.fromarray(np.round(a[:h*8,:w*8].reshape(h,8,w,8,3).mean(axis=(1,3))).astype(np.uint8)).save('$N.$Z.area.png')"
BIN=${BIN:-~/src/femtovg-wt/bin/_logos_full_zm2}
SKIP_UNSUPPORTED_FILTERS=1 VIEWPORT_CLIP=1 TRANSIENT_BUDGET_MB=1024 $BIN $Z $N.$Z.fvg.ppm $PWD/$N.svg >/dev/null 2>&1
python3 -c "from PIL import Image; Image.open('$N.$Z.fvg.ppm').save('$N.$Z.fvg.png')"
