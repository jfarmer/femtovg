"""calls.py REPEATS FRAMES file...  - the timing build (bin/_logos_full_fs_time, upstream master with timers around the
setup calls) at 1080p, REPEATS runs a file, each after gate.quiet(): microseconds a frame in the viewport bind groups,
the three write_buffer calls and encoder.finish(), and render() in all; medians over the runs."""
import os, re, statistics as st, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gate import quiet
R = '/Users/matt/src/femtovg-wt/runs/fsetup'
ENV = {'FRAME_W': '1920', 'FRAME_H': '1080', 'BOX': '1080', 'BOX_X': '420', 'BOX_Y': '0', 'SKIP_UNSUPPORTED_FILTERS': '1',
       'VIEWPORT_CLIP': '1', 'TRANSIENT_BUDGET_MB': '1024', 'FS_TIME': '1'}
repeats, frames = int(sys.argv[1]), sys.argv[2]
for f in sys.argv[3:]:
    rows, loads = [], []
    for _ in range(repeats):
        loads.append(quiet())
        r = subprocess.run(['/Users/matt/src/femtovg-wt/bin/_logos_full_fs_time', '1', f'{R}/calls.ppm', f], env={**os.environ, **ENV, 'FRAMES': frames},
                           capture_output=True, text=True)
        line = [l for l in r.stderr.split('\n') if l.startswith('FSTIME')][-1]
        rows.append({k: float(v) for k, v in re.findall(r'(\w+)=([\d.]+)', line)})
    os.remove(f'{R}/calls.ppm')
    m = {k: st.median(r[k] for r in rows) for k in rows[0]}
    each = m['viewport_us'] / max(m['viewport_n'], 1)
    print(f"{os.path.basename(f)[:-4]}: render {m['render_us']:.0f} us a frame; viewport groups {m['viewport_n']:.0f} x {each:.2f} us = {m['viewport_us']:.1f} us; "
          f"write_buffer vertices {m['write_vertex_us']:.1f}, fan indices {m['write_index_us']:.1f}, uniforms {m['write_uniform_us']:.1f} us; "
          f"encoder.finish {m['finish_us']:.0f} us  (others' CPU median {st.median(loads):.0f} %)", flush=True)
