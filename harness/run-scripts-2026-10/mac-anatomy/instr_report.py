import json, statistics as st, collections
rows=[json.loads(l) for l in open('instr.jsonl')]
by=collections.defaultdict(list)
for r in rows: by[(r['file'], r['variant'])].append(r)
probe={(r['file'],r['framing'],r['tol']):r for r in map(json.loads, open('probe.jsonl'))}
tol={'m7':'0.25','m7f':'0.0625','fb':'0.25','fc':'0.125'}
print('file | variant | instr M/frame (median, spread %) | cycles M/frame E-core (median, spread %) | IPC | d instr vs master | d cycles | points | d instr per extra point')
for f in ['tiger','puzzle-fox','mr-settodefault','svgenius-icon32','svgenius-icon5']:
    base=None
    for v in ['m7','m7f','fb','fc']:
        xs=by.get((f,v))
        if not xs: continue
        i=[x['instr'] for x in xs]; c=[x['cycles'] for x in xs]
        mi, mc = st.median(i), st.median(c)
        sp=lambda a: 100*(max(a)-min(a))/st.median(a)
        pts=probe[(f,'hd',tol[v])]['probe_points']/3
        if v=='m7': base=(mi,mc,pts)
        di=mi-base[0]; dc=mc-base[1]
        per = di/(pts-base[2]) if pts>base[2] else float('nan')
        print(f'{f} | {v} | {mi/1e6:.3f} ({sp(i):.1f} %, n={len(i)}) | {mc/1e6:.3f} ({sp(c):.1f} %) | {mi/mc:.2f} | {di/1e6:+.3f} M ({100*di/base[0]:+.1f} %) | {dc/1e6:+.3f} M ({100*dc/base[1]:+.1f} %) | {pts:.0f} | {per:.0f}')
