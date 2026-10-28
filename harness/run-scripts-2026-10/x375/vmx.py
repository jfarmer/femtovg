"""vmx.py VM_XML PROCESS_SUBSTRING - summarise an exported System Trace virtual-memory table for one process."""
import sys, re, collections
import xml.etree.ElementTree as ET
ids = {}
def val(el):
    """Resolve an element (or a ref to one) to (fmt, element)."""
    if el is None: return None
    ref = el.get('ref')
    if ref is not None: return ids[ref]
    if el.get('id') is not None: ids[el.get('id')] = el
    return el
rows = []
for ev, el in ET.iterparse(sys.argv[1], events=('end',)):
    if el.tag != 'row': continue
    kids = list(el)
    d = {}
    for k in kids:
        r = val(k)
        # register nested ids too
        for sub in k.iter():
            if sub.get('id') is not None: ids[sub.get('id')] = sub
        d[k.tag] = r
    rows.append(d)
want = sys.argv[2]
mine = []
for d in rows:
    th = d.get('thread'); 
    if th is None: continue
    name = th.get('fmt') or ''
    if want not in name: continue
    op = d['vm-op'].get('fmt'); t = int(d['start-time'].text); dur = int(d['duration'].text)
    addr = int(d['address'].text) if d.get('address') is not None and d['address'].text else 0
    bt = d.get('tagged-backtrace')
    frames = []
    if bt is not None:
        for fr in bt.iter('frame'):
            r = ids.get(fr.get('ref'), fr) if fr.get('ref') else fr
            frames.append(r.get('name'))
    mine.append((t, name.split(' (')[0] + ' ' + re.search(r'0x[0-9a-f]+', name).group(0), op, dur, addr, tuple(frames)))
print(len(rows), 'rows;', len(mine), 'for', want)
if not mine: sys.exit()
t0 = mine[0][0]; t1 = mine[-1][0]
print(f"span {(t1-t0)/1e6:.1f} ms")
by = collections.Counter(); dur = collections.Counter()
for t, th, op, du, addr, fr in mine:
    by[(th, op)] += 1; dur[(th, op)] += du
for k, n in by.most_common(20):
    print(f"  {n:6d} faults {dur[k]/1e6:8.2f} ms  {k}")
# the last 40 % of the run = steady frames
cut = t0 + (t1 - t0) * 0.6
late = [m for m in mine if m[0] >= cut]
print(f"late part: {len(late)} faults, {sum(m[3] for m in late)/1e6:.2f} ms in faults")
bt = collections.Counter(); btd = collections.Counter()
for t, th, op, du, addr, fr in late:
    key = (th.split(' 0x')[0], op, fr[:int(sys.argv[3]) if len(sys.argv) > 3 else 6])
    bt[key] += 1; btd[key] += du
for k, n in bt.most_common(12):
    print(f"  {n:6d} faults {btd[k]/1e6:7.2f} ms {k[0]} | {k[1]}")
    for f in k[2]: print(f"           {f}")
