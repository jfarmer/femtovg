#!/usr/bin/env python3
"""Streams an xctrace `counters-profile` export (manual CPU Counters mode,
time sampling) from stdin and sums the per-sample counter deltas per
(process, thread, core kind); for the soak thread also per Points of Interest
interval (signpost message = "<phase>/<file>") and, on the E-cores, per
function: the sample's leaf frame and its first frame in the app binary
("app frame": where femtovg/harness code called into the system).
Nothing big is written: the XML is parsed incrementally.

usage: xctrace export ... counters-profile | agg_counters.py <signposts.xml|-> <proc-substr> <thread-substr> <out.json>
The pmc-events column order is the table's pmc-events attribute (Cycles,
Instructions, then the configured events).

Coverage caveat (measured on the M4 Max): a sample's counters are the delta
since the previous record on that CPU for the running thread (its switch-in
or the previous timer tick), so the stretch from a thread's last tick to its
switch-out is never counted: on a soak that blocks on the GPU every frame the
samples hold ~45-60 % of the instructions thread_selfcounts reports for big
frames and ~20 % for sub-millisecond ones. Use the samples for ratios
(events per instruction) and thread_selfcounts for totals."""
import sys, json, bisect, collections, re
import xml.etree.ElementTree as ET

sp_path, want_proc, want_thread, out_path = sys.argv[1:5]

intervals = []
if sp_path != "-":
    try:
        root = ET.parse(sp_path).getroot()
    except ET.ParseError:
        root = None
    if root is not None:
        ids = {el.get("id"): el for el in root.iter() if el.get("id")}
        deref = lambda e: ids.get(e.get("ref"), e) if e.get("ref") else e
        for row in root.iter("row"):
            kids = [deref(k) for k in row]
            start = next((int(k.text) for k in kids if k.tag == "start-time"), None)
            dur = next((int(k.text) for k in kids if k.tag == "duration"), None)
            msgs = [k for k in kids if k.tag == "os-log-metadata"]
            if start is not None and dur is not None:
                intervals.append((start, start + dur, msgs[0].get("fmt") if msgs else ""))
intervals.sort()
# The soak marks each file once per pass, passes in order: number the
# occurrences so pass 0 (shader and pipeline compilation, first uploads) can be
# told apart. Names become "<phase>/<file>#<pass>".
seen = collections.Counter()
numbered = []
for s0, e0, name in intervals:
    numbered.append((s0, e0, f"{name}#{seen[name]}"))
    seen[name] += 1
intervals = numbered
starts = [i[0] for i in intervals]

def interval_of(t):
    i = bisect.bisect_right(starts, t) - 1
    return intervals[i][2] if i >= 0 and intervals[i][0] <= t <= intervals[i][1] else None

def short(name):
    name = re.sub(r"::h[0-9a-f]{16}$", "", name or "?")
    return name[:160]

ids = {}
binaries = {}
frames = {}
stacks = {}
totals = collections.defaultdict(lambda: None)
samples = collections.Counter()
# Per thread of the process, so the soak thread can be picked at the end even when a
# trace lost its thread names (seen on the A14: threads listed as "0x20352 (FlatC, pid: ...)").
mk = lambda: collections.defaultdict(lambda: None)
per_interval_t = collections.defaultdict(mk)
per_leaf_t = collections.defaultdict(mk)
per_app_t = collections.defaultdict(mk)
outside_t = collections.defaultdict(collections.Counter)

def add(d, key, vals):
    cur = d[key]
    d[key] = list(vals) if cur is None else [a + b for a, b in zip(cur, vals)]

