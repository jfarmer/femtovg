#!/usr/bin/env python3
"""pair.py SHORT.jsonl [LONG.jsonl] : the checker's own pairing of pass_time.py rows (mbase, poc), written without
reading analyze_q3.py's output. The i-th row of each build for a (file, framing) is repeat i.

Per frame: both medians, the paired difference poc - mbase (median, min..max), whether it has one sign in every
repeat, and which build ran first in each repeat (pass_time.py alternates). The frames whose route does not change
(changed_frames.json) are the noise floor: their paired medians should scatter about zero.

With LONG (a run of more frames), the frames after SHORT's are taken by difference inside each repeat:
(F_long * t_long[i] - F_short * t_short[i]) / (F_long - F_short), i.e. repeat i of the long run against repeat i of
the short run, and also against the short run's median as analyze_q3.py does."""
import collections, json, os, statistics, sys

BEFORE, AFTER = os.environ['POC_BEFORE'], os.environ['POC_AFTER']
changed = {(r['key'], r['framing']) for r in json.load(open(os.environ['POC_CHANGED']))}
med = statistics.median


def load(path):
    t, first, frames = collections.defaultdict(list), collections.defaultdict(list), None
    seen = collections.Counter()
    for l in open(path):
        r = json.loads(l)
        k = (r['key'], r['framing'])
        t[k + (r['build'],)].append((r['frame_ms'], r['encode_ms']))
        rep = seen[k + (r['build'],)]
        seen[k + (r['build'],)] += 1
        if len(first[k]) == rep:
            first[k].append(r['build'])
        frames = int(r['frames'])
    return t, first, frames


short, first, F = load(sys.argv[1])
long_ = load(sys.argv[2]) if len(sys.argv) > 2 else None
name = os.path.basename(sys.argv[1])[:-6]
out = []


def summarize(m, p):
    d = [b - a for a, b in zip(m, p)]
    return {'mbase': med(m), 'poc': med(p), 'diff': med(d), 'diff_min': min(d), 'diff_max': max(d),
            'pct': 100 * med(d) / med(m), 'one_sign': all(x > 0 for x in d) or all(x < 0 for x in d), 'n': len(d),
            'mbase_spread_pct': 100 * (max(m) - min(m)) / min(m), 'poc_spread_pct': 100 * (max(p) - min(p)) / min(p)}


def show(title, col, rows):
    print(f'\n{title}')
    for changed_frame in (True, False):
        sel = [r for r in rows if r['changed'] == changed_frame]
        print(f"  {'route changes' if changed_frame else 'route does not change (noise floor)'}: {len(sel)} frames")
        for r in sel:
            v = r[col]
            print(f"    {r['key'].split('__')[-1]:24s} {r['framing']:3s} {v['mbase']:7.3f} -> {v['poc']:7.3f}  paired {v['diff']:+.3f} "
                  f"({v['diff_min']:+.3f}..{v['diff_max']:+.3f}) {v['pct']:+6.1f} %  {'one sign' if v['one_sign'] else 'mixed   '} "
                  f"spread mbase {v['mbase_spread_pct']:.0f} % poc {v['poc_spread_pct']:.0f} %")
        if not changed_frame and sel:
            pcts = sorted(r[col]['pct'] for r in sel)
            print(f"    noise floor: paired medians {pcts[0]:+.1f} % .. {pcts[-1]:+.1f} %, median of their sizes "
                  f"{med(abs(x) for x in pcts):.1f} %, {sum(r[col]['one_sign'] for r in sel)} of {len(sel)} with one sign")


rows = []
for key, framing in sorted({(k, f) for k, f, _ in short}):
    m, p = short[(key, framing, BEFORE)], short[(key, framing, AFTER)]
    row = {'key': key, 'framing': framing, 'changed': (key, framing) in changed, 'frames': F,
           'first_in_repeat': first[(key, framing)],
           'frame_ms': summarize([v[0] for v in m], [v[0] for v in p]),
           'encode_ms': summarize([v[1] for v in m], [v[1] for v in p])}
    if long_:
        lt, _, FL = long_
        lm, lp = lt[(key, framing, BEFORE)], lt[(key, framing, AFTER)]
        n = min(len(m), len(p), len(lm), len(lp))
        later = lambda long_rows, short_rows, i: (FL * long_rows[i][0] - F * short_rows[i][0]) / (FL - F)
        row['later_same_repeat'] = summarize([later(lm, m, i) for i in range(n)], [later(lp, p, i) for i in range(n)])
        mm, pm = med(v[0] for v in m), med(v[0] for v in p)
        row['later_short_median'] = summarize([(FL * v[0] - F * mm) / (FL - F) for v in lm],
                                              [(FL * v[0] - F * pm) / (FL - F) for v in lp])
        row['later_frames'] = f'{F + 1}..{FL}'
    rows.append(row)
show(f'{name}: frame_ms, mean of {F} frames with the first', 'frame_ms', rows)
show(f'{name}: encode_ms', 'encode_ms', rows)
if long_:
    show(f"{name}: frames {rows[0]['later_frames']} by difference, repeat i against repeat i", 'later_same_repeat', rows)
    show(f"{name}: frames {rows[0]['later_frames']} by difference, against the short run's median (as analyze_q3.py)", 'later_short_median', rows)

# Does the build that runs first in a pair come out slower or faster? On frames whose route does not change, the
# difference second - first, whichever build that is.
order = []
for r in rows:
    if r['changed']:
        continue
    m, p = short[(r['key'], r['framing'], 'mbase')], short[(r['key'], r['framing'], 'poc')]
    for i, b in enumerate(r['first_in_repeat'][:min(len(m), len(p))]):
        a, c = (m[i][0], p[i][0]) if b == BEFORE else (p[i][0], m[i][0])
        order.append(100 * (c - a) / a)
if order:
    print(f'\norder within a pair, unchanged frames: second - first, median {med(order):+.1f} % of the first over {len(order)} pairs '
          f'({sum(x > 0 for x in order)} positive)')
json.dump(rows, open(f'{os.environ["CORPUS_RUN_OUT"]}/paired_{name}.json', 'w'), indent=1)
