#!/usr/bin/env python3
"""pair_sweep.py BEFORE AFTER [workers=4] [framings=z1,z2,z4,hd]  (run through tool.py)

Renders every corpus frame with both builds; appends both rows to accuracy.jsonl as accuracy.py writes them
(hash, layer stats, cfgs), and keeps the PNGs of both builds only where the hashes differ (png_changed).
Resumable: a (key, framing) with rows for both builds is skipped."""
import hashlib, json, os, re, shutil, subprocess, sys, threading, time
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
from common import *

before, after = sys.argv[1:3]
opts = dict(a.split('=', 1) for a in sys.argv[3:])
workers = int(opts.get('workers', 4))
framings = opts.get('framings', ','.join(DEFAULT_FRAMINGS)).split(',')
STATS = {'layers': r'layers begun: (\d+)', 'pass_through': r'layers passed through: (\d+)',
         'skipped': r'filters skipped \(SKIP_UNSUPPORTED_FILTERS\): (\d+)'}
os.makedirs(f'{OUT}/png_changed', exist_ok=True)
os.makedirs(f'{OUT}/tmp', exist_ok=True)


def render(f, framing, build):
    binary, extra = BUILDS[build]
    fr, z = FRAMINGS[framing]
    ppm = f'{OUT}/tmp/pair_{os.getpid()}_{threading.get_ident()}_{build}.ppm'
    if os.path.exists(ppm):
        os.remove(ppm)
    while shutil.disk_usage('/').free < 1.5e9:
        print('disk under 1.5 GB free, waiting', flush=True)
        time.sleep(20)
    row = {'key': f['key'], 'group': f['group'], 'framing': framing, 'build': build}
    try:
        r = subprocess.run([binary, f'{z:g}', ppm, f['path']], env={**os.environ, **fr, **SWEEP_ENV, **extra},
                           capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired:
        row['error'] = 'timeout'
        return row, None
    row['rc'] = r.returncode
    for name, pattern in STATS.items():
        m = re.search(pattern, r.stderr)
        if m:
            row[name] = int(m.group(1))
    m = re.search(r'harness cfgs: (.*)', r.stderr)
    if m:
        row['cfgs'] = m.group(1).strip()
    if r.returncode != 0 or not os.path.exists(ppm):
        row['error'] = r.stderr.strip()[-400:]
        return row, None
    row['hash'] = hashlib.sha1(open(ppm, 'rb').read()).hexdigest()
    return row, ppm


rows = {}
for line in open(f'{OUT}/accuracy.jsonl'):
    r = json.loads(line)
    rows[(r['key'], r['framing'], r['build'])] = r
out = open(f'{OUT}/accuracy.jsonl', 'a')
lock = threading.Lock()
counts = [0, 0, 0]  # pairs, changed, errors


def job(args):
    f, framing = args
    (rb, pb), (ra, pa) = render(f, framing, before), render(f, framing, after)
    changed = pb and pa and rb['hash'] != ra['hash']
    if changed:
        for build, p in ((before, pb), (after, pa)):
            Image.open(p).save(f'{OUT}/png_changed/{build}_{f["key"]}_{framing}.png')
    for p in (pb, pa):
        if p:
            os.remove(p)
    with lock:
        out.write(json.dumps(rb) + '\n')
        out.write(json.dumps(ra) + '\n')
        out.flush()
        counts[0] += 1
        counts[1] += bool(changed)
        counts[2] += not (pb and pa)
        if counts[0] % 500 == 0:
            print(time.strftime('%H:%M:%S'), counts, flush=True)


jobs = [(f, fr) for f in files() for fr in framings
        if (f['key'], fr, before) not in rows or (f['key'], fr, after) not in rows]
print(f'{len(jobs)} frame pairs to render', flush=True)
with ThreadPoolExecutor(workers) as ex:
    list(ex.map(job, jobs))
print('done: pairs, changed, errors =', counts, flush=True)
