import numpy as np, sys
from PIL import Image
for p in sys.argv[1:]:
    a=np.asarray(Image.open(p).convert('RGB')).astype(float)
    h,w=a.shape[0]//8,a.shape[1]//8
    ar=a.reshape(h,8,w,8,3).mean((1,3))
    Image.fromarray(ar.round().astype(np.uint8)).save(p.replace('chr8_','area_'))
