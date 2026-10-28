import re
SRC = '/Users/matt/src/femtovg-wt/da/corpus/buseybench/gpt-6-1-sol.svg'
D = '/Users/matt/src/femtovg-wt/runs/busey/triage/new-five-r2-verify'
ls = open(SRC).read().split('\n')
def ends(d):
    out = []
    for sp in re.findall(r'[Mm][^Mm]*', d):
        toks = re.findall(r'[A-Za-z]|-?(?:\d+\.?\d*|\.\d+)', sp); cmd = None; cur = None; start = None; nums = []
        i = 0
        while i < len(toks):
            t = toks[i]
            if t.isalpha(): cmd = t; i += 1; continue
            if cmd in 'Mm': cur = [float(toks[i]), float(toks[i + 1])]; start = list(cur); i += 2; cmd = 'L' if cmd == 'M' else 'l'
            elif cmd == 'L': cur = [float(toks[i]), float(toks[i + 1])]; i += 2
            elif cmd == 'l': cur = [cur[0] + float(toks[i]), cur[1] + float(toks[i + 1])]; i += 2
            elif cmd == 'C': cur = [float(toks[i + 4]), float(toks[i + 5])]; i += 6
            elif cmd == 'c': cur = [cur[0] + float(toks[i + 4]), cur[1] + float(toks[i + 5])]; i += 6
            else: raise ValueError(cmd)
        out.append((start, cur))
    return out
for ln, w, col in ((361, 1.35, '#f5ecd1'), (362, 1.35, '#f5ecd1'), (651, 0.72, '#7c624b')):
    s = ls[ln - 1]; d = re.search(r' d="([^"]+)"', s).group(1)
    discs = ''.join(f'<circle cx="{x:g}" cy="{y:g}" r="{w / 2:g}" fill="{col}" stroke="none"/>' for a, b in ends(d) for (x, y) in (a, b))
    ls[ln - 1] = s.replace('<path', '<path stroke-linecap="butt"', 1).replace('/>', '/>' + discs, 1)
open(f'{D}/svg/cd_sol_targeted.svg', 'w').write('\n'.join(ls)); print('ok')
