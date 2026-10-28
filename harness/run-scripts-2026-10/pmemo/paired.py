"""paired.py PAIRS FRAMES BEFORE AFTER file...  - steady-state frame and encode time of two harness builds
(bin/_logos_full_TAG) at 1080p, back to back with the order alternating: medians, and the median of the paired
differences, for frame_ms (a frame, the wait for the GPU included) and encode_ms (recording and encoding it,
before the submit). Rows are appended to paired.jsonl."""
import json, os, re, statistics as st, subprocess, sys, time
BIN = '/Users/matt/src/femtovg-wt/bin'; R = '/Users/matt/src/femtovg-wt/runs/pmemo'
ENV = {'FRAME_W': '1920', 'FRAME_H': '1080', 'BOX': '1080', 'BOX_X': '420', 'BOX_Y': '0', 'SKIP_UNSUPPORTED_FILTERS': '1',
       'VIEWPORT_CLIP': '1', 'LAYER_STATS': '1', 'TRANSIENT_BUDGET_MB': '1024', 'MEM_PEAKS': '1'}
pairs, frames, before, after = int(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4]
def run(build, f):
    r = subprocess.run([f'{BIN}/_logos_full_{build}', '1', f'{R}/paired_{os.getpid()}.ppm', f], env={**os.environ, **ENV, 'FRAMES': frames},
                       capture_output=True, text=True, timeout=1800)
    return float(re.search(r'frame_ms=([\d.]+)', r.stderr).group(1)), float(re.search(r'encode_ms=([\d.]+)', r.stderr).group(1))
def line(name, x, y):
    d = [q - p for p, q in zip(x, y)]
    return (f"{name} {st.median(x):.3f} -> {st.median(y):.3f} ms, paired difference {st.median(d):+.4f} ms ({100 * st.median(d) / st.median(x):+.1f} %), "
            f"{after} slower in {sum(v > 0 for v in d)} of {len(d)}, range {100 * min(d) / st.median(x):+.1f}..{100 * max(d) / st.median(x):+.1f} %")
for f in sys.argv[5:]:
    load0 = os.getloadavg()[0]
    a, b = [], []
    for i in range(pairs):
        if i % 2 == 0:
            p = run(before, f); q = run(after, f)
        else:
            q = run(after, f); p = run(before, f)
        a.append(p); b.append(q)
    name = os.path.basename(f)[:-4]
    print(f"{name} ({pairs} pairs of {frames} frames, load {load0:.1f}..{os.getloadavg()[0]:.1f}):", flush=True)
    print('  ' + line('encode', [v[1] for v in a], [v[1] for v in b]), flush=True)
    print('  ' + line('frame ', [v[0] for v in a], [v[0] for v in b]), flush=True)
    with open(f'{R}/paired.jsonl', 'a') as out:
        out.write(json.dumps({'file': name, 'before': before, 'after': after, 'frames': frames, 'time': time.strftime('%H:%M:%S'),
                              'load': [load0, os.getloadavg()[0]], before: a, after: b}) + '\n')
    os.remove(f'{R}/paired_{os.getpid()}.ppm')
