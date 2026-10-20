#!/bin/zsh
# measure3.sh  - after rr2: the full-screen fills page again with more rounds, the per-call costs on master, instructions.
setopt nonomatch
R=/Users/matt/src/femtovg-wt/runs/fsetup; D=/Users/matt/src/femtovg-wt/da/harness/clip-bench; C=/Users/matt/src/femtovg-wt/da/corpus/buseybench
cd $R
T=$(python3 -c "import json; print([f['path'] for f in json.load(open('files.json')) if 'Tiger' in f['key']][0])")
export BUSY_LIMIT=350 BUSY_WAIT=120
echo "--- full-screen fills again $(date +%T)"
python3 rr.py 32 400 fs_base fs_vp fs_p3b fs_all -- $D/overdraw_none.svg
echo "--- per-call costs on master $(date +%T)"
python3 calls.py 5 300 $D/cards_none_200.svg $D/cards_rounded_200.svg $D/overdraw_none.svg $T
python3 calls.py 5 40 $C/kimi-k2-6.svg $C/gemini-3-1-pro-preview.svg
echo "--- instructions $(date +%T)"
LO=100 HI=500 REPEATS=5 python3 instr.py fs_base fs_vp fs_p3b fs_all -- $D/cards_none_200.svg $D/cards_rounded_200.svg $D/overdraw_none.svg $T
LO=10 HI=60 REPEATS=5 python3 instr.py fs_base fs_vp fs_p3b fs_all -- $C/kimi-k2-6.svg
echo "end $(date +%T)"
