"""vmaddr.py VM_XML PROCESS - the faults of the process's non-main threads: when, which addresses, how often each page."""
import sys, re, collections
import xml.etree.ElementTree as ET
ids = {}
rows = []
for ev, el in ET.iterparse(sys.argv[1], events=('end',)):
    if el.tag != 'row': continue
    d = {}
    for k in list(el):
        for sub in k.iter():
            if sub.get('id') is not None: ids[sub.get('id')] = sub
        d[k.tag] = ids[k.get('ref')] if k.get('ref') is not None else k
    rows.append(d)
out = []
for d in rows:
    th = d['thread'].get('fmt') or ''
    if sys.argv[2] not in th: continue
    frames = [(ids.get(f.get('ref'), f) if f.get('ref') else f).get('name') for f in d['tagged-backtrace'].iter('frame')] if d.get('tagged-backtrace') is not None else []
    out.append((int(d['start-time'].text), 'main' if th.startswith('Main') else re.search(r'0x[0-9a-f]+', th).group(0), d['vm-op'].get('fmt'), int(d['address'].text or 0), int(d['duration'].text), frames))
t0 = out[0][0]
bg = [o for o in out if o[1] != 'main' and o[2] == 'Page Cache Hit']
print(len(bg), 'background-thread page-cache-hit faults')
# time histogram in 5 ms bins over the run
bins = collections.Counter((o[0] - t0) // 10_000_000 for o in bg)
print('faults per 10 ms bin:', ' '.join(f"{b}:{n}" for b, n in sorted(bins.items())))
pages = collections.Counter(o[3] >> 14 for o in bg)
print(len(pages), 'distinct pages; times each page faulted:', sorted(collections.Counter(pages.values()).items()))
# contiguous address runs
ps = sorted(pages)
runs = []; start = prev = ps[0]
for p in ps[1:]:
    if p != prev + 1:
        runs.append((start, prev)); start = p
    prev = p
runs.append((start, prev))
print(len(runs), 'address runs; largest:')
for a, b in sorted(runs, key=lambda r: r[0] - r[1])[:25]:
    print(f"   {a << 14:#x}-{(b + 1) << 14:#x}  {b - a + 1:5d} pages  faults {sum(pages[p] for p in range(a, b + 1))}")
with_bt = collections.Counter(tuple(o[5][:6]) for o in bg)
for k, n in with_bt.most_common(4): print(n, k)
