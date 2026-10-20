#!/bin/zsh
# run.sh SCRATCH [browsers...] : refs + femtovg z2 for SCRATCH/svg/*.svg
S=$1
cd /Users/matt/src/femtovg-wt/da/harness/corpus_run
export HARNESS_BIN=/Users/matt/src/femtovg-wt/bin CORPUS_RUN_OUT=$S
python3 files.py t=$S/svg > /dev/null
python3 -c "import json;p='$S/files.json';f=[x for x in json.load(open(p)) if x['group']=='t'];json.dump(f,open(p,'w'))"
python3 refs.py chromium framings=z2 group=t | tail -1
python3 refs.py firefox framings=z2 group=t | tail -1
python3 refs_webkit.py framings=z2 group=t | tail -1
rm -f $S/accuracy.jsonl
python3 accuracy.py mst2 group=t framings=z2 png=$S/png | tail -1
