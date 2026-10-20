#!/bin/zsh
S=/Users/matt/src/femtovg-wt/runs/busey/triage/gemini-3-1-pro-preview-verify/tips
cd /Users/matt/src/femtovg-wt/da/harness/corpus_run
export HARNESS_BIN=/Users/matt/src/femtovg-wt/bin CORPUS_RUN_OUT=$S
python3 files.py t=$S/svg >/dev/null
python3 -c "import json;p='$S/files.json';f=[x for x in json.load(open(p)) if x['group']=='t'];json.dump(f,open(p,'w'))"
python3 refs.py chromium framings=z2 group=t >/dev/null 2>&1
python3 refs.py firefox framings=z2 group=t >/dev/null 2>&1
python3 refs_webkit.py framings=z2 group=t >/dev/null 2>&1
python3 accuracy.py ${1:-mst2} group=t framings=z2 png=$S/png >/dev/null 2>&1
ls $S/refs | wc -l; ls $S/png | wc -l
