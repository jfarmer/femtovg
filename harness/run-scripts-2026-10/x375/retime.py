#!/usr/bin/env python3
"""retime.py [pass_time.py arguments after the two builds] - pass_time.py for this investigation's binaries, without
touching the shared build table: m375 (master 9d574e0), h375 (#375 at acf2d73) and f375 (#375 with the pool fix),
all three made from one harness source, with the earlier group-shadow mapping the published table was timed with."""
import os, sys
CR = '/Users/matt/src/femtovg-wt/da/harness/corpus_run'
sys.path.insert(0, CR)
os.environ.setdefault('CORPUS_RUN_OUT', '/Users/matt/src/femtovg-wt/runs/pr')
import common
for tag in ('m375', 'h375', 'f375'):
    common.BUILDS[tag] = (f'{common.BIN}/_logos_full_{tag}', {'SINGLE_SHADOW_LAYER': '1'})
sys.argv = ['pass_time.py'] + sys.argv[1:]
exec(compile(open(f'{CR}/pass_time.py').read(), f'{CR}/pass_time.py', 'exec'))
