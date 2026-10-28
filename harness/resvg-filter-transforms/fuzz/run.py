#!/usr/bin/env python3
"""Runs every case in DIR with each resvg build under /usr/bin/time -l and a time limit, appending one JSON line per
(case, build) to results.jsonl: CPU seconds, peak RSS, exit status. Resumable.

  run.py DIR [workers=6] [limit=30] [builds=base,both]
"""
import json, os, subprocess, sys, tempfile, re
from concurrent.futures import ThreadPoolExecutor
BIN = os.path.expanduser('~/src/femtovg-wt/bin')
EXE = {'base': f'{BIN}/resvg-0.49.0', 'both': f'{BIN}/resvg-both'}
d = sys.argv[1]
opts = dict(a.split('=', 1) for a in sys.argv[2:])
workers, limit = int(opts.get('workers', 6)), float(opts.get('limit', 30))
MEM_MB = int(opts.get('mem', 2048))
builds = opts.get('builds', 'base,both').split(',')
res_path = f'{d}/results.jsonl'
done = set()
if os.path.exists(res_path):
    for l in open(res_path):
        r = json.loads(l); done.add((r['case'], r['build']))
def one(job):
    """Runs one case under /usr/bin/time -l, polling the child's RSS: past MEM_MB it is killed (macOS enforces no
    address-space limit), past `limit` seconds too."""
    import time
    case, build = job
    with tempfile.TemporaryDirectory() as t:
        p = subprocess.Popen(['/usr/bin/time', '-l', EXE[build], f'{d}/{case}', f'{t}/o.png'], stdout=subprocess.DEVNULL,
                             stderr=subprocess.PIPE, text=True)
        start, peak, status = time.time(), 0, None
        while p.poll() is None:
            time.sleep(0.05)
            try:
                kids = subprocess.run(['pgrep', '-P', str(p.pid)], capture_output=True, text=True).stdout.split()
                rss = sum(int(x or 0) for x in subprocess.run(['ps', '-o', 'rss=', '-p', ','.join(kids)], capture_output=True, text=True).stdout.split()) if kids else 0
            except Exception:
                rss = 0
            peak = max(peak, rss // 1024)
            if peak > MEM_MB:
                status = 'mem'
            elif time.time() - start > limit:
                status = 'timeout'
            if status:
                for k in kids:
                    subprocess.run(['kill', '-9', k])
                p.wait()
                break
        err = p.stderr.read()
        if status:
            return dict(case=case, build=build, cpu=round(time.time() - start, 3), rss_mb=peak, rc=status, panic=False, msg='')
        user = float(re.search(r'([\d.]+) user', err).group(1)); sys_ = float(re.search(r'([\d.]+) sys', err).group(1))
        rss = int(re.search(r'(\d+)\s+maximum resident set size', err).group(1))
        msg = next((l for l in err.splitlines() if 'panicked' in l or 'memory allocation' in l), '')[:200]
        return dict(case=case, build=build, cpu=round(user + sys_, 3), rss_mb=round(rss / 2**20, 1), rc=p.returncode,
                    panic='panicked' in err, msg=msg)
cases = sorted(f for f in os.listdir(d) if f.endswith('.svg'))
jobs = [(c, b) for c in cases for b in builds if (c, b) not in done]
with ThreadPoolExecutor(workers) as ex, open(res_path, 'a') as out:
    for i, r in enumerate(ex.map(one, jobs)):
        out.write(json.dumps(r) + '\n'); out.flush()
        if (i + 1) % 200 == 0: print(f'{i + 1}/{len(jobs)}', flush=True)
print('done', len(jobs))
