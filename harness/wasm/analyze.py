#!/usr/bin/env python3
"""Summarises crosscheck jobs: stability, agreement with the native build, memory and compute.

  analyze.py RUN_DIR JOB [JOB...] [--json OUT.json]

Per job: frames, failures (thrown frames, frames the page died on twice, device errors, lost devices, page reloads),
agreement with the native frame (pixels beyond 2, 8 and 20 levels; frames with any pixel beyond 8 are listed with
their px > 20 against Chromium, Firefox and WebKit next to the native build's), the wasm heap (its high-water mark
and when it grew), the browser processes' footprint (high-water, lifetime maximum, growth from the first tenth of the
run to the last) and compute (record + encode milliseconds and the queue wait per framing, the processes' CPU
milliseconds and instructions per frame), with the frames furthest out on each."""
import json, os, statistics as st, sys
from collections import defaultdict

run = sys.argv[1]
args = sys.argv[2:]
out_json = None
if '--json' in args:
    i = args.index('--json')
    out_json = args[i + 1]
    args = args[:i] + args[i + 2:]
jobs = args


def load(job):
    path = f'{run}/{job}/results.jsonl'
    rows = [json.loads(l) for l in open(path)] if os.path.exists(path) else []
    events = [json.loads(l) for l in open(f'{run}/{job}/events.jsonl')] if os.path.exists(f'{run}/{job}/events.jsonl') else []
    procs = [json.loads(l) for l in open(f'{run}/{job}/procs.jsonl')] if os.path.exists(f'{run}/{job}/procs.jsonl') else []
    return rows, events, procs


def q(xs, p):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(p * len(xs)))] if xs else None


def role_of(r):
    return r.split(':')[0].rstrip('?')


