# shoot.py SVG ZOOM OUTPREFIX : femtovg (harness), chr, ff, wk at one zoom in the default framing -> OUTPREFIX_{fv,chr,ff,wk}.png
import sys, os, subprocess, tempfile, shutil
from PIL import Image
CH='/Users/matt/.cache/puppeteer/chrome-headless-shell/mac_arm-131.0.6778.204/chrome-headless-shell-mac-arm64/chrome-headless-shell'
FF='/Applications/Firefox Developer Edition.app/Contents/MacOS/firefox'
WK='/Users/matt/src/femtovg-wt/bin/wk_shot'
FV=os.environ.get('FV_BIN','/Users/matt/src/femtovg-wt/bin/_logos_full_zm2')
svg, z, out = sys.argv[1], sys.argv[2], sys.argv[3]
which = sys.argv[4].split(',') if len(sys.argv) > 4 else ['fv','chr','ff','wk']
env = dict(os.environ, FRAME_W='460', FRAME_H='260', BOX='200', BOX_X='130', BOX_Y='30')
html = out + '.html'
open(html,'w').write(subprocess.run(['python3','/Users/matt/src/femtovg-wt/da/harness/make_ref.py', svg, z], env=env, capture_output=True, text=True, check=True).stdout)
html = os.path.abspath(html)
def crop(p):
    im = Image.open(p).convert('RGB')
    if im.size != (460,260): im = im.crop((0,0,460,260))
    im.save(p)
if 'fv' in which:
    e = dict(env, SKIP_UNSUPPORTED_FILTERS='1', VIEWPORT_CLIP='1', TRANSIENT_BUDGET_MB='1024')
    subprocess.run([FV, z, out+'_fv.ppm', svg], env=e, capture_output=True, check=True)
    Image.open(out+'_fv.ppm').convert('RGB').save(out+'_fv.png'); os.remove(out+'_fv.ppm')
if 'chr' in which:
    subprocess.run([CH,'--headless','--disable-gpu','--hide-scrollbars','--force-device-scale-factor=1','--window-size=460,260','--default-background-color=FFFFFFFF',f'--screenshot={out}_chr.png','file://'+html], capture_output=True)
    crop(out+'_chr.png')
if 'ff' in which:
    prof = tempfile.mkdtemp(prefix='ffprof')
    try:
        subprocess.run([FF,'--headless','--no-remote','--profile',prof,'--window-size=460,260','--screenshot',os.path.abspath(out+'_ff.png'),'file://'+html], capture_output=True, timeout=120)
    finally: shutil.rmtree(prof, ignore_errors=True)
    crop(out+'_ff.png')
if 'wk' in which:
    subprocess.run([WK, html, os.path.abspath(out+'_wk.png'), '460', '260'], capture_output=True, timeout=60)
    crop(out+'_wk.png')
