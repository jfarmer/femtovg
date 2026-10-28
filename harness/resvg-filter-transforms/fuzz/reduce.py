#!/usr/bin/env python3
"""Greedy reducer for a fuzz case: drops filter primitives, transform functions, filter attributes and wrapper groups
while the predicate still holds for the build, and writes CASE.min.svg.

  reduce.py CASE.svg BUILD PREDICATE      PREDICATE: panic | mem | timeout | cpu>SECONDS | rss>MB
"""
import os, re, subprocess, sys, tempfile, time

case, build, pred = sys.argv[1:4]
EXE = {'base': '~/src/femtovg-wt/bin/resvg-0.49.0', 'both': '~/src/femtovg-wt/bin/resvg-both'}[build]
EXE = os.path.expanduser(EXE)
LIMIT, MEM = float(os.environ.get("LIMIT", 20)), 2048


def measure(src):
    with tempfile.TemporaryDirectory() as t:
        open(f'{t}/c.svg', 'w').write(src)
        p = subprocess.Popen(['/usr/bin/time', '-l', EXE, f'{t}/c.svg', f'{t}/o.png'], stdout=subprocess.DEVNULL,
                             stderr=subprocess.PIPE, text=True)
        start, peak, status = time.time(), 0, None
        while p.poll() is None:
            time.sleep(0.05)
            kids = subprocess.run(['pgrep', '-P', str(p.pid)], capture_output=True, text=True).stdout.split()
            if kids:
                out = subprocess.run(['ps', '-o', 'rss=', '-p', ','.join(kids)], capture_output=True, text=True).stdout.split()
                peak = max(peak, sum(int(x) for x in out) // 1024)
            if peak > MEM:
                status = 'mem'
            elif time.time() - start > LIMIT:
                status = 'timeout'
            if status:
                for k in kids:
                    subprocess.run(['kill', '-9', k])
                p.wait()
                return dict(status=status, cpu=time.time() - start, rss=peak)
        err = p.stderr.read()
        cpu = float(re.search(r'([\d.]+) user', err).group(1)) + float(re.search(r'([\d.]+) sys', err).group(1))
        rss = int(re.search(r'(\d+)\s+maximum resident set size', err).group(1)) / 2**20
        return dict(status='panic' if 'panicked' in err else 'ok', cpu=cpu, rss=rss)


def holds(src):
    m = measure(src)
    if pred in ('panic', 'mem', 'timeout'):
        return m['status'] == pred
    k, v = pred.split('>')
    return m['status'] in ('mem', 'timeout') or m[k] > float(v)


src = open(case).read()
assert holds(src), 'predicate does not hold on the original'
changed = True
while changed:
    changed = False
    # Candidate edits: drop one primitive line, one transform function, one attribute of <filter>, one wrapper <g>.
    cands = []
    for line in src.splitlines():
        if line.strip().startswith('<fe'):
            cands.append(src.replace(line + '\n', '', 1))
    for m in re.finditer(r'transform="([^"]*)"', src):
        funcs = re.findall(r'[a-zA-Z]+\([^)]*\)', m.group(1))
        for f in funcs:
            cands.append(src[:m.start(1)] + m.group(1).replace(f, '', 1).strip() + src[m.end(1):])
    fm = re.search(r'<filter [^>]*>', src)
    for a in re.findall(r' (?:x|y|width|height|filterUnits|primitiveUnits)="[^"]*"', fm.group(0)):
        cands.append(src.replace(fm.group(0), fm.group(0).replace(a, '', 1), 1))
    for m in re.finditer(r'<g transform="[^"]*"(?: filter="url\(#f\)")?>', src):
        inner = src[m.end():]
        j = inner.rfind('</g>')
        cands.append(src[:m.start()] + inner[:j] + inner[j + 4:])
    for c in cands:
        if c != src and holds(c):
            src, changed = c, True
            break
out = case[:-4] + '.min.svg'
open(out, 'w').write(src)
print(out)
print(src)
