"""cmp_runs.py - the published timing run (master vs #375 at acf2d73, runs/pr/pass_time.jsonl) against today's
(master vs #375 with the pool fix, runs/pr/pass_time_x375.jsonl): per frame the PR's time relative to master."""
import json, collections, statistics, sys
def load(path, before, after):
    t = collections.defaultdict(list)
    for l in open(path):
        r = json.loads(l); t[(r['key'], r['framing'], r['build'])].append(r['frame_ms'])
    med = lambda k: statistics.median(t[k])
    frames = sorted(set((k, f) for k, f, b in t))
    return {(k, f): (med((k, f, before)), med((k, f, after))) for k, f in frames if t[(k, f, before)] and t[(k, f, after)]}
old = load('/Users/matt/src/femtovg-wt/runs/pr/pass_time.jsonl', 'master', 'cp')
new = load('/Users/matt/src/femtovg-wt/runs/pr/pass_time_x375.jsonl', 'm375', 'f375')
group = {f['key']: f['group'] for f in json.load(open('/Users/matt/src/femtovg-wt/runs/pr/files.json'))}
port = sorted(k for k in new if group[k[0]] == 'buseybench')
print(f"portraits: {len(port)} frames")
for name, d in (('published (head acf2d73)', old), ('today (pool fix)', new)):
    tb, ta = sum(d[k][0] for k in port), sum(d[k][1] for k in port)
    slower = [k for k in port if d[k][1] > d[k][0] * 1.02]
    ratios = sorted(d[k][1] / d[k][0] for k in port)
    print(f"  {name}: {tb:.0f} -> {ta:.0f} ms ({100*(ta-tb)/tb:+.1f} %); slower than master by more than 2 %: {len(slower)}; "
          f"best {100*(ratios[0]-1):+.0f} %, median {100*(ratios[len(ratios)//2]-1):+.1f} %, worst {100*(ratios[-1]-1):+.1f} %")
    for k in slower: print('     slower:', k[0].split('__')[-1], k[1], f"{d[k][0]:.1f} -> {d[k][1]:.1f}")
print("portrait frames whose ratio to master moved by more than 4 points between the runs:")
for k in port:
    ro, rn = old[k][1] / old[k][0], new[k][1] / new[k][0]
    if abs(rn - ro) > 0.04:
        print(f"   {k[0].split('__')[-1]:28s} {k[1]}: published {old[k][0]:6.1f} -> {old[k][1]:6.1f} ({100*(ro-1):+.1f} %)   today {new[k][0]:6.1f} -> {new[k][1]:6.1f} ({100*(rn-1):+.1f} %)")
# files other than portraits that are slower in both runs
both = [k for k in new if group[k[0]] != 'buseybench' and k in old and new[k][1] > new[k][0] * 1.05 and old[k][1] > old[k][0] * 1.05]
print("other frames more than 5 % slower than master in both runs:", [(k[0].split('__')[-1], k[1], f"{new[k][0]:.2f}->{new[k][1]:.2f}") for k in both])
