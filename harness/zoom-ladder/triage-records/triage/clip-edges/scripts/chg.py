# chg.py SVG ZOOM OUT.png : GPU Chromium at one device pixel per CSS pixel
import sys, os, subprocess
CHR = os.path.expanduser('~/.cache/puppeteer/chrome-headless-shell/mac_arm-131.0.6778.204/chrome-headless-shell-mac-arm64/chrome-headless-shell')
GPU = ['--enable-gpu', '--use-angle=metal', '--enable-gpu-rasterization', '--ignore-gpu-blocklist']
svg, z, out = sys.argv[1:4]
env = {**os.environ, 'FRAME_W': '460', 'FRAME_H': '260', 'BOX': '200', 'BOX_X': '130', 'BOX_Y': '30'}
html = out[:-4] + '.html'
open(html, 'w').write(subprocess.run([sys.executable, os.path.expanduser('~/src/femtovg-wt/da/harness/make_ref.py'), svg, z], capture_output=True, text=True, env=env, check=True).stdout)
subprocess.run([CHR, '--headless', *GPU, '--hide-scrollbars', '--force-device-scale-factor=1', '--window-size=460,260', '--default-background-color=FFFFFFFF', f'--screenshot={out}', f'file://{os.path.abspath(html)}'], capture_output=True, timeout=120)
os.remove(html)
