#!/usr/bin/env python3
"""Summaries of counters/*.json (rec_campaign.py): per-frame E-core user-mode counts and mixes per variant and file,
and where a variant's extra instructions go by function.

usage: analyze.py mix | diff FILE VARIANT [TEMPLATE] | funcs FILE VARIANT [TEMPLATE]
"""
import glob, json, os, re, sys

OUT = os.path.expanduser('~/src/femtovg-wt/runs/mac-anatomy')
VARS = ['m7', 'm7f', 'fb', 'fc']
FILES = ['tiger', 'puzzle-fox', 'mr-settodefault', 'svgenius-icon32', 'svgenius-icon5']


def load(tpl, f, v):
    p = f'{OUT}/counters/{tpl}_{f}_{v}.json'
    if not os.path.exists(p):
        return None
    d = json.load(open(p))
    n = len(d['events'])
    d['frame'] = d['frame'][:n]
    d['all'] = d['all'][:n]
    for k in ('leaf', 'incl'):
        d[k] = {name: vals[:n] for name, vals in d[k].items()}
    return d


def per_frame(d):
    return {e: v / d['frames'] for e, v in zip(d['events'], d['frame'])}


def demangle(s):
    s = re.sub(r'_\$LT\$', '<', s)
    s = s.replace('$LT$', '<').replace('$GT$', '>').replace('$u20$', ' ').replace('$C$', ',').replace('..', '::')
    s = s.replace('$u7b$', '{').replace('$u7d$', '}').replace('$RF$', '&').replace('$BP$', '*')
    return s


def mix():
    rows = []
    for f in FILES:
        for v in VARS:
            r = {'file': f, 'variant': v}
            for tpl in ('T1', 'T2', 'T3'):
                d = load(tpl, f, v)
                if d:
                    pf = per_frame(d)
                    for e, x in pf.items():
                        if e in ('FIXED_CYCLES', 'FIXED_INSTRUCTIONS'):
                            r.setdefault(e, []).append(x)
                        else:
                            r[e] = x
                    r.setdefault('samples', []).append(d['samples'].get('frame', 0))
            rows.append(r)
    json.dump(rows, open(f'{OUT}/mix.json', 'w'), indent=1)
    hdr = ('file', 'var', 'instr M', 'cyc M', 'IPC', 'SIMD/FP alu', 'vec SIMD', 'int alu', 'int ld', 'int st', 'simd ld',
           'simd st', 'branch', 'L1D ld miss/ki', 'L1D st miss/ki', 'mispred/ki', 'map stall %', 'old-miss %', 'dTLB/ki')
    print(' | '.join(hdr))
    for r in rows:
        if 'FIXED_INSTRUCTIONS' not in r:
            continue
        ins = sum(r['FIXED_INSTRUCTIONS']) / len(r['FIXED_INSTRUCTIONS'])
        cyc = sum(r['FIXED_CYCLES']) / len(r['FIXED_CYCLES'])
        pct = lambda e: f"{100 * r[e] / ins:5.1f}" if e in r else '  -  '
        pki = lambda e: f"{1000 * r[e] / ins:5.2f}" if e in r else '  -  '
        pcy = lambda e: f"{100 * r[e] / cyc:5.1f}" if e in r else '  -  '
        print(' | '.join([r['file'], r['variant'], f'{ins / 1e6:6.2f}', f'{cyc / 1e6:6.2f}', f'{ins / cyc:4.2f}',
                          pct('INST_SIMD_ALU'), pct('INST_SIMD_ALU_VEC'), pct('INST_INT_ALU'), pct('INST_INT_LD'),
                          pct('INST_INT_ST'), pct('INST_SIMD_LD'), pct('INST_SIMD_ST'), pct('INST_BRANCH'),
                          pki('L1D_CACHE_MISS_LD'), pki('L1D_CACHE_MISS_ST'), pki('BRANCH_MISPRED_NONSPEC'),
                          pcy('MAP_STALL'), pcy('LDST_UNIT_OLD_L1D_CACHE_MISS'), pki('L1D_TLB_MISS')]))


def funcs(f, v, tpl='T1', key='leaf', k=40):
    d = load(tpl, f, v)
    ev = d['events']
    ins_i = ev.index('FIXED_INSTRUCTIONS')
    tot = d['frame'][ins_i]
    print(f'{f} {v} {tpl} {key}: {tot / d["frames"] / 1e6:.2f} M instr/frame, {d["samples"]}')
    for name, vals in sorted(d[key].items(), key=lambda kv: -kv[1][ins_i])[:k]:
        x = vals[ins_i]
        extra = ' '.join(f'{e[:12]}={100 * vals[i] / x:4.1f}%' for i, e in enumerate(ev) if e.startswith('INST_') and x)
        print(f'{100 * x / tot:6.2f}% {x / d["frames"] / 1e3:8.1f} k/frame  {demangle(name)[:90]:90s} {extra}')