for ev, el in ET.iterparse(sys.stdin.buffer, events=("end",)):
    tag = el.tag
    if tag == "binary":
        if el.get("id"):
            binaries[el.get("id")] = el.get("name")
        continue
    if tag == "frame":
        if el.get("id"):
            b = el.find("binary")
            bname = None
            if b is not None:
                bname = binaries.get(b.get("ref")) if b.get("ref") else b.get("name")
            frames[el.get("id")] = (el.get("name") or el.get("addr"), bname)
        continue
    if tag == "tagged-backtrace":
        if el.get("id"):
            fl = [frames.get(f.get("ref") or f.get("id"), ("?", None)) for f in el.findall("frame")]
            leaf = fl[0] if fl else ("?", None)
            app = next((n for n, b in fl if b and want_proc in b), None)
            stacks[el.get("id")] = (short(leaf[0]), leaf[1], short(app) if app else None)
        continue
    if tag == "row":
        t = proc = thread = core = pmc = None
        st = None
        for k in el:
            r = k.get("ref")
            if k.tag == "tagged-backtrace":
                st = stacks.get(r or k.get("id"))
                continue
            v = ids.get(r) if r else (k.get("fmt"), k.text)
            if v is None:
                continue
            if k.tag == "sample-time":
                t = int(v[1])
            elif k.tag == "thread":
                thread = v[0]
            elif k.tag == "process":
                proc = v[0]
            elif k.tag == "core":
                core = v[0]
            elif k.tag == "pmc-events":
                pmc = [int(x) for x in v[1].split()] if v[1] else None
        if pmc is not None and proc and want_proc in proc:
            kind = "E" if core and "E Core" in core else ("P" if core and "P Core" in core else "?")
            tname = (thread or "").split(" (0x")[0]
            key = f"{tname}|{kind}"
            add(totals, key, pmc)
            samples[key] += 1
            th = thread or "?"
            name = interval_of(t)
            if name is not None:
                add(per_interval_t[th], f"{name}|{kind}", pmc)
                phase = name.split("/")[0]
                if st is not None and kind == "E" and not name.endswith("#0") and "/r0#" not in name:
                    add(per_leaf_t[th], f"{phase}|{st[0]}|{st[1]}", pmc)
                    add(per_app_t[th], f"{phase}|{st[2]}", pmc)
            else:
                outside_t[th][kind] += 1
        el.clear()
        continue
    i = el.get("id")
    if i and tag in ("sample-time", "thread", "process", "core", "pmc-events"):
        ids[i] = (el.get("fmt"), el.text)

def top(d, n=60):
    by_phase = collections.defaultdict(list)
    for k, v in d.items():
        by_phase[k.split("|")[0]].append((k, v))
    keep = {}
    for ph, items in by_phase.items():
        items.sort(key=lambda kv: -kv[1][1])
        for k, v in items[:n]:
            keep[k] = v
        rest = [v for k, v in items[n:]]
        if rest:
            keep[f"{ph}|(other)"] = [sum(x) for x in zip(*rest)]
    return keep

named = [th for th in per_interval_t if want_thread in th]
if named:
    soak, fallback = named[0], False
else:
    # no thread carries the name: the thread with the most instructions inside the intervals
    soak = max(per_interval_t, key=lambda th: sum(v[1] for v in per_interval_t[th].values()), default=None)
    fallback = True
per_interval = per_interval_t.get(soak, {}) if soak else {}
per_leaf = per_leaf_t.get(soak, {}) if soak else {}
per_app = per_app_t.get(soak, {}) if soak else {}
outside = outside_t.get(soak, {}) if soak else {}
json.dump({"soak_thread": soak, "soak_thread_by_instructions": fallback, "totals": totals, "samples": samples, "per_interval": per_interval,
           "per_leaf": top(per_leaf), "per_app_frame": top(per_app),
           "soak_samples_outside_intervals": outside, "n_intervals": len(intervals)},
          open(out_path, "w"), indent=0)
print(f"{out_path}: {sum(samples.values())} samples of {want_proc}; soak thread {soak}{' (by instructions)' if fallback else ''}; {len(per_interval)} interval keys; "
      f"{len(per_leaf)} leaf keys; outside {dict(outside)}")
