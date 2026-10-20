import os, re, subprocess, statistics, sys
env = {**os.environ, 'FRAME_W': '1920', 'FRAME_H': '1080', 'BOX': '1080', 'BOX_X': '420', 'BOX_Y': '0', 'SKIP_UNSUPPORTED_FILTERS': '1',
       'VIEWPORT_CLIP': '1', 'TRANSIENT_BUDGET_MB': '1024', 'SINGLE_SHADOW_LAYER': '1', 'MEM_PEAKS': '1', 'FRAMES': '300'}
for f in sys.argv[1:]:
    res = {'m8': [], 'dc': []}
    for _ in range(7):
        for b in ('m8', 'dc'):
            r = subprocess.run([f'/Users/matt/src/femtovg-wt/bin/_logos_full_{b}', '1', f'/Users/matt/src/femtovg-wt/runs/dc/tmp/tm_{b}.ppm', f], env=env, capture_output=True, text=True)
            m = re.search(r'frame_ms=([\d.]+).*encode_ms=([\d.]+)', r.stderr)
            res[b].append((float(m.group(1)), float(m.group(2))))
    med = {b: (statistics.median(x[0] for x in v), statistics.median(x[1] for x in v)) for b, v in res.items()}
    print(f"{os.path.basename(f)[:-4][:32]:32s} frame {med['m8'][0]:.3f} -> {med['dc'][0]:.3f} ms, encode {med['m8'][1]:.3f} -> {med['dc'][1]:.3f} ms")