def diff(f, v, tpl='T1', key='leaf', k=30, base='m7'):
    a, b = load(tpl, f, base), load(tpl, f, v)
    ev = a['events']
    ii = ev.index('FIXED_INSTRUCTIONS')
    ci = ev.index('FIXED_CYCLES')
    fa, fb = a['frames'], b['frames']
    names = set(a[key]) | set(b[key])
    rows = []
    for n in names:
        x = a[key].get(n, [0] * len(ev))
        y = b[key].get(n, [0] * len(ev))
        rows.append((y[ii] / fb - x[ii] / fa, y[ci] / fb - x[ci] / fa, x[ii] / fa, y[ii] / fb, n))
    tot_i = b['frame'][ii] / fb - a['frame'][ii] / fa
    tot_c = b['frame'][ci] / fb - a['frame'][ci] / fa
    print(f'{f} {base} -> {v} ({tpl}, {key}): instructions/frame {a["frame"][ii] / fa / 1e6:.2f} -> {b["frame"][ii] / fb / 1e6:.2f} M '
          f'({tot_i / 1e6:+.2f} M), cycles/frame {a["frame"][ci] / fa / 1e6:.2f} -> {b["frame"][ci] / fb / 1e6:.2f} M ({tot_c / 1e6:+.2f} M)')
    for di, dc, x, y, n in sorted(rows, key=lambda r: -abs(r[0]))[:k]:
        print(f'  {di / 1e3:+9.1f} k instr ({100 * di / tot_i:+6.1f}% of the change)  {dc / 1e3:+8.1f} k cyc   '
              f'{x / 1e3:9.1f} -> {y / 1e3:9.1f} k  {demangle(n)[:100]}')


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'mix':
        mix()
    elif cmd == 'funcs':
        funcs(sys.argv[2], sys.argv[3], *(sys.argv[4:5] or ['T1']), key=(sys.argv[5] if len(sys.argv) > 5 else 'leaf'))
    elif cmd == 'diff':
        diff(sys.argv[2], sys.argv[3], *(sys.argv[4:5] or ['T1']), key=(sys.argv[5] if len(sys.argv) > 5 else 'leaf'))


def phases():
    """Per file/variant: per-frame user instructions and the mix of each phase (scene = render_scene, flush =
    flush_to_output), merged over T1-T3 (each template's own FIXED counters normalize its events)."""
    roots = {'scene': '_logos_full::render_scene', 'flush': 'femtovg::Canvas$LT$T$GT$::flush_to_output',
             'femtovg-fill': 'femtovg::Canvas$LT$T$GT$::fill_path_internal', 'env': 'std::env::_var'}
    out = {}
    for f in FILES:
        for v in VARS:
            rec = {}
            for tpl in ('T1', 'T2', 'T3'):
                d = load(tpl, f, v)
                if not d:
                    continue
                ev = d['events']
                ii, ci = ev.index('FIXED_INSTRUCTIONS'), ev.index('FIXED_CYCLES')
                for ph, root in [('frame', None)] + list(roots.items()):
                    vals = d['frame'] if root is None else d['incl'].get(root)
                    if not vals:
                        continue
                    r = rec.setdefault(ph, {'instr': [], 'cycles': []})
                    r['instr'].append(vals[ii] / d['frames'])
                    r['cycles'].append(vals[ci] / d['frames'])
                    for i, e in enumerate(ev):
                        if i in (ii, ci):
                            continue
                        r[e + '_per_instr'] = vals[i] / vals[ii]
                        r[e + '_per_cycle'] = vals[i] / vals[ci]
            out[f'{f}/{v}'] = rec
    json.dump(out, open(f'{OUT}/phases.json', 'w'), indent=1)
    keys = ['INST_SIMD_ALU', 'INST_SIMD_ALU_VEC', 'INST_INT_ALU', 'INST_INT_LD', 'INST_INT_ST', 'INST_SIMD_LD',
            'INST_SIMD_ST', 'INST_BRANCH']
    print('per-instruction shares (%), L1D misses and mispredicts per 1000 instructions, stalls as % of cycles')
    print('file/variant phase | instr M/frame | cyc M | IPC | ' + ' | '.join(k.replace('INST_', '') for k in keys) +
          ' | L1D ld miss/ki | L1D st miss/ki | mispred/ki | dTLB miss/ki | MAP_STALL %cyc | old L1D miss wait %cyc | dispatch bubble %cyc | uops/instr')
    for fv, rec in out.items():
        for ph in ('frame', 'scene', 'flush'):
            r = rec.get(ph)
            if not r:
                continue
            ins = sum(r['instr']) / len(r['instr'])
            cyc = sum(r['cycles']) / len(r['cycles'])
            g = lambda k, s='_per_instr', m=100: f"{m * r[k + s]:5.1f}" if k + s in r else '  -  '
            print(f'{fv:28s} {ph:6s} | {ins / 1e6:6.2f} | {cyc / 1e6:6.2f} | {ins / cyc:4.2f} | ' +
                  ' | '.join(g(k) for k in keys) + ' | ' +
                  ' | '.join([g('L1D_CACHE_MISS_LD', m=1000), g('L1D_CACHE_MISS_ST', m=1000), g('BRANCH_MISPRED_NONSPEC', m=1000),
                              g('L1D_TLB_MISS', m=1000), g('MAP_STALL', '_per_cycle'), g('LDST_UNIT_OLD_L1D_CACHE_MISS', '_per_cycle'),
                              g('MAP_DISPATCH_BUBBLE', '_per_cycle'), g('RETIRE_UOP', m=1)]))


if __name__ == '__main__' and sys.argv[1] == 'phases':
    phases()
