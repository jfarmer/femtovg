#!/usr/bin/env python3
"""Write a CPU Counters .tracetemplate in manual mode with a chosen event list.

usage: make_tpl.py OUT.tracetemplate [--pmi EVENT:THRESHOLD] [--hf] [--lean] EVENT...

The base is Xcode's own 'CPU Counters' template. Its counter options are a JSON
blob inside the NSKeyedArchiver plist; manual mode is configurationType
{"manual": {}} and the events are allEventsAndFormulas, each an archived
XRCountersSetupEventOrFormula naming a kpep mnemonic (/usr/share/kpep/<cpu>.plist).
Without --pmi the counters are sampled on the instrument's timer.
"""
import base64, json, plistlib, sys

BASE = '/Applications/Xcode.app/Contents/Applications/Instruments.app/Contents/Resources/templates/CPU Counters.tracetemplate'


def event_archive(mnemonic):
    objs = [
        '$null',
        {'$class': plistlib.UID(4), '_formulaEvaluator': plistlib.UID(0), '_formulaText': plistlib.UID(0),
         '_explanation': plistlib.UID(3), '_mnemonic': plistlib.UID(2), '_beingEdited': False,
         '_displayName': plistlib.UID(2), '_aliasOrMnemonic': plistlib.UID(2)},
        mnemonic,
        mnemonic,
        {'$classname': 'XRCountersSetupEventOrFormula', '$classes': ['XRCountersSetupEventOrFormula', 'NSObject']},
    ]
    doc = {'$version': 100000, '$archiver': 'NSKeyedArchiver', '$top': {'root': plistlib.UID(1)}, '$objects': objs}
    return base64.b64encode(plistlib.dumps(doc, fmt=plistlib.FMT_BINARY)).decode()


def main():
    args = sys.argv[1:]
    out = args.pop(0)
    pmi = None
    hf = False
    lean = False
    events = []
    while args:
        a = args.pop(0)
        if a == '--pmi':
            pmi = args.pop(0)
        elif a == '--hf':
            hf = True
        elif a == '--lean':
            lean = True
        else:
            events.append(a)
    p = plistlib.load(open(BASE, 'rb'))
    objs = p['$objects']
    hits = 0
    for i, o in enumerate(objs):
        b = o if isinstance(o, bytes) else (o.get('NS.data') if isinstance(o, dict) else None)
        if not b or b[:1] != b'{':
            continue
        j = json.loads(b)
        if 'configurationType' not in j:
            continue
        j['configurationType'] = {'manual': {}}
        j['allEventsAndFormulas'] = [event_archive(e) for e in events]
        j['useHighFrequencyForManualMode'] = hf
        if pmi:
            name, threshold = pmi.split(':')
            j['sampleByTime'] = False
            j['pmiEventAliasOrMnemonic'] = name
            j['pmiThreshold'] = int(threshold)
        else:
            j['sampleByTime'] = True
        nb = json.dumps(j).encode()
        if isinstance(o, bytes):
            objs[i] = nb
        else:
            o['NS.data'] = nb
        hits += 1
    assert hits == 1, hits
    if lean:
        # Keep only the CPU Counters instrument and its sampler ($1..$4): drop
        # Thread Activity ($5/$6, every context switch of every thread) and
        # Points of Interest ($7/$8).
        top = p['$top']
        for k in ('$5', '$6', '$7', '$8'):
            top.pop(k, None)
        objs.append(2)
        top['$0'] = plistlib.UID(len(objs) - 1)
    plistlib.dump(p, open(out, 'wb'), fmt=plistlib.FMT_BINARY)
    print(f'{out}: manual, {len(events)} events, pmi={pmi}, hf={hf}, lean={lean}')


main()
