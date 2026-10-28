#!/bin/zsh
# chr.sh page.html out.png [dsf]
dsf=${3:-1}
~/.cache/puppeteer/chrome-headless-shell/mac_arm-131.0.6778.204/chrome-headless-shell-mac-arm64/chrome-headless-shell --headless --disable-gpu --hide-scrollbars --force-device-scale-factor=$dsf --window-size=460,260 --screenshot=$2 file://$PWD/$1 >/dev/null 2>&1
