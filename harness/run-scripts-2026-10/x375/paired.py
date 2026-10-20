#!/usr/bin/env python3
"""paired.py ROUNDS BUILD_A BUILD_B [VAR=VALUE ...] - two harness builds alternating on a fixed set of portrait frames,
FRAMES=20 each; per frame the median frame_ms of each build and the change. Extra VAR=VALUE go to both builds."""
import os, re, statistics, subprocess, sys
rounds, A, B = int(sys.argv[1]), sys.argv[2], sys.argv[3]
# A build is TAG or TAG@VAR=VALUE,... (environment for that build only).
extra = dict(a.split('=', 1) for a in sys.argv[4:])
D = '/Users/matt/src/femtovg-wt/da/corpus/buseybench'
Z = dict(FRAME_W='460', FRAME_H='260', BOX='200', BOX_X='130', BOX_Y='30')
H = dict(FRAME_W='1920', FRAME_H='1080', BOX='1080', BOX_X='420', BOX_Y='0')
frames = [('glm-5-3', 'z', 1), ('glm-5-3', 'z', 3), ('glm-5-3', 'z', 4), ('glm-5-3', 'z', 4.5), ('glm-5-3', 'z', 8),
          ('qwen3-8-2-4t-a95b', 'z', 4), ('gemini-3-1-pro-preview', 'hd', 1), ('claude-fable-5-1', 'hd', 1),
          ('qwen3-8-flash', 'hd', 1), ('gemini-3-1-pro-preview-custom-tools', 'hd', 1)]
if os.environ.get('ONLY'):
    frames = [f for f in frames if re.search(os.environ['ONLY'], f'{f[0]} {f[1]} {f[2]}')]
def run(build, f):
    name, fr, z = f
    build, _, own = build.partition('@')
    own = dict(a.split('=', 1) for a in own.split(',') if a)
    env = {**os.environ, **(H if fr == 'hd' else Z), 'SKIP_UNSUPPORTED_FILTERS': '1', 'VIEWPORT_CLIP': '1',
           'TRANSIENT_BUDGET_MB': '1024', 'MEM_PEAKS': '1', 'MEM_SETTLE_MS': '0', 'FRAMES': '20', **extra, **own}
    ppm = f'/Users/matt/src/femtovg-wt/runs/x375/p_{build}.ppm'
    r = subprocess.run([f'/Users/matt/src/femtovg-wt/bin/_logos_full_{build}', str(z), ppm, f'{D}/{name}.svg'],
                       capture_output=True, text=True, env=env)
    m = re.search(r'frame_ms=([\d.]+)', r.stderr)
    return float(m.group(1)) if m else float('nan')
t = {(f, b): [] for f in frames for b in (A, B)}
for r in range(rounds):
    for f in frames:
        for b in ((A, B) if r % 2 == 0 else (B, A)):
            t[(f, b)].append(run(b, f))
    print(f'round {r + 1} done, load {os.getloadavg()[0]:.1f}', file=sys.stderr, flush=True)
for f in frames:
    a, b = statistics.median(t[(f, A)]), statistics.median(t[(f, B)])
    print(f"{f[0]:38s} {f[1]}{f[2]:<4} {A} {a:7.1f}  {B} {b:7.1f}  {100 * (b - a) / a:+6.1f} %   "
          f"{[round(x, 1) for x in t[(f, A)]]} {[round(x, 1) for x in t[(f, B)]]}")
for b in (A, B):
    p = f"/Users/matt/src/femtovg-wt/runs/x375/p_{b.partition('@')[0]}.ppm"
    if os.path.exists(p): os.remove(p)
