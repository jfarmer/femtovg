import re, sys, collections
for f in sys.argv[1:]:
    lines = [l for l in open(f) if re.match(r'^\s*[0-9a-f]+:\s', l)]
    c = collections.Counter()
    calls = collections.Counter()
    for l in lines:
        ins = l.split(':', 1)[1].strip()
        op = ins.split()[0] if ins else ''
        args = ins[len(op):]
        if op in ('bl', 'blr'):
            m = re.search(r'<([^>]+)>', args); calls[(m.group(1) if m else 'indirect')[:60]] += 1
        if re.search(r'\.(4s|2s|2d|16b|8b|8h|4h|s|d)$', op) and op not in ('ld', 'st') and re.search(r'\bv\d+', args) or re.search(r'\bv\d+\.(4s|2s|2d|16b|8b|8h|4h)', args) or op in ('ld1', 'st1', 'ld2', 'st2', 'ld1r', 'dup', 'zip1', 'zip2', 'uzp1', 'uzp2', 'trn1', 'trn2', 'ext', 'ins', 'mov') and re.search(r'\bv\d+', args):
            c['neon-vector'] += 1
        elif re.search(r'\bs\d+\b', args) and op.startswith('f') or op in ('fcvtzs', 'fcvtzu', 'scvtf', 'ucvtf', 'fcsel'):
            c['scalar-fp'] += 1
        elif op.startswith('ld') or op.startswith('st'):
            # q/d/s regs loads are SIMD loads
            if re.search(r'\b[qdsv]\d+\b', args.split(',')[0] + (args.split(',')[1] if ',' in args else '')):
                c['simd-ldst'] += 1
            else:
                c['int-ldst'] += 1
        elif op.startswith('b') or op in ('cbz', 'cbnz', 'tbz', 'tbnz', 'ret'):
            c['branch'] += 1
        else:
            c['int-other'] += 1
        if op in ('fsqrt',): c['fsqrt'] += 1
        if op in ('fdiv',): c['fdiv'] += 1
    vec = [l.split(':',1)[1].strip() for l in lines if re.search(r'\bv\d+\.(4s|2s)', l)]
    print(f'== {f}: {len(lines)} instrs', dict(c), 'calls:', dict(calls))
    if '-v' in sys.argv[0:1]: pass
