"""scan.py BUILD  - the counter build (bin/_logos_full_BUILD, FS_STATS) over every corpus file at 1080p, one frame a
file: commands, render passes, viewport bind groups created, staging regrowths and the bytes written to the vertex,
index and uniform buffers. Writes scan.jsonl."""
import json, os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
R = '/Users/matt/src/femtovg-wt/runs/fsetup'
ENV = {'FRAME_W': '1920', 'FRAME_H': '1080', 'BOX': '1080', 'BOX_X': '420', 'BOX_Y': '0', 'SKIP_UNSUPPORTED_FILTERS': '1',
       'VIEWPORT_CLIP': '1', 'TRANSIENT_BUDGET_MB': '1024', 'FS_STATS': '1', 'LAYER_STATS': '1', 'FRAMES': '1'}
files = json.load(open('/Users/matt/src/femtovg-wt/runs/fsetup/files.json'))
def run(i_f):
    i, f = i_f
    ppm = f'{R}/scan_{i}.ppm'
    try:
        r = subprocess.run([f'/Users/matt/src/femtovg-wt/bin/_logos_full_{sys.argv[1]}', '1', ppm, f['path']], env={**os.environ, **ENV},
                           capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired:
        return None
    finally:
        if os.path.exists(ppm):
            os.remove(ppm)
    rows = [l for l in r.stderr.split('\n') if l.startswith('FSSTATS')]
    if not rows:
        return {'key': f['key'], 'path': f['path'], 'failed': r.returncode}
    row = {'key': f['key'], 'path': f['path']}
    row.update({k: int(v) for k, v in re.findall(r'(\w+)=(\d+)', rows[-1])})
    m = re.search(r'layers begun: (\d+)', r.stderr)
    row['layers'] = int(m.group(1)) if m else None
    return row
with ThreadPoolExecutor(6) as ex, open(f'{R}/scan.jsonl', 'w') as out:
    for row in ex.map(run, enumerate(files)):
        if row:
            out.write(json.dumps(row) + '\n')
