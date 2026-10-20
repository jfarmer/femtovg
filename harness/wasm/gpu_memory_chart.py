#!/usr/bin/env python3
"""gpu_memory_chart.py RUN_DIR OUT.png LABEL=JOB[:ROLE] ... : the GPU process's footprint after each file of timing
jobs (BuseyBench then the perf scenes, 1x and 1080p, ten frames each), one line per job; ROLE picks the sampled
process (default gpu-process; the largest of several). Marks where the perf scenes with 1,000 gradients and 4,000
rects come."""
import json, sys
from PIL import Image, ImageDraw, ImageFont

run, out, *series = sys.argv[1:]
font = lambda s: ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', s)
COLORS = [(214, 39, 40), (255, 127, 14), (31, 119, 180), (44, 160, 44), (148, 103, 189), (140, 86, 75)]
lines, marks = [], {}
for spec in series:
    label, job = spec.split('=', 1)
    role = 'gpu-process'
    if ':' in job:
        job, role = job.split(':', 1)
    rows = sorted((json.loads(l) for l in open(f'{run}/{job}/results.jsonl')), key=lambda r: r['t'])
    pts = []
    for i, r in enumerate(rows):
        vals = [v['footprint'] / 2**20 for k, v in (r.get('procs') or {}).items() if k.split(':')[0].rstrip('?') == role]
        if vals:
            pts.append((i, max(vals)))
        for scene in ('grads-1000', 'rects-4000'):
            if r['key'].endswith(scene) and scene not in marks:
                marks[scene] = i
    lines.append((label, pts))

W, H, L, R, T, B = 900, 420, 70, 20, 40, 60
top = max(y for _, pts in lines for _, y in pts) * 1.08
n = max(x for _, pts in lines for x, _ in pts) + 1
img = Image.new('RGB', (W, H), 'white')
d = ImageDraw.Draw(img)
X = lambda x: L + (W - L - R) * x / max(1, n - 1)
Y = lambda y: H - B - (H - B - T) * y / top
for gb in range(0, int(top // 512) + 1):
    y = gb * 512
    d.line([(L, Y(y)), (W - R, Y(y))], fill=(230, 230, 230))
    d.text((8, Y(y) - 7), f'{y:,} MiB', fill=(90, 90, 90), font=font(11))
for scene, i in marks.items():
    d.line([(X(i), T), (X(i), H - B)], fill=(180, 180, 180))
    d.text((X(i) + 3, T), scene, fill=(90, 90, 90), font=font(11))
d.text((L, H - B + 8), 'BuseyBench (36 portraits)', fill=(90, 90, 90), font=font(11))
d.text((X(n * 0.68), H - B + 8), 'synthetic scenes', fill=(90, 90, 90), font=font(11))
d.text((L, 10), "GPU process footprint after each frame set (ten frames, 460x260 and 1080p), femtovg master 06243b80 on WebGPU",
       fill='black', font=font(13))
for k, (label, pts) in enumerate(lines):
    c = COLORS[k % len(COLORS)]
    d.line([(X(x), Y(y)) for x, y in pts], fill=c, width=2)
    d.text((L + 10 + k * 205, H - 28), f'— {label}', fill=c, font=font(12))
img.save(out)
print('wrote', out, img.size)
