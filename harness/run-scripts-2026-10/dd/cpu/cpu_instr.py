"""cpu_instr.py BUILD... -- FILE[@ZOOM]... : instructions per frame of bin/_path_cpu_BUILD (FRAMES=HI minus FRAMES=LO)."""
import os, re, subprocess, sys
args = sys.argv[1:]; i = args.index('--'); builds, fs = args[:i], args[i + 1:]
lo, hi, reps = int(os.environ.get('LO', 50)), int(os.environ.get('HI', 550)), int(os.environ.get('REPEATS', 5))
def run(b, f, z, n):
    r = subprocess.run(['/usr/bin/time', '-l', f'/Users/matt/src/femtovg-wt/bin/_path_cpu_{b}', f, z], env={**os.environ, 'FRAMES': str(n)}, capture_output=True, text=True)
    return int(re.search(r'(\d+)\s+instructions retired', r.stderr).group(1))
for spec in fs:
    f, _, z = spec.partition('@'); z = z or '1'
    base = None
    for b in builds:
        v = sorted((run(b, f, z, hi) - run(b, f, z, lo)) / (hi - lo) for _ in range(reps))
        med = v[len(v) // 2]; mn = v[0]; base = base or (med, mn)
        print(f'{os.path.basename(f)[:-4][:30]:30s} x{z:4s} {b:4s} median {med/1e6:8.4f} M/frame {100*(med/base[0]-1):+.2f} %, min {mn/1e6:8.4f} {100*(mn/base[1]-1):+.2f} % (spread {100*(v[-1]-v[0])/v[0]:.2f} %)', flush=True)
