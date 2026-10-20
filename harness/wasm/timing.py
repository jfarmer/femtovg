#!/usr/bin/env python3
"""Steady-state cost of the timing jobs (FRAMES=n per file, NO_READBACK): per file and framing, the median over frames
2..n of the record + encode milliseconds and of the queue wait, and the browser processes' CPU milliseconds and
instructions per frame (the task's counters, from the result before it to its own, over n frames). Compares builds
file by file, and fits the GPU process's cost per element on the perf group's N-element scenes.

  timing.py RUN_DIR BASE_JOB JOB [JOB...]"""
import json, re, statistics as st, sys
from collections import defaultdict

run, base, *others = sys.argv[1:]


def load(job):
    rows = {}
    for line in open(f'{run}/{job}/results.jsonl'):
        r = json.loads(line)
        if r.get('error') or r.get('failed') or not r.get('encode_ms'):
            continue
        n = len(r['encode_ms'])
        steady = slice(1, None) if n > 1 else slice(None)
        procs = {}
        for role, p in (r.get('procs') or {}).items():
            if 'cpu_ms' in p:
                kind = role.split(':')[0].rstrip('?')
                q = procs.setdefault(kind, {'cpu_ms': 0.0, 'instructions': 0})
                q['cpu_ms'] += p['cpu_ms'] / n
                q['instructions'] += p['instructions'] / n
        rows[(r['key'], r['framing'])] = {
            'encode': st.median(r['encode_ms'][steady]), 'queue': st.median(r['gpu_wait_ms'][steady]),
            'first_encode': r['encode_ms'][0], 'first_queue': r['gpu_wait_ms'][0], 'procs': procs,
            'layers': r.get('stats', {}).get('layers'), 'passes': r.get('stats', {}).get('passes'),
        }
    return rows


B = load(base)
print(f'{base}: {len(B)} frames')
GPU_ROLE = 'gpu-process'
MAIN_ROLES = ('renderer', 'webcontent')


def main_cpu(r):
    return sum(v['cpu_ms'] for k, v in r['procs'].items() if k in MAIN_ROLES)


for job in others:
    J = load(job)
    common = sorted(set(B) & set(J))
    print(f'\n== {job} against {base}: {len(common)} frames')
    for fr in sorted(set(f for _, f in common)):
        ks = [k for k in common if k[1] == fr]
        if not ks:
            continue
        def ratio(f):
            vals = [f(J[k]) / f(B[k]) for k in ks if f(B[k]) > 0.05]
            return (round(st.median(vals), 3), round(min(vals), 2), round(max(vals), 2)) if vals else None
        def total(f, D):
            return round(sum(f(D[k]) for k in ks), 1)
        print(f'  {fr}: encode median ratio {ratio(lambda r: r["encode"])}, sum {total(lambda r: r["encode"], B)} -> {total(lambda r: r["encode"], J)} ms; '
              f'queue ratio {ratio(lambda r: r["queue"])}, sum {total(lambda r: r["queue"], B)} -> {total(lambda r: r["queue"], J)} ms')
        g = lambda r: r['procs'].get(GPU_ROLE, {}).get('cpu_ms', 0)
        print(f'       GPU process cpu/frame ratio {ratio(g)}, sum {total(g, B)} -> {total(g, J)} ms; '
              f'page process cpu/frame ratio {ratio(main_cpu)}, sum {total(main_cpu, B)} -> {total(main_cpu, J)} ms')
        worst = sorted(ks, key=lambda k: -(J[k]['encode'] + J[k]['queue']) / max(0.05, B[k]['encode'] + B[k]['queue']))[:4]
        best = sorted(ks, key=lambda k: (J[k]['encode'] + J[k]['queue']) / max(0.05, B[k]['encode'] + B[k]['queue']))[:4]
        fmt = lambda k: f"{k[0].split('__')[-1]} {B[k]['encode']:.1f}+{B[k]['queue']:.1f} -> {J[k]['encode']:.1f}+{J[k]['queue']:.1f}"
        print('       slowest relative:', '; '.join(fmt(k) for k in worst))
        print('       fastest relative:', '; '.join(fmt(k) for k in best))

# Cost per element on the perf group's N-element scenes, each job.
for job in [base] + others:
    D = load(job) if job != base else B
    for fr in ('z1', 'hd'):
        pts = []
        for (k, f), r in D.items():
            m = re.match(r'perf__rects-(\d+)$', k)
            if m and f == fr:
                pts.append((int(m.group(1)), r['encode'], r['queue'], r['procs'].get(GPU_ROLE, {}).get('cpu_ms', 0), main_cpu(r)))
        pts.sort()
        if len(pts) >= 3:
            def slope(i):
                xs = [p[0] for p in pts]; ys = [p[i] for p in pts]
                mx, my = st.mean(xs), st.mean(ys)
                return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
            print(f'{job} {fr} rects: per 1000 elements: encode {1000 * slope(1):.2f} ms, queue {1000 * slope(2):.2f} ms, '
                  f'GPU process {1000 * slope(3):.2f} ms, page process {1000 * slope(4):.2f} ms; '
                  + ' '.join(f'N={p[0]}:{p[1]:.1f}/{p[2]:.1f}/{p[3]:.1f}' for p in pts))
