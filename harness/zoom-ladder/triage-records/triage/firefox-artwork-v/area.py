import os, subprocess, sys
import numpy as np
from PIL import Image
H=os.path.expanduser('~')
CHR=f'{H}/.cache/puppeteer/chrome-headless-shell/mac_arm-131.0.6778.204/chrome-headless-shell-mac-arm64/chrome-headless-shell'
OUT=f'{H}/src/femtovg-wt/runs/zoom/triage/firefox-artwork-v/area'
ENV={**os.environ,'FRAME_W':'460','FRAME_H':'260','BOX':'200','BOX_X':'130','BOX_Y':'30'}
def shoot(svg, zoom, S, tag):
    png=f'{OUT}/{tag}_s{S}.png'
    html=f'{OUT}/{tag}.html'
    r=subprocess.run([sys.executable,f'{H}/src/femtovg-wt/da/harness/make_ref.py',svg,str(zoom)],capture_output=True,text=True,env=ENV)
    open(html,'w').write(r.stdout)
    big=png[:-4]+'_big.png'
    subprocess.run([CHR,'--headless','--disable-gpu','--hide-scrollbars',f'--force-device-scale-factor={S}','--window-size=460,260',f'--screenshot={big}',f'file://{html}'],capture_output=True,timeout=300)
    im=np.asarray(Image.open(big).convert('RGB'),dtype=np.float64); os.remove(big)
    w,h=460,260
    if S>1: im=im[:h*S,:w*S].reshape(h,S,w,S,3).mean(axis=(1,3))
    Image.fromarray(np.rint(im).astype(np.uint8)).save(png)
    print(png)
svg,zoom,S,tag=sys.argv[1],float(sys.argv[2]),int(sys.argv[3]),sys.argv[4]
shoot(svg,zoom,S,tag)
