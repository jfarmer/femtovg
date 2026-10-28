"""capdiscs.py: opus with every unfiltered open round-capped stroke rewritten as butt caps + discs of r=w/2 (same geometry)."""
import re, json
import sys; NAME = sys.argv[1]; SRC = f'/Users/matt/src/femtovg-wt/da/corpus/buseybench/{NAME}.svg'
D = '/Users/matt/src/femtovg-wt/runs/busey/triage/new-five-r2-verify'
A = lambda s, k: (re.search(rf'\s{k}="([^"]*)"', s) or [None, None])[1]
out = []; stack = []; n = 0; touched = []
for i, line in enumerate(open(SRC).read().split('\n'), 1):
    s = line.strip()
    if s.startswith('<g') and not s.endswith('/>'):
        stack.append({k: A(s, k) for k in ('stroke', 'stroke-width', 'stroke-linecap', 'filter', 'opacity')})
    elif s.startswith('</g'):
        stack.pop() if stack else None
    if s.startswith('<path') and s.endswith('/>'):
        eff = {}
        for g in stack:
            for k, v in g.items():
                if v is not None: eff[k] = v
        for k in ('stroke', 'stroke-width', 'stroke-linecap', 'filter'):
            v = A(s, k)
            if v is not None: eff[k] = v
        d = A(s, 'd')
        filt = any(g.get('filter') for g in stack) or A(s, 'filter')
        if eff.get('stroke-linecap') == 'round' and eff.get('stroke') not in (None, 'none') and not filt and d and not re.search('[Zz]', d) \
                and not re.search('[a-y]', d.replace('e', '')) and 'dasharray' not in s:
            nums = re.findall(r'-?[\d.]+', d); w = float(eff.get('stroke-width', '1')); col = eff['stroke']
            op = A(s, 'opacity')
            p = re.sub(r'\sopacity="[^"]*"', '', s)
            p = re.sub(r'\sstroke-linecap="[^"]*"', '', p).replace('<path', '<path stroke-linecap="butt"', 1)
            disc = lambda x, y: f'<circle cx="{x}" cy="{y}" r="{w / 2:g}" fill="{col}" stroke="none"/>'
            g0 = f'<g opacity="{op}">' if op else '<g>'
            line = line[:len(line) - len(line.lstrip())] + g0 + p + disc(nums[0], nums[1]) + disc(nums[-2], nums[-1]) + '</g>'
            n += 1; touched.append(i)
    out.append(line)
open(f'{D}/svg/cd_{NAME}.svg', 'w').write('\n'.join(out))
print(n, 'strokes rewritten at lines', touched)
