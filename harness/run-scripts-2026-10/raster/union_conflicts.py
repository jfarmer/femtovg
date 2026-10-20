#!/usr/bin/env python3
"""union_conflicts.py FILE: resolves every conflict hunk in FILE by keeping both sides, ours then theirs (for
CHANGELOG entries added on two branches)."""
import sys
p = sys.argv[1]
out, side = [], None
for line in open(p):
    if line.startswith('<<<<<<< '):
        side = 'ours'
    elif line.startswith('||||||| ') and side == 'ours':
        side = 'base'
    elif line.startswith('=======') and side in ('ours', 'base'):
        side = 'theirs'
    elif line.startswith('>>>>>>> ') and side == 'theirs':
        side = None
    elif side != 'base':
        out.append(line)
open(p, 'w').write(''.join(out))
