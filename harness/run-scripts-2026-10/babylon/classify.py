#!/usr/bin/env python3
"""Which visual tests draw vector graphics with a 2D canvas that becomes a texture: a DynamicTexture's context, a
GUI AdvancedDynamicTexture (which lays out and draws its controls on one), or a canvas of their own."""
import json, os, re, sys
here = os.path.dirname(os.path.abspath(__file__))
def code_of(pid):
    name, *ver = pid.strip('#').split('#')
    p = f'{here}/snippets/{name}_{ver[0] if ver else "0"}.json'
    if not os.path.exists(p):
        return None
    d = json.load(open(p))
    payload = json.loads(d['jsonPayload'])
    code = payload.get('code', '')
    if code.startswith('{"v":'):
        files = json.loads(code).get('files', {})
        code = '\n'.join(files.values())
    return code
DRAW = re.compile(r'\b(fillRect|strokeRect|arc|arcTo|bezierCurveTo|quadraticCurveTo|lineTo|fillText|strokeText|drawImage|createLinearGradient|createRadialGradient|roundRect|ellipse|clip)\s*\(')
rows = []
for src, path in [('native', '/Users/matt/src/BabylonNative/Apps/Playground/Scripts/config.json'),
                  ('babylonjs', '/Users/matt/src/Babylon.js/packages/tools/tests/test/visualization/config.json')]:
    for t in json.load(open(path, encoding='utf-8-sig')).get('tests', []):
        pid = t.get('playgroundId')
        if not pid:
            continue
        code = code_of(pid)
        if code is None:
            rows.append((src, t, pid, None)); continue
        kinds = []
        if re.search(r'AdvancedDynamicTexture', code): kinds.append('gui')
        if re.search(r'DynamicTexture\b', code) and re.search(r'getContext\s*\(', code): kinds.append('dynamic')
        if re.search(r'createElement\s*\(\s*["\']canvas', code) or re.search(r'OffscreenCanvas', code): kinds.append('canvas')
        draws = sorted(set(DRAW.findall(code)))
        rows.append((src, t, pid, (kinds, draws)))
json.dump([{'source': s, 'title': t.get('title'), 'playgroundId': pid, 'referenceImage': t.get('referenceImage'),
            'excluded': bool(t.get('excludeFromAutomaticTesting')), 'kinds': k[0] if k else None, 'draws': k[1] if k else None}
           for s, t, pid, k in rows], open(f'{here}/classified.json', 'w'), indent=1)
use = [r for r in rows if r[3] and r[3][0]]
print(len(rows), 'tests;', sum(1 for r in rows if r[3] is None), 'without a snippet yet;', len(use), 'use a 2D canvas')
from collections import Counter
print(Counter((r[0], '+'.join(r[3][0])) for r in use).most_common())
