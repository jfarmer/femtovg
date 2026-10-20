import sys
from PIL import Image
import numpy as np
R='/Users/matt/src/femtovg-wt/runs/zoom'
key=sys.argv[1]; fr=sys.argv[2]; step=sys.argv[3]; x=int(sys.argv[4]); y=int(sys.argv[5]); axis=sys.argv[6] if len(sys.argv)>6 else 'col'
ims={}
ims['fv']=np.asarray(Image.open(f'{R}/png/zl_zm_svg/{key}/{step}.png').convert('RGB')).astype(int)
for b in ['chr','ff','wk']:
    try: ims[b]=np.asarray(Image.open(f'{R}/fresh/refs/{b}_{key}_{fr}.png').convert('RGB')).astype(int)
    except Exception: pass
for b,a in ims.items():
    if axis=='col': print(b.ljust(4),' '.join(f'{a[yy,x,0]:3d},{a[yy,x,1]:3d}' for yy in range(y-3,y+4)))
    else: print(b.ljust(4),' '.join(f'{a[y,xx,0]:3d},{a[y,xx,1]:3d}' for xx in range(x-3,x+4)))
