#!/usr/bin/env python3
"""tool.py SCRIPT ARGS... - run a corpus_run script with this run's builds registered, without editing common.py.

CORPUS_RUN_OUT defaults to this directory."""
import importlib.util, os, runpy, sys
HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault('CORPUS_RUN_OUT', HERE)
CR = os.path.expanduser('~/src/femtovg-wt/da/harness/corpus_run')
sys.path.insert(0, CR)
spec = importlib.util.spec_from_file_location('common', f'{CR}/common.py')
common = importlib.util.module_from_spec(spec)
sys.modules['common'] = common
spec.loader.exec_module(common)
# m8 = upstream master d70ffeb; rv = path-dedupe's first form (slice lookup); rvf = path-dedupe 0d36c10 (chord
# bound; renders all 8,372 frames as rv); rvd = rv + rv_diag.patch (RV_DIAG=1 logs merges). Every cfg.
for tag in ('m8', 'rv', 'rvf', 'rvd', 'dc'):
    common.BUILDS[tag] = (f'{common.BIN}/_logos_full_{tag}', {'SINGLE_SHADOW_LAYER': '1'})
script = sys.argv[1]
if not os.path.exists(script):
    script = f'{CR}/{script}'
sys.argv = [script] + sys.argv[2:]
runpy.run_path(script, run_name='__main__')
