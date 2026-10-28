"""featcheck.py name [fr...]: for every filter / mask / clip-path / pattern the file uses, the union bbox of the elements
that reference it (filters grown by 3 sigma), and inside it: femtovg px > 20 off all three browsers (where the browsers
agree), femtovg vs each browser px > 8, and the browsers' own pairwise px > 8 (their spread)."""
import sys, re, numpy as np
from PIL import Image
S = '/Users/matt/src/femtovg-wt/runs/busey/triage/new-five-r2'
sys.path.insert(0, f'{S}/scripts')
from locate import elements, parse, S as FS
L = lambda p: np.asarray(Image.open(p).convert('RGB'), dtype=np.int16)
name = sys.argv[1]; frs = sys.argv[2:] or ['z2', 'hd']
svgp = f'/Users/matt/src/femtovg-wt/da/corpus/buseybench/{name}.svg'
txt = open(svgp).read()
els = elements(svgp)
# filter id -> max stdDeviation and primitive list
filt = {}
for m in re.finditer(r'<filter\b([^>]*)>(.*?)</filter>', txt, re.S):
    fid = re.search(r'id="([^"]+)"', m.group(1)).group(1)
    sd = [float(x) for s in re.findall(r'stdDeviation="([^"]+)"', m.group(2)) for x in s.split()]
    off = [abs(float(x)) for x in re.findall(r'd[xy]="([^"]+)"', m.group(2))]
    prims = re.findall(r'<(fe[A-Za-z]+)', m.group(2))
    filt[fid] = (max(sd + [0]) * 3 + max(off + [0]), prims)
feat = {}
for e in els:
    if e['kind'] != 'draw': continue
    refs = []
    for k in ('filter', 'mask', 'clip-path', 'fill', 'stroke'):
        v = e['attrs'].get(k)
        if v and 'url(#' in v: refs.append((k, v[5:-1]))
    for (tag, line, a) in e['ctx']:
        for k in ('filter', 'mask', 'clip-path'):
            v = a.get(k)
            if v and 'url(#' in v: refs.append((k, v[5:-1]))
    for k, fid in refs:
        if k in ('fill', 'stroke') and not re.search(rf'<pattern[^>]*id="{fid}"', txt): continue
        kind = 'pattern' if k in ('fill', 'stroke') else k
        grow = filt.get(fid, (0, []))[0] if k == 'filter' else 0
        bb = np.vstack([P for P in e['polys'] if len(P)])
        lo, hi = bb.min(0) - grow - e['sw'], bb.max(0) + grow + e['sw']
        f = feat.setdefault((kind, fid), [lo, hi, set()])
        f[0] = np.minimum(f[0], lo); f[1] = np.maximum(f[1], hi); f[2].add(e['line'])
R = '/Users/matt/src/femtovg-wt/runs/busey/refs'
for fr in frs:
    k = 'corpus__buseybench__' + name
    o = L(f'{S}/png/mst4_{k}_{fr}.png'); refs = {x: L(f'{R}/{x}_{k}_{fr}.png') for x in ('chr', 'ff', 'wk')}
    d = lambda a, b, t: np.abs(a - b).max(2) > t
    off3 = d(o, refs['chr'], 20) & d(o, refs['ff'], 20) & d(o, refs['wk'], 20)
    sp20 = d(refs['chr'], refs['ff'], 20) | d(refs['chr'], refs['wk'], 20) | d(refs['ff'], refs['wk'], 20)
    ox, oy, s = FS[fr]; H, W = off3.shape
    print(f'== {name} {fr}')
    for (kind, fid), (lo, hi, lines) in sorted(feat.items()):
        x0, y0 = max(int(ox + lo[0] * s), 0), max(int(oy + lo[1] * s), 0)
        x1, y1 = min(int(np.ceil(ox + hi[0] * s)), W), min(int(np.ceil(oy + hi[1] * s)), H)
        if x1 <= x0 or y1 <= y0:
            print(f'  {kind:9s} {fid:16s} off-frame'); continue
        sl = (slice(y0, y1), slice(x0, x1)); n = (y1 - y0) * (x1 - x0)
        fv = {b: 100 * d(o[sl], refs[b][sl], 8).mean() for b in refs}
        br = {f'{a}-{b}': 100 * d(refs[a][sl], refs[b][sl], 8).mean() for a, b in (('chr', 'ff'), ('chr', 'wk'), ('ff', 'wk'))}
        prim = '+'.join(dict.fromkeys(filt[fid][1])) if kind == 'filter' else ''
        print(f'  {kind:9s} {fid:16s} {prim:42s} box {n:7d}px  off3 {int(off3[sl].sum()):3d} (agreed {int((off3 & ~sp20)[sl].sum()):3d})  fv>8: ' +
              ' '.join(f'{b} {v:5.2f}%' for b, v in fv.items()) + '  | browsers>8: ' + ' '.join(f'{b} {v:5.2f}%' for b, v in br.items()) + f'  L{sorted(lines)[:3]}')
