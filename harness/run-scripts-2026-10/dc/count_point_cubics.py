"""count_point_cubics.py: per corpus file, the cubics (and quads) whose points all equal the current point, from the
harness's PATH_DUMP of master (bin/_logos_full_m8) at 1x."""
import json, os, re, subprocess, collections
from concurrent.futures import ThreadPoolExecutor
files = json.load(open('/Users/matt/src/femtovg-wt/runs/dd/files.json'))
env = {**os.environ, 'FRAME_W': '460', 'FRAME_H': '260', 'BOX': '200', 'BOX_X': '130', 'BOX_Y': '30',
       'SKIP_UNSUPPORTED_FILTERS': '1', 'VIEWPORT_CLIP': '1', 'TRANSIENT_BUDGET_MB': '1024', 'SINGLE_SHADOW_LAYER': '1', 'PATH_DUMP': '1'}
P = r'Point \{ x: ([-\d.e]+), y: ([-\d.e]+) \}'
def job(f):
    ppm = f'/Users/matt/src/femtovg-wt/runs/dc/tmp/c_{abs(hash(f["key"]))}.ppm'
    r = subprocess.run(['/Users/matt/src/femtovg-wt/bin/_logos_full_m8', '1', ppm, f['path']], env=env, capture_output=True, text=True, timeout=300)
    if os.path.exists(ppm): os.remove(ppm)
    cur = start = None; n = cubics = 0
    for line in r.stderr.splitlines():
        line = line.strip()
        pts = [(float(a), float(b)) for a, b in re.findall(P, line)]
        if line.startswith('MoveTo'): cur = start = pts[0]
        elif line.startswith('LineTo'): cur = pts[0]
        elif line.startswith('CubicTo') or line.startswith('QuadTo'):
            cubics += 1
            if all(p == cur for p in pts): n += 1
            cur = pts[-1]
        elif line.startswith('Close'): cur = start
    return f['key'], f['group'], n, cubics
rows = []
with ThreadPoolExecutor(6) as ex:
    rows = list(ex.map(job, files))
json.dump(rows, open('point_cubics.json', 'w'))
hit = [r for r in rows if r[2]]
print(f'{len(hit)} of {len(rows)} files have point cubics; {sum(r[2] for r in rows)} of {sum(r[3] for r in rows)} curves')
print('by group:', collections.Counter(r[1] for r in hit).most_common())
for r in sorted(hit, key=lambda r: -r[2])[:15]: print(f'   {r[2]:5d} of {r[3]:6d}  {r[0][-60:]}')