summary = {}
for job in jobs:
    rows, events, procs = load(job)
    s = {'frames': len(rows)}
    s['thrown'] = [(r['key'], r['framing'], (r.get('error') or '')[:200]) for r in rows if r.get('error')]
    s['died'] = [(r['key'], r['framing']) for r in rows if r.get('failed')]
    s['device_errors'] = [(r['key'], r['framing'], r['device_errors'][:3]) for r in rows if r.get('device_errors')]
    s['lost'] = [(r['key'], r['framing'], r['lost']) for r in rows if r.get('lost')]
    s['reloads'] = sum(1 for e in events if e.get('event') in ('reload', 'driver-reload', 'webcontent-terminated'))
    s['hellos'] = sum(1 for e in events if e.get('event') == 'hello')
    vn = [(r, r['vs_native']) for r in rows if 'px0' in r.get('vs_native', {})]
    s['with_native'] = len(vn)
    s['identical'] = sum(1 for _, v in vn if v['px0'] == 0)
    s['beyond2'] = sum(1 for _, v in vn if v['px2'] > 0)
    s['beyond8'] = sorted([(r['key'], r['framing'], v['px8'], v['px20'], v['max'], r.get('vs')) for r, v in vn if v['px8'] > 0],
                          key=lambda x: -x[2])
    s['max_level'] = max((v['max'] for _, v in vn), default=None)
    s['no_native'] = [(r['key'], r['framing']) for r in rows if 'vs_native' not in r and not r.get('error') and not r.get('failed')]
    wasm = [r['wasm_after'] for r in rows if 'wasm_after' in r]
    s['wasm_heap_max_mib'] = round(max(wasm) / 2**20, 1) if wasm else None
    growth = []
    last = None
    for r in sorted(rows, key=lambda r: r.get('t', 0)):
        if 'wasm_after' in r:
            if last is not None and r['wasm_after'] > last:
                growth.append((r['key'], r['framing'], round(last / 2**20, 1), round(r['wasm_after'] / 2**20, 1)))
            last = r['wasm_after'] if last is None else max(last, r['wasm_after'])
    s['wasm_heap_growth'] = growth
    by_role = defaultdict(list)
    for r in sorted(rows, key=lambda r: r.get('t', 0)):
        for role, p in (r.get('procs') or {}).items():
            by_role[role_of(role)].append((r, p))
    s['processes'] = {}
    for role, xs in by_role.items():
        fp = [p['footprint'] for _, p in xs]
        n = max(1, len(fp) // 10)
        cpu = [p['cpu_ms'] for _, p in xs if 'cpu_ms' in p]
        ins = [p['instructions'] for _, p in xs if 'instructions' in p]
        if max(fp) < 32 << 20 and sum(cpu) < 100:
            continue
        top = sorted(xs, key=lambda x: -x[1].get('cpu_ms', 0))[:5]
        s['processes'][role] = {
            'footprint_max_mib': round(max(fp) / 2**20), 'lifetime_max_mib': round(max(p['lifetime_max'] for _, p in xs) / 2**20),
            'footprint_first_tenth_mib': round(st.median(fp[:n]) / 2**20), 'footprint_last_tenth_mib': round(st.median(fp[-n:]) / 2**20),
            'cpu_ms_per_frame_median': round(st.median(cpu), 2) if cpu else None, 'cpu_ms_total': round(sum(cpu)),
            'instructions_per_frame_median': int(st.median(ins)) if ins else None,
            'cpu_top': [(r['key'], r['framing'], round(p.get('cpu_ms', 0))) for r, p in top],
            'footprint_top': [(r['key'], r['framing'], round(p['footprint'] / 2**20)) for r, p in sorted(xs, key=lambda x: -x[1]['footprint'])[:5]],
        }
    s['compute'] = {}
    for fr in sorted(set(r['framing'] for r in rows)):
        rr = [r for r in rows if r['framing'] == fr and r.get('encode_ms')]
        if not rr:
            continue
        enc = [sum(r['encode_ms']) for r in rr]
        gw = [sum(r['gpu_wait_ms']) for r in rr]
        s['compute'][fr] = {
            'encode_ms_median': round(st.median(enc), 2), 'encode_ms_p95': round(q(enc, 0.95), 2), 'encode_ms_max': round(max(enc), 1),
            'gpu_wait_ms_median': round(st.median(gw), 2), 'gpu_wait_ms_p95': round(q(gw, 0.95), 2), 'gpu_wait_ms_max': round(max(gw), 1),
            'encode_top': [(r['key'], round(sum(r['encode_ms']), 1)) for r in sorted(rr, key=lambda r: -sum(r['encode_ms']))[:5]],
            'gpu_top': [(r['key'], round(sum(r['gpu_wait_ms']), 1)) for r in sorted(rr, key=lambda r: -sum(r['gpu_wait_ms']))[:5]],
        }
    gpu = [p['gpu'] for p in procs if p.get('gpu')]
    if gpu:
        s['gpu_system'] = {'in_use_max_mib': round(max(g.get('In use system memory', 0) for g in gpu) / 2**20),
                           'device_util_median': st.median(g.get('Device Utilization %', 0) for g in gpu)}
    summary[job] = s

for job, s in summary.items():
    print(f"== {job}: {s['frames']} frames, {len(s['thrown'])} thrown, {len(s['died'])} died twice, "
          f"{len(s['device_errors'])} with device errors, {len(s['lost'])} lost, {s['reloads']} reloads")
    print(f"   vs native ({s['with_native']}): {s['identical']} identical, {s['beyond2']} beyond 2 levels, "
          f"{len(s['beyond8'])} beyond 8, max {s['max_level']}; {len(s['no_native'])} without a native frame")
    for x in s['beyond8'][:8]:
        print('     ', x)
    for x in (s['thrown'] + s['died'] + s['device_errors'] + s['lost'])[:8]:
        print('   !', x)
    print(f"   wasm heap max {s['wasm_heap_max_mib']} MiB, grew {len(s['wasm_heap_growth'])} times; last growths: {s['wasm_heap_growth'][-3:]}")
    for role, p in s['processes'].items():
        print(f"   {role}: footprint max {p['footprint_max_mib']} MiB (first tenth {p['footprint_first_tenth_mib']}, last tenth "
              f"{p['footprint_last_tenth_mib']}), lifetime max {p['lifetime_max_mib']}; cpu/frame {p['cpu_ms_per_frame_median']} ms, "
              f"total {p['cpu_ms_total']} ms; top {p['cpu_top'][:2]}")
    for fr, c in s['compute'].items():
        print(f"   {fr}: encode {c['encode_ms_median']} / p95 {c['encode_ms_p95']} / max {c['encode_ms_max']} ms; "
              f"queue {c['gpu_wait_ms_median']} / p95 {c['gpu_wait_ms_p95']} / max {c['gpu_wait_ms_max']} ms; "
              f"encode top {c['encode_top'][:2]}")
    if 'gpu_system' in s:
        print(f"   GPU (system): in use max {s['gpu_system']['in_use_max_mib']} MiB, device utilisation median {s['gpu_system']['device_util_median']} %")
if out_json:
    json.dump(summary, open(out_json, 'w'), indent=1)
