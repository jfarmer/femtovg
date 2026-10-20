#!/usr/bin/env python3
"""table.py : one consistent table over the devices - per phase, each variant's median steady frame (each frame's
median over its passes and legs first, as compare.py), and the change between the two medians."""
import csv, glob, json, os, statistics as st
from collections import defaultdict

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNS = {'a12': ['r2'], 'a13': ['r2'], 'a14': ['r2', 'r3'], 'atv15': ['r2'], 'atv10': ['r2']}


def per_frame(dev, prefixes):
    vals = defaultdict(lambda: defaultdict(list))
    for prefix in prefixes:
        for path in glob.glob(f'{HERE}/{dev}/frames-{prefix}-*.jsonl'):
            v = path.rsplit('-', 1)[1].split('.')[0]
            for line in open(path):
                r = json.loads(line)
                if r['rep'] < 1:
                    continue
                key = (r['phase'], r['file'], r['zoom'].lstrip('z'), r['rep'])
                for m in ('gpu_ms', 'read_mb', 'write_mb'):
                    if r.get(m) is not None:
                        vals[key][f'{v}:{m}:{prefix}'].append(r[m])
        for path in glob.glob(f'{HERE}/{dev}/soak-{prefix}-*.csv'):
            v = path.rsplit('-', 1)[1].split('.')[0]
            for r in csv.DictReader(open(path)):
                if int(r['rep']) < 1:
                    continue
                z = str(float(r['zoom'])).rstrip('0').rstrip('.')
                vals[(r['phase'], r['file'], z, int(r['rep']))][f'{v}:post_ms:{prefix}'].append(
                    float(r['wall_ms']) - float(r['encode_ms']))
    return vals


for dev, prefixes in RUNS.items():
    vals = per_frame(dev, prefixes)
    for phase in ('curvehd', 'buseyhd', 'busey', 'curve'):
        for m in ('gpu_ms', 'read_mb', 'write_mb', 'post_ms'):
            # A phase's frames come from one prefix: the A14's curve phases from r3, its BuseyBench from r2.
            best = None
            for prefix in prefixes:
                a = [st.median(p[f'pp:{m}:{prefix}']) for k, p in vals.items() if k[0] == phase and p.get(f'pp:{m}:{prefix}') and p.get(f'pc:{m}:{prefix}')]
                b = [st.median(p[f'pc:{m}:{prefix}']) for k, p in vals.items() if k[0] == phase and p.get(f'pp:{m}:{prefix}') and p.get(f'pc:{m}:{prefix}')]
                if a and (best is None or len(a) > len(best[0])):
                    best = (a, b, prefix)
            if not best:
                continue
            a, b, prefix = best
            ma, mb = st.median(a), st.median(b)
            lower = sum(y < x for x, y in zip(a, b))
            print(f'{dev:5s} {phase:7s} {m:8s} {ma:8.3f} -> {mb:8.3f} ({(mb - ma) / ma * 100:+5.1f} %)  sum {(sum(b) - sum(a)) / sum(a) * 100:+5.1f} %  lower {lower}/{len(a)}  [{prefix}]')
