import os, subprocess, sys, tempfile, shutil, numpy as np
from PIL import Image
H = os.path.expanduser('~')
CHR = f'{H}/.cache/puppeteer/chrome-headless-shell/mac_arm-131.0.6778.204/chrome-headless-shell-mac-arm64/chrome-headless-shell'
FF = '/Applications/Firefox Developer Edition.app/Contents/MacOS/firefox'
WK = f'{H}/src/femtovg-wt/bin/wk_shot'
ENV = {**os.environ, 'FRAME_W': '460', 'FRAME_H': '260', 'BOX': '200', 'BOX_X': '130', 'BOX_Y': '30'}
HENV = {**ENV, 'SKIP_UNSUPPORTED_FILTERS': '1', 'VIEWPORT_CLIP': '1', 'TRANSIENT_BUDGET_MB': '1024'}
svg, z, out, which = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4].split(',')
binary = os.environ.get('FV_BIN', f'{H}/src/femtovg-wt/bin/_logos_full_zm2'); tag = os.environ.get('FV_TAG', 'fv')
os.makedirs(out, exist_ok=True)
name = os.path.basename(svg)[:-4] + f'_z{z}'
html = os.path.abspath(f'{out}/{name}.html')
open(html,'w').write(subprocess.run([sys.executable, f'{H}/src/femtovg-wt/da/harness/make_ref.py', svg, z], env=ENV, capture_output=True, text=True).stdout)
def chrome(png, dpr):
    subprocess.run([CHR,'--headless','--disable-gpu','--hide-scrollbars',f'--force-device-scale-factor={dpr}','--window-size=460,260','--default-background-color=FFFFFFFF',f'--screenshot={png}',f'file://{html}'],capture_output=True,timeout=180)
    im = Image.open(png).convert('RGB')
    if dpr>1:
        a=np.asarray(im,dtype=np.float64)[:260*dpr,:460*dpr].reshape(260,dpr,460,dpr,3).mean(axis=(1,3)); im=Image.fromarray(np.round(a).astype(np.uint8))
    else: im=im.crop((0,0,460,260))
    im.save(png)
if 'fv' in which:
    ppm=f'{out}/{tag}_{name}.ppm'; r=subprocess.run([binary,z,ppm,svg],env={**HENV,'LAYER_STATS':'1'},capture_output=True,text=True,timeout=120)
    Image.open(ppm).convert('RGB').save(ppm[:-4]+'.png'); os.remove(ppm)
if 'chr' in which: chrome(f'{out}/chr_{name}.png',1)
if 'area' in which: chrome(f'{out}/area_{name}.png',8)
if 'wk' in which:
    subprocess.run([WK,html,f'{out}/wk_{name}.png','460','260'],capture_output=True,timeout=60); Image.open(f'{out}/wk_{name}.png').convert('RGB').save(f'{out}/wk_{name}.png')
if 'ff' in which:
    prof=tempfile.mkdtemp(); png=os.path.abspath(f'{out}/ff_{name}.png')
    subprocess.run([FF,'--headless','--no-remote','--profile',prof,'--window-size=460,260','--screenshot',png,f'file://{html}'],capture_output=True,timeout=180)
    shutil.rmtree(prof,ignore_errors=True); Image.open(png).convert('RGB').crop((0,0,460,260)).save(png)
