#!/usr/bin/env python3
"""Parse an xctrace `counters-profile` export into per-sample records.

usage: cp_parse.py EXPORT.xml PROCESS_SUBSTRING [--frames N] [--stacks]

Prints, for the threads of the matching process: per core type, the summed
counters, and (with --stacks) the counters attributed to leaf functions and to
inclusive femtovg frames. Each sample's pmc-events are the counts since that
thread's previous sample, so sums over samples are totals.
"""
import collections, sys
import xml.etree.ElementTree as ET


def load(path, want):
    events = None
    ids = {}
    recs = []
    for ev, el in ET.iterparse(path, events=('end',)):
        if el.tag == 'schema' and events is None:
            pass
        if el.get('id') is not None:
            ids[el.get('id')] = el
        if el.tag != 'row':
            continue
        kids = []
        for c in el:
            if c.get('ref') is not None:
                c = ids[c.get('ref')]
            kids.append(c)
        rec = {}
        for c in kids:
            if c.tag == 'sample-time':
                rec['t'] = int(c.text)
            elif c.tag == 'thread':
                rec['thread'] = c.get('fmt')
            elif c.tag == 'process':
                rec['proc'] = c.get('fmt')
            elif c.tag == 'core':
                rec['core'] = c.get('fmt')
            elif c.tag == 'thread-state':
                rec['state'] = c.get('fmt')
            elif c.tag == 'tagged-backtrace' or c.tag == 'backtrace':
                frames = []
                for f in c.iter('frame'):
                    if f.get('ref') is not None:
                        f = ids[f.get('ref')]
                    frames.append(f.get('name'))
                rec['stack'] = frames
            elif c.tag == 'pmc-events':
                rec['pmc'] = [int(x) for x in (c.text or '').split()]
        if want in rec.get('proc', '') and 'pmc' in rec:
            recs.append(rec)
    return recs


def short(name):
    if name is None:
        return '?'
    import re
    m = re.sub(r'::h[0-9a-f]{16}$', '', name)
    return m


def main():
    args = sys.argv[1:]
    path, want = args[0], args[1]
    stacks = '--stacks' in args
    recs = load(path, want)
    if not recs:
        sys.exit('no samples')
    n = len(recs[0]['pmc'])
    by_core = collections.defaultdict(lambda: [0] * n)
    cnt = collections.Counter()
    for r in recs:
        ct = 'E' if 'E Core' in (r.get('core') or '') else ('P' if 'P Core' in (r.get('core') or '') else '?')
        v = by_core[ct]
        for i, x in enumerate(r['pmc']):
            v[i] += x
        cnt[ct] += 1
    for ct, v in by_core.items():
        print(ct, cnt[ct], 'samples', ' '.join(str(x) for x in v))
    if stacks:
        leaf = collections.defaultdict(lambda: [0] * n)
        incl = collections.defaultdict(lambda: [0] * n)
        for r in recs:
            st = r.get('stack') or ['?']
            l = leaf[short(st[0])]
            for i, x in enumerate(r['pmc']):
                l[i] += x
            seen = set()
            for f in st:
                s = short(f)
                if s in seen:
                    continue
                seen.add(s)
                v = incl[s]
                for i, x in enumerate(r['pmc']):
                    v[i] += x
        tot = [sum(r['pmc'][i] for r in recs) for i in range(n)]
        print('== leaf, by counter 1 (instructions)')
        for k, v in sorted(leaf.items(), key=lambda kv: -kv[1][1])[:60]:
            print(f'{v[1]/tot[1]*100:6.2f}% ' + ' '.join(str(x) for x in v) + ' ' + k)
        print('== inclusive')
        for k, v in sorted(incl.items(), key=lambda kv: -kv[1][1])[:80]:
            print(f'{v[1]/tot[1]*100:6.2f}% ' + ' '.join(str(x) for x in v) + ' ' + k)


main()
