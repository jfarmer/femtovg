# area.py SVG ZOOM OUT.png [sw|gpu] [scale]: Chromium at SCALE device px per CSS px, block-averaged.
import sys, os, subprocess, numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
CHR = os.path.expanduser('~/.cache/puppeteer/chrome-headless-shell/mac_arm-131.0.6778.204/chrome-headless-shell-mac-arm64/chrome-headless-shell')
GPU = ['--enable-gpu', '--use-angle=metal', '--enable-gpu-rasterization', '--ignore-gpu-blocklist']
svg, z, out = sys.argv[1], sys.argv[2], sys.argv[3]
mode = sys.argv[4] if len(sys.argv) > 4 else 'sw'; S = int(sys.argv[5]) if len(sys.argv) > 5 else 8
env = {**os.environ, 'FRAME_W': '460', 'FRAME_H': '260', 'BOX': '200', 'BOX_X': '130', 'BOX_Y': '30'}
html = out[:-4] + '.html'; big = out[:-4] + '_big.png'
open(html, 'w').write(subprocess.run([sys.executable, os.path.expanduser('~/src/femtovg-wt/da/harness/make_ref.py'), svg, z], capture_output=True, text=True, env=env, check=True).stdout)
flags = GPU if mode == 'gpu' else ['--disable-gpu']
subprocess.run([CHR, '--headless', *flags, '--hide-scrollbars', f'--force-device-scale-factor={S}', '--window-size=460,260',
                '--default-background-color=FFFFFFFF', f'--screenshot={big}', f'file://{os.path.abspath(html)}'], capture_output=True, timeout=300)
im = np.asarray(Image.open(big).convert('RGB'), dtype=np.float64)[:260 * S, :460 * S]
im = im.reshape(260, S, 460, S, 3).mean(axis=(1, 3))
Image.fromarray(np.rint(im).astype(np.uint8)).save(out)
os.remove(big); os.remove(html)
