#!/usr/bin/env python3
"""tool.py SCRIPT ARGS... - run a corpus_run script (or one here) with CORPUS_RUN_OUT = this directory.
Builds resolve through common.py's fallback: $HARNESS_BIN/_logos_full_<name>.
m10 = upstream master 9f5ad261; dc10 = flatten-degenerate-cubic 155d565e; dd10 = path-dedupe af9d7c9b;
ddf10 = dd10 with interior points through add_point (equivalence check of the in-register comparison)."""
import os, runpy, sys
HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault('CORPUS_RUN_OUT', HERE)
os.environ.setdefault('HARNESS_BIN', os.path.expanduser('~/src/femtovg-wt/bin'))
CR = os.path.expanduser('~/src/femtovg-wt/da/harness/corpus_run')
sys.path.insert(0, CR)
script = sys.argv[1]
if not os.path.exists(script):
    script = f'{CR}/{script}'
sys.argv = [script] + sys.argv[2:]
runpy.run_path(script, run_name='__main__')
