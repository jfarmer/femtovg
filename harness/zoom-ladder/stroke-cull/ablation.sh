#!/bin/bash
# ablation.sh KEY PATH: draws one file with _logos_nocull (the harness on femtovg 06243b80 with the stroke early-out at
# src/lib.rs L1607-L1614 deleted) at zooms 1, 1.5, 2, 3, 4 and 0.5, and prints the pixels that differ at all from
# master's ladder frame of that zoom (ablation.txt: one line per file and zoom, 1,026 files).
K=$1; P=$2; D=~/src/femtovg-wt/runs/zoom/triage/mask-thin-stroke-3x-v
for zs in "1:00" "2:04" "3:05" "4:06" "1.5:02" "0.5:14"; do
  Z=${zs%%:*}; S=${zs##*:}
  L=~/src/femtovg-wt/runs/zoom/png/zl_zm_svg/$K/$S.png
  [ -f "$L" ] || continue
  O=$D/sweep/${K}_$S
  env FRAME_W=460 FRAME_H=260 BOX=200 BOX_X=130 BOX_Y=30 SKIP_UNSUPPORTED_FILTERS=1 VIEWPORT_CLIP=1 TRANSIENT_BUDGET_MB=1024 $D/bin/_logos_nocull $Z $O.ppm "$P" >/dev/null 2>&1
  python3 -c "
import numpy as np
from PIL import Image
a=np.asarray(Image.open('$O.ppm').convert('RGB')).astype(int); b=np.asarray(Image.open('$L').convert('RGB')).astype(int)
n=int((np.abs(a-b).max(2)>0).sum()) if a.shape==b.shape else -1
print('$K',$Z,n)
if n!=0: Image.fromarray(a.astype('uint8')).save('$O.png')
" 
  rm -f $O.ppm
done
