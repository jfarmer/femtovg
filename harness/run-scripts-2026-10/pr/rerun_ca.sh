#!/bin/zsh
# Re-run the corpus for the `ca` build after its binary changed: drop its rows and kept frames, then render the
# same (key, framing) set again - reftest groups and probes with frames kept.
R=/Users/matt/src/femtovg-wt/runs/pr; A=/Users/matt/src/femtovg-wt/da/harness/corpus_run/accuracy.py
cd $R && export CORPUS_RUN_OUT=$R
python3 - <<'PY'
import json, gzip, collections, shutil, os
R='/Users/matt/src/femtovg-wt/runs/pr'
shutil.copy(f'{R}/accuracy.jsonl', f'{R}/accuracy.before-ca-rerun.jsonl')
keep=[]; extra=collections.defaultdict(set)
for l in open(f'{R}/accuracy.jsonl'):
    r=json.loads(l)
    if r['build']=='ca':
        if r['framing'] not in ('z1','z2','z4','hd'): extra[r['framing']].add(r['key'])
    else: keep.append(l)
open(f'{R}/accuracy.jsonl','w').writelines(keep)
for fr,keys in extra.items(): json.dump(sorted(keys), open(f'{R}/tmp/ca_extra_{fr}.json','w'))
print('kept rows', len(keep), 'extra framings', {k: len(v) for k,v in extra.items()})
PY
rm -f png_wpt/ca_* png_nyt/ca_* png/ca_*
python3 $A ca group=wpt-blend-reftests group=wpt-blend-reftests-2 group=wpt-clip-path-reftests group=wpt-fegaussianblur-reftests group=wpt-femorphology-reftests group=wpt-feoffset-reftests group=wpt-fill-blur-reftests png=$R/png_wpt
python3 $A ca group=clip-probes png=$R/png
python3 $A ca group=nyt png=$R/png_nyt
for f in tmp/ca_extra_*.json; do fr=${${f:t:r}#ca_extra_}; python3 $A ca keys=$R/$f framings=$fr png=$R/png_nyt; done
python3 $A ca
echo CA_RERUN_DONE $(date +%T)
