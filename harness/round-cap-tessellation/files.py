#!/usr/bin/env python3
"""files.py: writes $CORPUS_RUN_OUT/files.json for this directory's runs and links the references that already exist.

The reductions here (keys red__NAME): caps, caps-butt, joins, joins-miter, repro, sheet-caps, sheet-joins and
joins-bevel. The corpus files whose round caps and joins the change can move: every file of the wasmx run's list
(~/src/femtovg-wt/runs/wasmx/files.json) that names a round linecap or linejoin (every BuseyBench portrait and 10
other files), plus the whole wpt22 group 21-degenerate-paths-dashes-and-joins. No other stroke goes through the
code the change touches (round_cap_start, round_cap_end, round_join), so the rest of the corpus renders as before.
Their Chromium, Firefox, WebKit and area references are linked from runs/busey/refs, runs/wpt22/refs and
runs/wasmx/refs; the reductions' (and any missing Chromium reference) come from corpus_run/refs*.py."""
import json, os, re
OUT = os.environ['CORPUS_RUN_OUT']; HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.expanduser('~/src/femtovg-wt/runs')
os.makedirs(f'{OUT}/refs', exist_ok=True)
files = [{'path': f'{HERE}/{n}.svg', 'key': f'red__{n}', 'group': g} for n, g in (
    ('caps', 'reductions'), ('caps-butt', 'reductions'), ('joins', 'reductions'), ('joins-miter', 'reductions'),
    ('repro', 'reductions'), ('joins-bevel', 'checks'), ('sheet-caps', 'sheetred'), ('sheet-joins', 'sheetred'))]
for x in json.load(open(f'{RUNS}/wasmx/files.json')):
    try:
        s = open(x['path'], errors='ignore').read()
    except OSError:
        continue
    rnd = bool(re.search(r'linecap|linejoin', s) and 'round' in s)
    if x['group'] in ('buseybench', '21-degenerate-paths-dashes-and-joins') or rnd:
        files.append({**x, 'round': rnd})
json.dump(files, open(f'{OUT}/files.json', 'w'), indent=0)
links = 0
for x in files:
    if x['key'].startswith('red__'):
        continue
    for fr in ('z1', 'z2', 'hd'):
        for b in ('chr', 'ff', 'wk', 'id'):
            dst = f'{OUT}/refs/{b}_{x["key"]}_{fr}.png'
            if os.path.lexists(dst):
                continue
            for d in ('busey', 'wpt22', 'wasmx'):
                src = f'{RUNS}/{d}/refs/{b}_{x["key"]}_{fr}.png'
                if os.path.exists(src):
                    os.symlink(src, dst); links += 1
                    break
print(f'{len(files)} files, {links} references linked')
