# area.py SVG ZOOM OUTNAME [dsf]: Chromium page at DSF (default 8), box-downsampled to 460x260.
import sys, os, subprocess, numpy as np
from PIL import Image
D='/Users/matt/src/femtovg-wt/runs/zoom/triage/feoffset/'
CH='/Users/matt/.cache/puppeteer/chrome-headless-shell/mac_arm-131.0.6778.204/chrome-headless-shell-mac-arm64/chrome-headless-shell'
svg, z, name = sys.argv[1], sys.argv[2], sys.argv[3]
dsf = int(sys.argv[4]) if len(sys.argv) > 4 else 8
env = dict(os.environ, FRAME_W='460', FRAME_H='260', BOX='200', BOX_X='130', BOX_Y='30')
page = f'{D}pages/{name}.html'
if not (len(sys.argv) > 5 and sys.argv[5] == 'raw'):
    html = subprocess.run(['python3', '/Users/matt/src/femtovg-wt/da/harness/make_ref.py', svg, z], env=env, capture_output=True, text=True, check=True).stdout
    open(page, 'w').write(html)
else:
    page = svg
tmp = f'{D}area/_tmp_{name}.png'
subprocess.run([CH, '--headless', '--disable-gpu', '--hide-scrollbars', f'--force-device-scale-factor={dsf}', '--window-size=460,260',
                f'--screenshot={tmp}', 'file://' + page], capture_output=True, check=True)
a = np.asarray(Image.open(tmp).convert('RGBA')).astype(np.float64)
os.remove(tmp)
if dsf > 1:
    a = a.reshape(260, dsf, 460, dsf, 4).mean(axis=(1, 3))
Image.fromarray(np.round(a).astype(np.uint8)).save(f'{D}area/{name}.png')
