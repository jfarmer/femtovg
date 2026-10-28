"""memosim.py [LIMIT]  - the instrumented harness (pm_stats) over the corpus at 1080p, one frame a file: lookups in the
pipeline map and what memos of several sizes would catch. Writes memosim.jsonl."""
import json, os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
R = '/Users/matt/src/femtovg-wt/runs/pmemo'
ENV = {'FRAME_W': '1920', 'FRAME_H': '1080', 'BOX': '1080', 'BOX_X': '420', 'BOX_Y': '0', 'SKIP_UNSUPPORTED_FILTERS': '1',
       'VIEWPORT_CLIP': '1', 'TRANSIENT_BUDGET_MB': '1024', 'PIPELINE_MEMO_STATS': '1', 'FRAMES': '1'}
fs = json.load(open('/Users/matt/src/femtovg-wt/runs/pr/files.json'))
if len(sys.argv) > 1:
    fs = fs[::max(1, len(fs) // int(sys.argv[1]))]
def run(f):
    ppm = f"{R}/sim_{abs(hash(f['key'])) % 8}_{os.getpid()}_{f['key'][:40].replace('/', '_')}.ppm"
    try:
        r = subprocess.run(['/Users/matt/src/femtovg-wt/bin/_logos_full_pm_stats', '1', ppm, f['path']], env={**os.environ, **ENV},
                           capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired:
        return None
    finally:
        if os.path.exists(ppm):
            os.remove(ppm)
    rows = [l for l in r.stderr.split('\n') if l.startswith('MEMOSIM')]
    if not rows:
        return None
    tot = {'key': f['key'], 'renders': len(rows)}
    for l in rows:
        for k, v in re.findall(r'(\w+)=(\S+)', l):
            if k in ('fifo', 'lru'):
                d = tot.setdefault(k, {})
                for part in v.split(','):
                    n, h = part.split(':'); d[n] = d.get(n, 0) + int(h)
            elif k == 'distinct':
                tot[k] = max(tot.get(k, 0), int(v))
            else:
                tot[k] = tot.get(k, 0) + int(v)
    return tot
with ThreadPoolExecutor(6) as ex, open(f'{R}/memosim.jsonl', 'w') as out:
    n = 0
    for t in ex.map(run, fs):
        if t:
            out.write(json.dumps(t) + '\n'); n += 1
print(n, 'of', len(fs), 'files')
