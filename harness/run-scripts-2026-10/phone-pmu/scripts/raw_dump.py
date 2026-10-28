#!/usr/bin/env python3
"""Streams an xctrace export of kdebug-counters-with-time-sample or
kdebug-counters-with-kdebug-sample (raw per-CPU absolute counter values) from
stdin and writes compact TSV: kind, time_ns, cpu, core_kind, thread, state, counters...
usage: xctrace export ... | raw_dump.py <kind-letter> > out.tsv"""
import sys
import xml.etree.ElementTree as ET
kind = sys.argv[1]
ids = {}
out = sys.stdout
for ev, el in ET.iterparse(sys.stdin.buffer, events=("end",)):
    tag = el.tag
    if tag == "row":
        t = cpu = ck = thread = state = pmc = None
        args = []
        for k in el:
            r = k.get("ref")
            v = ids.get(r) if r else (k.get("fmt"), k.text)
            if v is None:
                continue
            if k.tag in ("sample-time", "event-time"):
                t = v[1]
            elif k.tag == "thread":
                thread = v[0]
            elif k.tag == "core":
                cpu = v[1]; ck = "E" if "E Core" in (v[0] or "") else ("P" if "P Core" in (v[0] or "") else "?")
            elif k.tag == "thread-state":
                state = v[0]
            elif k.tag == "kdebug-arg":
                args.append(v[1])
            elif k.tag == "pmc-events":
                pmc = v[1]
        if pmc and cpu is not None:
            th = (thread or "").replace("\t", " ")
            out.write(f"{kind}\t{t}\t{cpu}\t{ck}\t{th}\t{state}\t{','.join(args)}\t{pmc}\n")
        el.clear()
        continue
    i = el.get("id")
    if i and tag in ("sample-time", "event-time", "thread", "core", "thread-state", "kdebug-arg", "pmc-events"):
        ids[i] = (el.get("fmt"), el.text)
