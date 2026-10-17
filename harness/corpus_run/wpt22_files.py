#!/usr/bin/env python3
"""wpt22_files.py [SUITE]: files.json for the extracted reftest suite alone (groups 01-22 of SUITE, by default
~/.gemini/antigravity/scratch/wpt_svg_reftests), keyed wpt22__<group>__<name>, into CORPUS_RUN_OUT. Then
refs.py chromium framings=z1,z2,z4,hd, accuracy.py BUILD framings=z1,z2,z4,hd png=$CORPUS_RUN_OUT/png for each
build, and wpt22_report.py BASE HEAD (run from CORPUS_RUN_OUT: it reads accuracy.jsonl, png/ and refs/ there)."""
import glob, json, os, sys
from common import OUT
S = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser('~/.gemini/antigravity/scratch/wpt_svg_reftests')
out = [{'path': p, 'key': f'wpt22__{os.path.basename(d)}__{os.path.basename(p)[:-4]}', 'group': os.path.basename(d)}
       for d in sorted(glob.glob(f'{S}/[0-9][0-9]-*')) for p in sorted(glob.glob(f'{d}/*.svg'))]
assert len({f['key'] for f in out}) == len(out)
os.makedirs(OUT, exist_ok=True)
json.dump(out, open(f'{OUT}/files.json', 'w'), indent=0, ensure_ascii=False)
print(len(out), 'files')
