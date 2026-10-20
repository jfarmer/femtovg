import xml.etree.ElementTree as ET, sys
def rows(path, kind):
    ids = {}; out = []
    for ev, el in ET.iterparse(path, events=('end',)):
        if el.get('id') is not None: ids[el.get('id')] = el
        if el.tag != 'row': continue
        kids = [ids[c.get('ref')] if c.get('ref') else c for c in el]
        r = {'kind': kind}
        for c in kids:
            t = c.tag
            if t == 'sample-time': r['t'] = int(c.text)
            elif t == 'thread': r['th'] = c.get('fmt')
            elif t == 'core': r['core'] = c.get('fmt')
            elif t == 'thread-state': r['st'] = c.get('fmt')
            elif t == 'pmc-events': r['pmc'] = [int(x) for x in (c.text or '').split()]
            elif t == 'time-sample-kind': r['sk'] = c.get('fmt')
        mn = [c for c in kids if c.tag in ('kdebug-func',)]
        if mn: r['fn'] = mn[0].get('fmt')
        for c in kids:
            if c.tag == 'kdebug-arg': r.setdefault('args', []).append(c.get('fmt'))
        out.append(r)
    return out
