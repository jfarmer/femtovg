#!/bin/zsh
# render.sh SVG ZOOM OUTPREFIX  -> OUTPREFIX_{fem.ppm,chr.png,area8.png,ff.png,wk.png}
svg=$1; z=$2; o=$3
export FRAME_W=460 FRAME_H=260 BOX=200 BOX_X=130 BOX_Y=30
CHR=~/.cache/puppeteer/chrome-headless-shell/mac_arm-131.0.6778.204/chrome-headless-shell-mac-arm64/chrome-headless-shell
FF='/Applications/Firefox Developer Edition.app/Contents/MacOS/firefox'
python3 ~/src/femtovg-wt/da/harness/make_ref.py $svg $z > ${o}.html
SKIP_UNSUPPORTED_FILTERS=1 VIEWPORT_CLIP=1 TRANSIENT_BUDGET_MB=1024 LAYER_STATS=1 ${FEMBIN:-$HOME/src/femtovg-wt/bin/_logos_full_zm2} $z ${o}_fem.ppm $svg > ${o}_stats.txt 2>&1
$CHR --headless --disable-gpu --hide-scrollbars --force-device-scale-factor=1 --window-size=460,260 --default-background-color=FFFFFFFF --screenshot=${o}_chr.png file://${o}.html >/dev/null 2>&1
$CHR --headless --disable-gpu --hide-scrollbars --force-device-scale-factor=8 --window-size=460,260 --default-background-color=FFFFFFFF --screenshot=${o}_area8.png file://${o}.html >/dev/null 2>&1
if [[ -z $NOFF ]]; then
prof=$(mktemp -d /tmp/ffprofXXXX)
"$FF" --headless --no-remote --profile $prof --window-size=460,260 --screenshot ${o}_ff.png file://${o}.html >/dev/null 2>&1
rm -rf $prof
fi
~/src/femtovg-wt/bin/wk_shot ${o}.html ${o}_wk.png 460 260 >/dev/null 2>&1
