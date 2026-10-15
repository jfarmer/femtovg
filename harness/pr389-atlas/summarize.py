#!/usr/bin/env python3
"""Collect the existing harness analyses into one machine-readable summary.

Measurements stay in run.py's raw outputs. Timing statistics below come from
the reused October 12 paired analysis, not a new benchmark implementation.
"""
import collections
import json
import os
from pathlib import Path
import re
import statistics as st

HERE = Path(__file__).resolve().parent
DEFAULT_ROOT = HERE / 'results' if (HERE / 'results').exists() else HERE.parents[2] / 'results'
ROOT = Path(os.environ.get('POC_RESULTS', DEFAULT_ROOT))
PAIRS = [('m15', 'p15'), ('p15', 'a15'), ('m15sw', 'p15sw'), ('p15sw', 'a15sw')]
summary = {}


def rows(name):
    return [json.loads(line) for line in (ROOT / name).open()]


def index(data):
    return {(r['build'], r['key'], r['framing']): r for r in data}


def changes(data, a, b):
    return [(k, f) for bb, k, f in data if bb == a and (b, k, f) in data
            and data[a, k, f].get('hash') != data[b, k, f].get('hash')]


pixels = rows('pixels.jsonl')
assert len(pixels) == 1280 * 4 * 6
assert not any(r.get('error') or r.get('rc') for r in pixels)
pd = index(pixels)
summary['pixels'] = {}
for a, b in PAIRS:
    changed = changes(pd, a, b)
    summary['pixels'][f'{a}_{b}'] = {
        'frames': 5120, 'changed': len(changed), 'files': sorted({k for k, f in changed}),
    }

accuracy = rows('accuracy.jsonl')
assert len(accuracy) == 68 * 9 * 6
assert not any(r.get('error') or r.get('rc') for r in accuracy)
assert all('vs_chr' in r and 'vs_ff' in r for r in accuracy)
summary['accuracy'] = {}
for a, b in PAIRS:
    text = (ROOT / f'logs/accuracy_compare_{a}_{b}.log').read_text()
    result = {'frames': 612, 'changed': len(changes(index(accuracy), a, b))}
    for browser, label in [('chr', 'Chromium (software)'), ('ff', 'Firefox')]:
        pattern = re.escape(label) + r': (\d+) changed frames compared; toward (\d+), away (\d+), level (\d+);'
        matches = re.findall(pattern, text)
        assert matches, (a, b, label)
        n, toward, away, level = map(int, matches[-1])
        result[browser] = {'compared': n, 'toward': toward, 'away': away, 'level': level}
    summary['accuracy'][f'{a}_{b}'] = result

summary['timing'] = {}
for a, b in PAIRS:
    result = {}
    for mode, field in [('text', 'frame_ms'), ('short', 'later_same_repeat'),
                        ('drift_short', 'later_same_repeat')]:
        path = ROOT / f'paired_timing_{a}_{b}_{mode}.json'
        data = json.loads(path.read_text())
        assert len(data) == (272 if mode == 'text' else 52)
        assert all(r[field]['n'] == (3 if mode == 'text' else 5) for r in data)
        subset = {}
        for name, selected in [('all', data), ('pixels_changed', [r for r in data if r['changed']]),
                               ('pixels_identical', [r for r in data if not r['changed']])]:
            if not selected:
                continue
            values = [r[field] for r in selected]
            subset[name] = {
                'frames': len(values), 'median_paired_pct': st.median(v['pct'] for v in values),
                'range_pct': [min(v['pct'] for v in values), max(v['pct'] for v in values)],
                'same_sign_in_every_repeat': sum(v['one_sign'] for v in values),
            }
        result[mode] = subset
    cold = rows(f'timing_{a}_{b}_cold.jsonl')
    assert len(cold) == 52 * 2 * 5
    grouped = collections.defaultdict(list)
    for r in cold:
        grouped[r['key'], r['framing'], r['build']].append(r['frame_ms'])
    result['cold'] = [
        {'key': k, 'framing': f, 'before_ms': st.median(grouped[k, f, a]),
         'after_ms': st.median(grouped[k, f, b]),
         'paired_delta_ms': st.median(y - x for x, y in zip(grouped[k, f, a], grouped[k, f, b]))}
        for k, f, bb in grouped if bb == a
    ]
    summary['timing'][f'{a}_{b}'] = result

summary['instructions'] = {}
for a, b in PAIRS + [('p15', 'p15'), ('p15sw', 'p15sw')]:
    data = json.loads((ROOT / f'instructions_{a}_{b}.json').read_text())
    assert len(data) == (3 if a == b else 14)
    assert all(r['repeats'] == 3 for r in data)
    summary['instructions'][f'{a}_{b}'] = [
        {'key': r['key'], 'framing': r['framing'],
         'before_millions': st.median(r['a_steady']) / 1e6,
         'after_millions': st.median(r['b_steady']) / 1e6,
         'paired_pct': r['median_diff_pct'],
         'range_pct': [min(r['paired_diff_pct']), max(r['paired_diff_pct'])]}
        for r in data
    ]

