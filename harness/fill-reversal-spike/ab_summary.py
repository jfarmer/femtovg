#!/usr/bin/env python3
"""Summary of corpus_ab.py: per variant, the frames that move, and of those how many come closer to Chromium (fewer
pixels more than 20/255 off it), go further, or keep the same count; the same against all three browsers where
Firefox and WebKit references exist, and against the 8x area reference. Lists the moved frames by count change.

  ab_summary.py AB.jsonl [VARIANT...] [--list]"""
import json, sys
from collections import Counter, defaultdict

args = sys.argv[1:]
path = args.pop(0)
listing = '--list' in args
want = [a for a in args if not a.startswith('--')]
rows = [json.loads(line) for line in open(path)]
by = defaultdict(list)
for r in rows:
    by[r['variant']].append(r)


def verdict(r, ref):
    b, a = r['before'].get(ref), r['after'].get(ref)
    if b is None or a is None:
        return None
    return 'toward' if a < b else 'away' if a > b else 'same'


summary = {}
for v, rs in by.items():
    if want and v not in want:
        continue
    total = len(rs)
    errors = sum(1 for r in rs if r.get('error'))
    moved = [r for r in rs if r.get('moved')]
    unrepro = sum(1 for r in moved if not r.get('master_reproduced'))
    s = {'frames': total, 'errors': errors, 'moved': len(moved), 'master_not_reproduced': unrepro}
    for ref in ('chr', 'off3', 'id'):
        c = Counter(verdict(r, ref) for r in moved)
        s[ref] = {k: c[k] for k in ('toward', 'away', 'same', None) if c[k]}
        s[ref + '_px'] = sum(r['after'].get(ref, 0) - r['before'].get(ref, 0) for r in moved
                             if ref in r['after'] and ref in r['before'])
    sets = defaultdict(Counter)
    for r in moved:
        sets[r['set']][verdict(r, 'chr')] += 1
    s['by_set'] = {k: dict(c) for k, c in sets.items()}
    summary[v] = s
    print(f"{v}: {total} frames, {errors} errors, {len(moved)} moved (master reproduced its stored hash in all but "
          f"{unrepro}). vs Chromium px>20: {s['chr']} net {s['chr_px']:+d} px; off all three: {s['off3']} net "
          f"{s['off3_px']:+d}; vs area: {s['id']} net {s['id_px']:+d}; by set {s['by_set']}")
    if listing:
        for r in sorted(moved, key=lambda r: r['after'].get('chr', 0) - r['before'].get('chr', 0)):
            b, a = r['before'], r['after']
            print(f"   {r['key']} {r['framing']}: chr {b.get('chr')}->{a.get('chr')} off3 {b.get('off3')}->{a.get('off3')} "
                  f"id {b.get('id')}->{a.get('id')}")
json.dump(summary, open(path.replace('.jsonl', '_summary.json'), 'w'), indent=1)
