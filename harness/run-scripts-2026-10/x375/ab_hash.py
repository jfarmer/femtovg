#!/usr/bin/env python3
"""ab_hash.py BIN_A BIN_B [match=REGEX] [env=NAME=VALUE,...] [workers=4] [out=NAME]
Renders every corpus frame (files.json of CORPUS_RUN_OUT, the four default framings) with two harness binaries and
compares the frames byte for byte. Rows go to ab_hash_<out>.jsonl in this directory; a second run resumes."""
import hashlib, json, os, re, subprocess, sys, concurrent.futures as cf
sys.path.insert(0, '/Users/matt/src/femtovg-wt/da/harness/corpus_run')
os.environ.setdefault('CORPUS_RUN_OUT', '/Users/matt/src/femtovg-wt/runs/pr')
from common import *
a, b = sys.argv[1:3]
opts = dict(x.split('=', 1) for x in sys.argv[3:])
extra = dict(p.split('=', 1) for p in opts.get('env', '').split(',') if p)
here = os.path.dirname(os.path.abspath(__file__))
path = f"{here}/ab_hash_{opts.get('out', 'run')}.jsonl"
done = {}
if os.path.exists(path):
    for l in open(path):
        r = json.loads(l); done[(r['key'], r['framing'])] = r
match = re.compile(opts['match']) if 'match' in opts else None
todo = [(f, fr) for f in files() if match is None or match.search(open(f['path'], errors='replace').read())
        for fr in DEFAULT_FRAMINGS]
os.makedirs(f'{here}/abtmp', exist_ok=True)

def render(binary, f, framing):
    env, z = FRAMINGS[framing]
    ppm = f"{here}/abtmp/{os.getpid()}_{abs(hash((binary, f['key'], framing))) % 10**10}.ppm"
    r = subprocess.run([binary, f'{z:g}', ppm, f['path']], capture_output=True, text=True, timeout=900,
                       env={**os.environ, **env, **SWEEP_ENV, **extra})
    if not os.path.exists(ppm):
        return None, None
    data = open(ppm, 'rb').read(); os.remove(ppm)
    held = re.search(r'transient bytes held at flush: (\d+)', r.stderr)
    return hashlib.sha1(data).hexdigest(), int(held.group(1)) if held else None

def one(item):
    f, fr = item
    if (f['key'], fr) in done:
        return done[(f['key'], fr)]
    (ha, ta), (hb, tb) = render(a, f, fr), render(b, f, fr)
    return {'key': f['key'], 'framing': fr, 'a': ha, 'b': hb, 'held_a': ta, 'held_b': tb}

out = open(path, 'a')
rows = []
with cf.ThreadPoolExecutor(int(opts.get('workers', 4))) as pool:
    for r in pool.map(one, todo):
        if (r['key'], r['framing']) not in done:
            out.write(json.dumps(r) + '\n'); out.flush()
        rows.append(r)
same = [r for r in rows if r['a'] and r['a'] == r['b']]
diff = [r for r in rows if r['a'] != r['b']]
failed = [r for r in rows if not r['a'] or not r['b']]
held = [r for r in rows if r['held_a'] != r['held_b']]
print(f"{len(rows)} frames of {len(set(r['key'] for r in rows))} files: {len(same)} identical, {len(diff)} differ, "
      f"{len(failed)} without a frame; transient bytes at the flush differ on {len(held)}")
for r in diff[:20]: print('  differs:', r['key'], r['framing'])
for r in held[:10]: print('  held:', r['key'], r['framing'], r['held_a'], r['held_b'])
