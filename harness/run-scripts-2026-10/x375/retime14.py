#!/usr/bin/env python3
"""retime14.py [pass_time.py arguments] - pass_time.py with this run's builds: m14 (upstream master 9f5ad26), pc14
(#368 merged into it, slices of 64 passes), pc14u (the same, unsliced) and pc14s200 (slices of 200)."""
import os, sys
CR = '/Users/matt/src/femtovg-wt/da/harness/corpus_run'
sys.path.insert(0, CR)
os.environ.setdefault('CORPUS_RUN_OUT', '/Users/matt/src/femtovg-wt/runs/pm14')
import common
common.BUILDS.update({'m14': (f'{common.BIN}/_logos_full_m14', {}), 'pc14': (f'{common.BIN}/_logos_full_pc14', {}),
                      'pc14u': (f'{common.BIN}/_logos_full_pc14', {'NO_SLICES': '1'}),
                      'pc14s200': (f'{common.BIN}/_logos_full_pc14', {'SLICE_PASSES': '200'})})
sys.argv = ['pass_time.py'] + sys.argv[1:]
exec(compile(open(f'{CR}/pass_time.py').read(), f'{CR}/pass_time.py', 'exec'))
