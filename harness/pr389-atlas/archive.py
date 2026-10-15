#!/usr/bin/env python3
"""Preserve the completed run beside its report; exclude binaries and scratch PPMs."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
RUN = Path(os.environ.get('POC_RUN_DIR', HERE.parents[2]))
source, dest = RUN / 'results', HERE / 'results'
assert (source / 'summary.json').is_file(), 'summarize the complete run first'
shutil.copytree(source, dest, dirs_exist_ok=True, symlinks=True,
                ignore=shutil.ignore_patterns('tmp', '__pycache__'))
for p in dest.glob('memory-r*/refs'):
    if p.is_symlink():
        p.unlink()
        p.symlink_to('../refs', target_is_directory=True)
shutil.copytree(RUN / 'bin/logs', dest / 'build-logs', dirs_exist_ok=True)
patch = subprocess.check_output(['git', 'format-patch', '-1', '--stdout', 'da58dfb'], cwd=RUN / 'src/poc2389')
(HERE / 'atlas.patch').write_bytes(patch)
relevant = [HERE.parent / '_logos_full.rs', HERE.parent / 'build.sh',
            HERE.parent / 'corpus_run/common.py', HERE.parent / 'corpus_run/run.py',
            HERE / 'tools/interleaved.py', HERE / 'tools/pair.py', HERE / 'tools/short_runs.py',
            HERE / 'Cargo.lock.snapshot']
hashes = {str(p.relative_to(HERE.parents[1])): hashlib.sha256(p.read_bytes()).hexdigest() for p in relevant}
(dest / 'harness-source-sha256.json').write_text(json.dumps(hashes, indent=2) + '\n')
print(dest)
