# Render one SVG at one zoom through femtovg (harness), Chromium 1x, Chromium 8x (area), WebKit, Firefox.
import os, subprocess, sys, numpy as np
from PIL import Image
H = os.path.expanduser('~')
CHR = f'{H}/.cache/puppeteer/chrome-headless-shell/mac_arm-131.0.6778.204/chrome-headless-shell-mac-arm64/chrome-headless-shell'
FF = '/Applications/Firefox Developer Edition.app/Contents/MacOS/firefox'
WK = f'{H}/src/femtovg-wt/bin/wk_shot'
ENV = {**os.environ, 'FRAME_W': '460', 'FRAME_H': '260', 'BOX': '200', 'BOX_X': '130', 'BOX_Y': '30'}
HENV = {**ENV, 'SKIP_UNSUPPORTED_FILTERS': '1', 'VIEWPORT_CLIP': '1', 'TRANSIENT_BUDGET_MB': '1024'}
def page(svg, z, out):
    html = subprocess.run([sys.executable, f'{H}/src/femtovg-wt/da/harness/make_ref.py', svg, f'{z:g}'], env=ENV, capture_output=True, text=True).stdout
    open(out, 'w').write(html); return out
def chrome(html, png, dpr=1):
    subprocess.run([CHR, '--headless', '--disable-gpu', '--hide-scrollbars', f'--force-device-scale-factor={dpr}', '--window-size=460,260',
                    '--default-background-color=FFFFFFFF', f'--screenshot={png}', f'file://{html}'], capture_output=True, timeout=180)
    im = Image.open(png).convert('RGB')
    if dpr > 1:
        a = np.asarray(im, dtype=np.float64)[:260 * dpr, :460 * dpr]
        a = a.reshape(260, dpr, 460, dpr, 3).mean(axis=(1, 3))
        im = Image.fromarray(np.round(a).astype(np.uint8))
    else:
        im = im.crop((0, 0, 460, 260))
    im.save(png)
def webkit(html, png):
    subprocess.run([WK, html, png, '460', '260'], capture_output=True, timeout=60)
    Image.open(png).convert('RGB').save(png)
def femtovg(binary, svg, z, png, extra={}):
    ppm = png[:-4] + '.ppm'
    subprocess.run([binary, f'{z:g}', ppm, svg], env={**HENV, **extra}, capture_output=True, timeout=120)
    Image.open(ppm).convert('RGB').save(png); os.remove(ppm)
if __name__ == '__main__':
    svg, z, outdir = sys.argv[1], float(sys.argv[2]), sys.argv[3]
    which = sys.argv[4].split(',') if len(sys.argv) > 4 else ['fv', 'chr', 'area', 'wk']
    binary = os.environ.get('FV_BIN', f'{H}/src/femtovg-wt/bin/_logos_full_zm2')
    tag = os.environ.get('FV_TAG', 'fv')
    os.makedirs(outdir, exist_ok=True)
    name = os.path.basename(svg)[:-4] + f'_z{z:g}'
    html = os.path.abspath(f'{outdir}/{name}.html'); page(svg, z, html)
    if 'fv' in which: femtovg(binary, svg, z, f'{outdir}/{tag}_{name}.png')
    if 'chr' in which: chrome(html, f'{outdir}/chr_{name}.png')
    if 'area' in which: chrome(html, f'{outdir}/area_{name}.png', 8)
    if 'wk' in which: webkit(html, f'{outdir}/wk_{name}.png')
