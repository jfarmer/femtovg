"""rr.py ROUNDS FRAMES TAG... -- file...  - harness builds bin/_logos_full_TAG at 1080p, round-robin: each round runs
every build once, in turn, the order reversed every other round. For each file: median encode_ms (recording and
encoding the frame, before the submit) and frame_ms (the frame, the wait for the GPU included) of each build, and the
median of its per-round differences from the first build, with how many rounds it was slower. Rows go to rr.jsonl."""
import json, os, re, statistics as st, subprocess, sys, time
BIN = '/Users/matt/src/femtovg-wt/bin'; R = '/Users/matt/src/femtovg-wt/runs/fsetup'
ENV = {'FRAME_W': '1920', 'FRAME_H': '1080', 'BOX': '1080', 'BOX_X': '420', 'BOX_Y': '0', 'SKIP_UNSUPPORTED_FILTERS': '1',
       'VIEWPORT_CLIP': '1', 'LAYER_STATS': '1', 'TRANSIENT_BUDGET_MB': '1024', 'MEM_PEAKS': '1'}
args = sys.argv[1:]; i = args.index('--')
rounds, frames, tags, files = int(args[0]), args[1], args[2:i], args[i + 1:]
def busy():
    """Percent CPU the other processes use, from ps (each process's recent average)."""
    out = subprocess.run(['ps', '-Ao', 'pcpu=,comm='], capture_output=True, text=True).stdout
    return sum(float(l.split(None, 1)[0]) for l in out.splitlines() if l.strip() and '_logos_full_' not in l)
def quiet(limit=float(os.environ.get('BUSY_LIMIT', 250)), longest=float(os.environ.get('BUSY_WAIT', 900))):
    """Waits, up to `longest` seconds, until the rest of the machine uses less than `limit` percent CPU twice in a row."""
    start = time.time()
    while time.time() - start < longest:
        if busy() < limit:
            time.sleep(2)
            if busy() < limit:
                break
        time.sleep(5)
    return busy()
def run(tag, f):
    ppm = f'{R}/rr_{os.getpid()}.ppm'
    r = subprocess.run([f'{BIN}/_logos_full_{tag}', '1', ppm, f], env={**os.environ, **ENV, 'FRAMES': frames}, capture_output=True, text=True, timeout=3600)
    os.remove(ppm)
    g = lambda k: float(re.search(k + r'=([\d.]+)', r.stderr).group(1))
    return g('encode_ms'), g('frame_ms')
for f in files:
    load0 = os.getloadavg()[0]
    t = {tag: [] for tag in tags}
    loads = []
    for rnd in range(rounds):
        loads.append(quiet())
        for tag in (tags if rnd % 2 == 0 else tags[::-1]):
            t[tag].append(run(tag, f))
    name = os.path.basename(f)[:-4]
    print(f"{name} ({rounds} rounds of {frames} frames, load {load0:.1f}..{os.getloadavg()[0]:.1f}, other processes' CPU at round starts median {st.median(loads):.0f} %, max {max(loads):.0f} %)", flush=True)
    base = t[tags[0]]
    for k, label in ((0, 'encode'), (1, 'frame ')):
        b = st.median(v[k] for v in base)
        cols = [f"{tags[0]} {b:.3f}"]
        for tag in tags[1:]:
            d = [y[k] - x[k] for x, y in zip(base, t[tag])]
            cols.append(f"{tag} {st.median(v[k] for v in t[tag]):.3f} ({100 * st.median(d) / b:+.1f} %, slower in {sum(v > 0 for v in d)}/{len(d)})")
        print(f"  {label} ms  " + '   '.join(cols), flush=True)
    with open(f'{R}/rr.jsonl', 'a') as out:
        out.write(json.dumps({'file': name, 'frames': frames, 'time': time.strftime('%H:%M:%S'), 'load': [load0, os.getloadavg()[0]], 'busy': loads, 'runs': t}) + '\n')
