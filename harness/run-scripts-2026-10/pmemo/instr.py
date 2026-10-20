"""instr.py TAG... -- file...  : instructions retired and cycles per frame of harness builds bin/_logos_full_TAG at
1080p, as the difference of a long (HI frames) and a short (LO frames) run under /usr/bin/time -l; REPEATS times,
builds interleaved; the median and the spread."""
import os, re, subprocess, sys
BIN = '/Users/matt/src/femtovg-wt/bin'; R = '/Users/matt/src/femtovg-wt/runs/pmemo'
ENV = {'FRAME_W': '1920', 'FRAME_H': '1080', 'BOX': '1080', 'BOX_X': '420', 'BOX_Y': '0', 'SKIP_UNSUPPORTED_FILTERS': '1',
       'VIEWPORT_CLIP': '1', 'LAYER_STATS': '1', 'TRANSIENT_BUDGET_MB': '1024', 'MEM_PEAKS': '1'}
args = sys.argv[1:]; i = args.index('--'); builds, files_ = args[:i], args[i + 1:]
lo, hi = int(os.environ.get('LO', 200)), int(os.environ.get('HI', 1200))
def run(build, f, frames):
    r = subprocess.run(['/usr/bin/time', '-l', f'{BIN}/_logos_full_{build}', '1', f'{R}/instr.ppm', f],
                       env={**os.environ, **ENV, 'FRAMES': str(frames)}, capture_output=True, text=True)
    g = lambda name: int(re.search(r'(\d+)\s+' + name, r.stderr).group(1))
    return g('instructions retired'), g('cycles elapsed')
for f in files_:
    rows = {b: [] for b in builds}
    for _ in range(int(os.environ.get('REPEATS', 3))):
        for b in builds:
            (i0, c0), (i1, c1) = run(b, f, lo), run(b, f, hi)
            rows[b].append(((i1 - i0) / (hi - lo), (c1 - c0) / (hi - lo)))
    base = None
    for b in builds:
        ins = sorted(r[0] for r in rows[b]); cyc = sorted(r[1] for r in rows[b])
        mi, mc = ins[len(ins) // 2], cyc[len(cyc) // 2]
        if base is None:
            base = (mi, mc)
        print(f"{os.path.basename(f)[:-4]:28s} {b:12s} instructions/frame {mi / 1e6:8.3f} M ({100 * (mi / base[0] - 1):+6.2f} %, spread {100 * (ins[-1] - ins[0]) / ins[0]:.2f} %)"
              f"  cycles/frame {mc / 1e6:8.3f} M ({100 * (mc / base[1] - 1):+6.2f} %, spread {100 * (cyc[-1] - cyc[0]) / cyc[0]:.2f} %)", flush=True)
