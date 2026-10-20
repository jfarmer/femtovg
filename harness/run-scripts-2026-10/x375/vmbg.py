"""vmbg.py VM_XML PROCESS - faults a process takes off its main thread, by kind and by the call stack that led to
them, for the last third of the run (steady frames)."""
import sys, re, collections
import xml.etree.ElementTree as ET
ids = {}; out = []
for ev, el in ET.iterparse(sys.argv[1], events=('end',)):
    if el.tag != 'row': continue
    d = {}
    for k in list(el):
        for sub in k.iter():
            if sub.get('id') is not None: ids[sub.get('id')] = sub
        d[k.tag] = ids[k.get('ref')] if k.get('ref') is not None else k
    th = d['thread'].get('fmt') or ''
    if sys.argv[2] not in th: continue
    frames = [(ids.get(f.get('ref'), f) if f.get('ref') else f).get('name') for f in d['tagged-backtrace'].iter('frame')] if d.get('tagged-backtrace') is not None else []
    out.append((int(d['start-time'].text), th.startswith('Main'), d['vm-op'].get('fmt'), int(d['duration'].text), frames))
t0, t1 = out[0][0], out[-1][0]
late = [o for o in out if o[0] >= t1 - (t1 - t0) / 3]
span = (late[-1][0] - late[0][0]) / 1e6
print(f"{len(out)} faults in the run; last third: {len(late)} faults over {span:.0f} ms")
by = collections.Counter(); dur = collections.Counter()
for t, main, op, du, fr in late:
    stack = next((f for f in fr if f and ('IOGPU' in f or 'AGX' in f or 'wgpu' in f or 'femtovg' in f)), fr[0] if fr else '(no user stack: in the kernel)')
    k = ('main thread' if main else 'other thread', op, stack[:90]); by[k] += 1; dur[k] += du
for k, n in by.most_common(8):
    print(f"  {n:6d} faults  {dur[k]/1e6:6.2f} ms in the fault handler  {k[0]} | {k[1]} | {k[2]}")
