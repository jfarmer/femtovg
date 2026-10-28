# ref1.py SVG ZOOM SCALE OUT.png [extra chrome flags...]: Chromium reference of one SVG in the harness framing,
# at SCALE device pixels per CSS pixel, box-downsampled back to 460x260.
import os, subprocess, sys, tempfile
import numpy as np
from PIL import Image
H=os.path.expanduser('~')
CHR=f'{H}/.cache/puppeteer/chrome-headless-shell/mac_arm-131.0.6778.204/chrome-headless-shell-mac-arm64/chrome-headless-shell'
svg,z,S,out=sys.argv[1],sys.argv[2],int(sys.argv[3]),sys.argv[4]
ENV={**os.environ,'FRAME_W':'460','FRAME_H':'260','BOX':'200','BOX_X':'130','BOX_Y':'30'}
r=subprocess.run([sys.executable,f'{H}/src/femtovg-wt/da/harness/make_ref.py',svg,z],capture_output=True,text=True,env=ENV)
d=tempfile.mkdtemp(dir=os.path.dirname(os.path.abspath(out)))
html=f'{d}/p.html'; open(html,'w').write(r.stdout); big=f'{d}/big.png'
subprocess.run([CHR,'--headless','--disable-gpu','--hide-scrollbars',f'--force-device-scale-factor={S}','--window-size=460,260','--default-background-color=FFFFFFFF',f'--screenshot={big}',f'file://{html}'],capture_output=True,timeout=300)
im=np.asarray(Image.open(big).convert('RGB'),dtype=np.float64)
im=im[:260*S,:460*S].reshape(260,S,460,S,3).mean(axis=(1,3))
Image.fromarray(np.rint(im).astype(np.uint8)).save(out)
os.remove(big); os.remove(html); os.rmdir(d)
