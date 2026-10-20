#!/usr/bin/env python3
"""tool2.py SCRIPT ARGS... - tool.py, plus the build all_fm: the integration build (all current open PRs merged, #401
included) with the harness's FILL_MASKS=1 experiment (fills thinner than a pixel as exact coverage masks, #327)."""
import importlib.util, os, runpy, sys
HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault('CORPUS_RUN_OUT', HERE)
os.environ.setdefault('HARNESS_BIN', os.path.expanduser('~/src/femtovg-wt/bin'))
CR = os.path.expanduser('~/src/femtovg-wt/da/harness/corpus_run')
sys.path.insert(0, CR)
spec = importlib.util.spec_from_file_location('common', f'{CR}/common.py')
common = importlib.util.module_from_spec(spec); sys.modules['common'] = common; spec.loader.exec_module(common)
common.BUILDS['all_fm'] = (f"{os.environ['HARNESS_BIN']}/_logos_full_all", {'SINGLE_SHADOW_LAYER': '1', 'FILL_MASKS': '1'})
script = sys.argv[1] if os.path.exists(sys.argv[1]) else f'{CR}/{sys.argv[1]}'
sys.argv = [script] + sys.argv[2:]
runpy.run_path(script, run_name='__main__')
