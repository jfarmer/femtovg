#!/usr/bin/env python3
"""Attributes raw per-CPU absolute counter records (raw_dump.py TSVs of the
time samples and the context-switch kdebug samples) to one thread.
A record's 'thread' is the thread running when it was taken (a timer sample)
or the thread switching out (a MACH_SCHED kdebug record emitted by the
outgoing thread). For consecutive records on one CPU, prev -> cur:
  clean  : prev is a timer sample of the same thread (it ran from prev to cur
           without leaving the CPU, or a switch-out record would sit between);
  resumed: prev is the same thread's switch-out record (other threads may have
           run on that CPU in between; not counted);
Usage: raw_attr.py <thread-substr> <signposts.xml|-> <out.json> raw1.tsv [raw2.tsv ...]"""
import sys, json, bisect, collections
import xml.etree.ElementTree as ET
want, sp_path, out_path = sys.argv[1:4]
recs = []
for p in sys.argv[4:]:
    for line in open(p):
        k, t, cpu, ck, th, st, args, pmc = line.rstrip("\n").split("\t")
        recs.append((int(t), int(cpu), ck, k, th, [int(x) for x in pmc.split()]))
recs.sort(key=lambda r: (r[1], r[0]))
intervals = []
if sp_path != "-":
    root = ET.parse(sp_path).getroot()
    ids = {el.get("id"): el for el in root.iter() if el.get("id")}
    deref = lambda e: ids.get(e.get("ref"), e) if e.get("ref") else e
    for row in root.iter("row"):
        kids = [deref(k) for k in row]
        s = next((int(k.text) for k in kids if k.tag == "start-time"), None)
        d = next((int(k.text) for k in kids if k.tag == "duration"), None)
        m = [k for k in kids if k.tag == "os-log-metadata"]
        if s is not None and d is not None:
            intervals.append((s, s + d, m[0].get("fmt") if m else ""))
intervals.sort()
starts = [i[0] for i in intervals]
def interval_of(t):
    i = bisect.bisect_right(starts, t) - 1
    return intervals[i][2] if i >= 0 and intervals[i][0] <= t <= intervals[i][1] else None
tot = collections.defaultdict(lambda: None)
cnt = collections.Counter()
per = collections.defaultdict(lambda: None)
def add(d, key, v):
    d[key] = list(v) if d[key] is None else [a + b for a, b in zip(d[key], v)]
for a, b in zip(recs, recs[1:]):
    if a[1] != b[1] or want not in b[4] or a[4] != b[4]:
        continue
    delta = [y - x for x, y in zip(a[5], b[5])]
    if any(x < 0 for x in delta):
        continue
    kind = "clean" if a[3] == "T" else "resumed"
    key = f"{kind}|{b[2]}"
    add(tot, key, delta); cnt[key] += 1
    if kind == "clean":
        name = interval_of(b[0])
        if name:
            add(per, f"{name}|{b[2]}", delta)
json.dump({"totals": tot, "pairs": cnt, "per_interval": per}, open(out_path, "w"), indent=0)
for k in sorted(tot):
    print(k, cnt[k], [round(x / 1e6, 1) for x in tot[k][:2]], "M cyc/instr")
