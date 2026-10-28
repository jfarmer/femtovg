#!/bin/zsh
# rerun.sh BUILD...  - drop each build's rows and kept frames, then render the corpus again with it: the reftest
# groups, the probes and the NYT set with frames kept (png_wpt, png, png_nyt), the rest without.
R=/Users/matt/src/femtovg-wt/runs/pr; A=/Users/matt/src/femtovg-wt/da/harness/corpus_run/accuracy.py
cd $R && export CORPUS_RUN_OUT=$R
for b in "$@"; do
python3 - $b <<'PY'
import json, sys, collections
R='/Users/matt/src/femtovg-wt/runs/pr'; b=sys.argv[1]
keep=[]; extra=collections.defaultdict(set)
for l in open(f'{R}/accuracy.jsonl'):
    r=json.loads(l)
    if r['build']==b:
        if r['framing'] not in ('z1','z2','z4','hd'): extra[r['framing']].add(r['key'])
    else: keep.append(l)
open(f'{R}/accuracy.jsonl','w').writelines(keep)
for fr in ('z01','z025','z05'):
    json.dump(sorted(extra.get(fr, [])), open(f'{R}/tmp/{b}_extra_{fr}.json','w'))
print(b, 'rows of other builds kept', len(keep), 'extra framings', {k: len(v) for k,v in extra.items()})
PY
for d in png_wpt png_nyt png png_changed; do find $d -maxdepth 1 -name "${b}_corpus__*" -delete; done
python3 $A $b group=wpt-blend-reftests group=wpt-blend-reftests-2 group=wpt-clip-path-reftests group=wpt-fegaussianblur-reftests group=wpt-femorphology-reftests group=wpt-feoffset-reftests group=wpt-fill-blur-reftests png=$R/png_wpt
python3 $A $b group=clip-probes png=$R/png
python3 $A $b group=nyt png=$R/png_nyt
for fr in z01 z025 z05; do [ -s tmp/${b}_extra_$fr.json ] && [ "$(cat tmp/${b}_extra_$fr.json)" != "[]" ] && python3 $A $b keys=$R/tmp/${b}_extra_$fr.json framings=$fr png=$R/png_nyt; done
python3 $A $b
echo "RERUN $b DONE $(date +%T)"
done
echo ALL_RERUNS_DONE
