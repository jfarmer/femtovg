import json, sys
for fix in sys.argv[1:]:
    rows=[json.loads(l) for l in open(f'reg/fix{fix}.jsonl')]
    moved=[(r['key'],s) for r in rows for s in r['steps'] if s.get('moved')]
    print(f"== fix{fix}: files {len(rows)} rc!=0 {sum(r['rc']!=0 for r in rows)} missing {sum(1 for r in rows for s in r['steps'] if s.get('missing'))} frames moved {len(moved)} in {len({k for k,_ in moved})} files")
    c=f=sm=0
    for k,s in moved:
        bs=[b for b in ['chr','ff','wk'] if b in s]
        before=min(s[b][0] for b in bs); after=min(s[b][1] for b in bs)
        tag='closer' if after<before else 'further' if after>before else 'same'
        c+=after<before; f+=after>before; sm+=after==before
        flag=' PASS->FAIL' if before<=24<after else ' FAIL->PASS' if after<=24<before else ''
        print(f"  {tag:7s} {k[:84]:84s} z{s['zoom']:<5} moved={s['moved']:4d} max={s['max']:3d} best {before}->{after}{flag}  "+" ".join(f"{b}:{s[b][0]}->{s[b][1]}" for b in bs))
    print(f"  closer {c} further {f} same {sm}")
