import os, subprocess, sys
import numpy as np
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
H=os.path.expanduser('~')
CHR=f'{H}/.cache/puppeteer/chrome-headless-shell/mac_arm-131.0.6778.204/chrome-headless-shell-mac-arm64/chrome-headless-shell'
OUT=f'{H}/src/femtovg-wt/runs/zoom/triage/firefox-artwork/area'
ENV={**os.environ,'FRAME_W':'460','FRAME_H':'260','BOX':'200','BOX_X':'130','BOX_Y':'30'}
Z={'z1':1,'z125':1.25,'z15':1.5,'z175':1.75,'z2':2,'z3':3,'z4':4,'z075':0.75,'z05':0.5,'z033':0.33,'z025':0.25}
def shoot(job):
    key,svg,fr,S=job
    png=f'{OUT}/id{S}_{key}_{fr}.png'
    if os.path.exists(png): return 'kept'
    html=f'{OUT}/{key}_{fr}_{S}.html'
    r=subprocess.run([sys.executable,f'{H}/src/femtovg-wt/da/harness/make_ref.py',svg,str(Z[fr])],capture_output=True,text=True,env=ENV)
    open(html,'w').write(r.stdout)
    big=png[:-4]+'_big.png'
    subprocess.run([CHR,'--headless','--disable-gpu','--hide-scrollbars',f'--force-device-scale-factor={S}','--window-size=460,260','--default-background-color=FFFFFFFF',f'--screenshot={big}',f'file://{html}'],capture_output=True,timeout=300)
    im=np.asarray(Image.open(big).convert('RGB'),dtype=np.float64); os.remove(big)
    w,h=460,260
    im=im[:h*S,:w*S].reshape(h,S,w,S,3).mean(axis=(1,3))
    Image.fromarray(np.rint(im).astype(np.uint8)).save(png)
    return 'made'
keys=sys.argv[1].split(',')
S=int(sys.argv[2]) if len(sys.argv)>2 else 8
jobs=[]
for k in keys:
    svg=f'{H}/src/femtovg-wt/da/corpus/firefox/'+k.split('__')[-1]+'.svg'
    for fr in Z: jobs.append((k,svg,fr,S))
with ThreadPoolExecutor(4) as ex:
    print(list(ex.map(shoot,jobs)))
