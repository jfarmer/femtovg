"""tl.py TRACE [frame ...] - per-frame GPU timeline statistics from a PASS_TRACE file."""
import sys, re, collections, statistics

def frames(path):
    out, cur = [], None
    for line in open(path):
        p = line.split()
        if p[0] == 'F':
            cur = {'n': int(p[1]), 'events': [], 'passes': [], 'slices': [], 'faults': next((int(x.split('=')[1]) for x in p if x.startswith('faults=')), None)}
            out.append(cur)
        elif p[0] == 'E':
            cur['events'].append(p[1:])
        elif p[0] == 'S':
            cur['slices'].append({k: int(v) for k, v in (kv.split('=') for kv in p[2:])})
        elif p[0] == 'P':
            d = {'i': int(p[1])}
            for kv in p[2:]:
                if '=' in kv:
                    k, v = kv.split('=', 1); d[k] = v
                else:
                    d['size'] = kv
            for k in ('k', 'clear', 'st', 'd', 'v', 't0', 't1', 'sl'):
                d[k] = int(d[k])
            d['r'] = [x for x in d['r'].split(',') if x]
            cur['passes'].append(d)
    return out

def label(p):
    kind = {0: 'screen', 1: 'image', 2: 'filter'}[p['k']]
    return f"{kind}{'' if p['d'] else '-empty'}"

if __name__ == '__main__':
    fs = frames(sys.argv[1])
    want = [int(a) for a in sys.argv[2:]] or [f['n'] for f in fs if f['passes']]
    for f in fs:
        if f['n'] not in want or not f['passes']:
            continue
        ps = f['passes']
        t0 = min(p['t0'] for p in ps if p['t0']); t1 = max(p['t1'] for p in ps)
        busy = 0; end = 0
        for p in sorted(ps, key=lambda p: p['t0']):
            s, e = p['t0'], p['t1']
            if e > end:
                busy += e - max(s, end); end = e
        allocs = [e for e in f['events'] if e[1] == 'alloc']
        stencils = [e for e in f['events'] if e[1] == 'stencil']
        px = sum(int(e[3].split('x')[0]) * int(e[3].split('x')[1]) for e in allocs)
        print(f"frame {f['n']}: faults={f['faults']} passes={len(ps)} span={(t1-t0)/1e6:.2f} ms busy={busy/1e6:.2f} ms "
              f"sum={sum(p['t1']-p['t0'] for p in ps)/1e6:.2f} ms allocs={len(allocs)} ({px*4/1e6:.1f} MB) stencils={len(stencils)}")
