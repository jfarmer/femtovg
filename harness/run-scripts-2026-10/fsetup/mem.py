"""mem.py TAG... -- file...  - memory of harness builds at 1080p (MEM_PEAKS, MEM_SETTLE_MS=500): the process footprint and
graphics memory over the idle baseline at the frames' peak, after the last frame and half a second later, in MiB;
the median of REPEATS runs."""
import os, re, statistics as st, subprocess, sys
BIN = '/Users/matt/src/femtovg-wt/bin'; R = '/Users/matt/src/femtovg-wt/runs/fsetup'
ENV = {'FRAME_W': '1920', 'FRAME_H': '1080', 'BOX': '1080', 'BOX_X': '420', 'BOX_Y': '0', 'SKIP_UNSUPPORTED_FILTERS': '1',
       'VIEWPORT_CLIP': '1', 'TRANSIENT_BUDGET_MB': '1024', 'MEM_PEAKS': '1', 'MEM_SETTLE_MS': '500', 'FRAMES': os.environ.get('FRAMES', '20')}
args = sys.argv[1:]; i = args.index('--'); tags, files = args[:i], args[i + 1:]
mib = lambda b: b / 2 ** 20
for f in files:
    for tag in tags:
        rows = []
        for _ in range(int(os.environ.get('REPEATS', 3))):
            r = subprocess.run([f'{BIN}/_logos_full_{tag}', '1', f'{R}/mem.ppm', f], env={**os.environ, **ENV}, capture_output=True, text=True, timeout=1800)
            g = lambda k: int(re.search(k + r'=(\d+)', r.stderr).group(1))
            rows.append((g('peak_footprint') - g('baseline_footprint'), g('after_footprint') - g('baseline_footprint'), g('settled_footprint') - g('baseline_footprint'),
                         g('peak_graphics') - g('baseline_graphics'), g('settled_graphics') - g('baseline_graphics')))
        m = [st.median(r[k] for r in rows) for k in range(5)]
        print(f"{os.path.basename(f)[:-4][:40]:40s} {tag:8s} footprint peak {mib(m[0]):7.1f}  after {mib(m[1]):7.1f}  settled {mib(m[2]):7.1f} MiB | graphics peak {mib(m[3]):7.1f}  settled {mib(m[4]):7.1f} MiB", flush=True)
    os.remove(f'{R}/mem.ppm')