cold = json.loads((ROOT / 'cold_instructions.json').read_text())
assert len(cold) == 7
summary['cold_instructions'] = {}
for a, b in PAIRS:
    result = []
    for r in cold:
        first = lambda tag: [y - x for x, y in zip(r['raw'][tag]['0'], r['raw'][tag]['1'])]
        va, vb = first(a), first(b)
        result.append({'key': r['name'], 'framing': r['framing'],
                       'before_millions': st.median(va) / 1e6,
                       'after_millions': st.median(vb) / 1e6,
                       'paired_delta_millions': st.median(y - x for x, y in zip(va, vb)) / 1e6})
    summary['cold_instructions'][f'{a}_{b}'] = result

memory = [index(rows(f'memory-r{i}/memory.jsonl')) for i in range(3)]
assert all(len(d) == 68 * 4 * 6 for d in memory)
assert not any(r.get('error') or r.get('rc') for d in memory for r in d.values())
summary['memory'] = {}
for a, b in PAIRS:
    result = []
    for k, f in changes(pd, a, b):
        values = {}
        for field in ['after_graphics', 'peak_footprint']:
            va = [d[a, k, f]['mem'][field] / 2**20 for d in memory]
            vb = [d[b, k, f]['mem'][field] / 2**20 for d in memory]
            values[field] = {'before_mib': st.median(va), 'after_mib': st.median(vb),
                             'median_delta_mib': st.median(y - x for x, y in zip(va, vb))}
        result.append({'key': k, 'framing': f, **values})
    summary['memory'][f'{a}_{b}'] = result

counters = rows('memory.jsonl')
assert len(counters) == 68 * 4 * 6
assert not any(r.get('error') or r.get('rc') for r in counters)
cd = index(counters)
summary['counters'] = {}
for a, b in PAIRS:
    items = [(k, f) for bb, k, f in cd if bb == 'count_' + a]
    result = {}
    for field in ['alloc_calls', 'alloc_bytes']:
        result[field] = {
            'equal_frames': sum(cd['count_' + a, k, f][field] == cd['count_' + b, k, f][field] for k, f in items),
            'total_frames': len(items),
        }
    result['instrumented_hash_mismatches'] = sum(
        cd['count_' + bb, k, f]['hash'] != pd[bb, k, f]['hash']
        for bb in (a, b) for k, f in items)
    result['passes'] = [
        {'key': k, 'framing': f, 'before_integer_average_6_frames': cd['count_' + a, k, f]['mem']['passes'],
         'after_integer_average_6_frames': cd['count_' + b, k, f]['mem']['passes']}
        for k, f in items if cd['count_' + a, k, f]['mem']['passes'] != cd['count_' + b, k, f]['mem']['passes']
    ]
    summary['counters'][f'{a}_{b}'] = result

summary['timing_noise'] = {}
for b in ['p15', 'p15sw']:
    data = json.loads((ROOT / f'paired_timing_noise_{b}.json').read_text())
    assert len(data) == 8 and all(r['frame_ms']['n'] == 7 for r in data)
    summary['timing_noise'][b] = [
        {'key': r['key'], 'framing': r['framing'], **r['frame_ms']} for r in data
    ]
history = index(rows('history-check/pixels.jsonl'))
assert len(history) == 24
assert not any(r.get('error') or r.get('rc') for r in history.values())
summary['history_check'] = {
    'normal_six_vs_first_changed': [(b, k, f) for b, k, f in history
                                   if history[b, k, f]['hash'] != pd[b, k, f]['hash']],
    'normal_vs_instrumented_six_changed': [(b, k, f) for b, k, f in history
                                          if history[b, k, f]['hash'] != cd['count_' + b, k, f]['hash']],
}
summary['instruction_checks'] = {
    f.stem: json.loads(f.read_text()) for f in ROOT.glob('instruction_check_*.json')
}
assert len(summary['instruction_checks']) == 4
summary['soaks'] = {}
for b in ['m15', 'p15', 'a15', 'm15sw', 'p15sw', 'a15sw']:
    runs = []
    for dest in [ROOT, ROOT / 'soak-r1', ROOT / 'soak-r2']:
        lines = (dest / f'soak_{b}_hd.csv').read_text().splitlines()
        assert len(lines) == 1280 * 3 + 1
        header = lines[0].split(',')
        values = []
        # The existing soak.py report uses this split because names may have
        # commas: pass, name, then thirteen numeric columns.
        for line in lines[1:]:
            parts = line.split(',')
            values.append(dict(zip(header, [parts[0], ','.join(parts[1:-13])] + parts[-13:])))
        runs.append({'peak_mib': max(float(r['peak_footprint']) for r in values) / 2**20,
                     'held_after_pass_mib': [float([r for r in values if r['pass'] == str(n)][-1]['footprint_after']) / 2**20
                                             for n in range(3)]})
    summary['soaks'][b] = runs
(ROOT / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
print(ROOT / 'summary.json')
