"""cb_instr.py BUILD... -- FILE... : PathCache::new + expand_fill instructions per pass over a file's paths (bin/_cb_BUILD)."""
import os, re, subprocess, sys
args = sys.argv[1:]; i = args.index('--'); builds, fs = args[:i], args[i + 1:]
lo, hi, reps = int(os.environ.get('LO', 20)), int(os.environ.get('HI', 220)), int(os.environ.get('REPEATS', 7))
def run(b, f, n):
    r = subprocess.run(['/usr/bin/time', '-l', os.path.join(os.environ.get('HARNESS_BIN', 'bin'), f'_fb_{b}'), 'fill_bench', '--exact', 'path::cache::fill_bench::fill_bench', '--test-threads=1', '--nocapture'],
                       env={**os.environ, 'CB_FILE': f, 'CB_N': str(n)}, capture_output=True, text=True)
    pts = re.search(r'CB points/iter (\d+)', r.stderr).group(1)
    return int(re.search(r'(\d+)\s+instructions retired', r.stderr).group(1)), pts
for f in fs:
    base = None
    for b in builds:
        v = []
        for _ in range(reps):
            (h, pts), (l, _) = run(b, f, hi), run(b, f, lo)
            v.append((h - l) / (hi - lo))
        v.sort(); med = v[len(v) // 2]; base = base or med
        print(f'{os.path.basename(f)[:-4][:28]:28s} {b:4s} {med/1e3:9.1f} k instr per pass ({pts} points, {med/int(pts):6.1f} per point) spread {100*(v[-1]-v[0])/v[0]:.2f} % {100*(med/base-1):+.2f} %', flush=True)
