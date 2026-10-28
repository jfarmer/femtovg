#!/usr/bin/env python3
"""Copy every draft's assets into the demo-assets worktree and check that each demo-assets URL in each body
resolves to a file (or directory) there. Prints missing references; copies nothing over an existing different file
without saying so."""
import json, os, re, shutil, sys, filecmp
from urllib.parse import unquote
D = os.path.dirname(os.path.abspath(__file__))
DA = os.path.expanduser('~/src/femtovg-wt/da')
res = {r['id']: r for r in json.load(open(f'{D}/draft_results.json'))}
extra = {'C1-comment-151': [
    {'src': f'{D}/C1-comment-151/assets/pen-stencil-off.png', 'dest': 'zoom-ladder/comment-151/pen-stencil-off.png'}] + [
    {'src': f'{D}/C1-comment-151/harness/nostencil/{f}', 'dest': f'harness/zoom-ladder/comment-151/nostencil/{f}'}
    for f in sorted(os.listdir(f'{D}/C1-comment-151/harness/nostencil'))]}
dry = '--dry' in sys.argv
copied, missing, clash = 0, [], []
for id_, r in res.items():
    assets = (r['draft']['assets'] if r['draft'] else []) + extra.get(id_, [])
    for a in assets:
        src, dest = os.path.expanduser(a['src']), a['dest']
        if not os.path.exists(src):
            missing.append((id_, 'asset src', src)); continue
        out = os.path.join(DA, dest)
        if os.path.exists(out) and not filecmp.cmp(src, out, shallow=False):
            clash.append((id_, dest))
        if not dry:
            os.makedirs(os.path.dirname(out), exist_ok=True)
            shutil.copy2(src, out)
        copied += 1
    body = open(f'{D}/{id_}/body.md').read()
    for m in re.finditer(r'https://raw\.githubusercontent\.com/rebeckerspecialties/femtovg/demo-assets/([^)\s"]+)', body):
        if not os.path.exists(os.path.join(DA, unquote(m.group(1)))): missing.append((id_, 'raw', m.group(1)))
    for m in re.finditer(r'https://github\.com/rebeckerspecialties/femtovg/(?:blob|tree)/demo-assets/([^)\s"#]+)', body):
        if not os.path.exists(os.path.join(DA, unquote(m.group(1)))): missing.append((id_, 'blob/tree', m.group(1)))
print(f'copied {copied} files' + (' (dry run)' if dry else ''))
for c in clash: print('OVERWROTE a different file:', c)
for m in missing: print('MISSING', m)
