"""rotate.py ROUNDS FILLS FRAMES PAIRS,... TAG...  - bin/pm_rotate_TAG run round-robin, ROUNDS times each; median
encode_ms per (pairs, tag), the difference from the first tag, and instructions retired per frame."""
import re, statistics as st, subprocess, sys
B = '/Users/matt/src/femtovg-wt/bin'
rounds, fills, frames = int(sys.argv[1]), sys.argv[2], sys.argv[3]
pairs_list, tags = sys.argv[4].split(','), sys.argv[5:]
def run(tag, pairs, n):
    r = subprocess.run(['/usr/bin/time', '-l', f'{B}/pm_rotate_{tag}', pairs, fills, str(n)], capture_output=True, text=True)
    return float(re.search(r'encode_ms=([\d.]+)', r.stdout).group(1)), int(re.search(r'(\d+)\s+instructions retired', r.stderr).group(1))
for pairs in pairs_list:
    t = {tag: [] for tag in tags}; ins = {}
    for rnd in range(rounds):
        order = tags if rnd % 2 == 0 else tags[::-1]
        for tag in order:
            t[tag].append(run(tag, pairs, int(frames))[0])
    for tag in tags:
        lo, hi = run(tag, pairs, 50)[1], run(tag, pairs, 250)[1]
        ins[tag] = (hi - lo) / 200
    b, bi = st.median(t[tags[0]]), ins[tags[0]]
    print(f"pairs {pairs:>2s} ({2 * int(pairs):2d} pipelines):  " + '  '.join(
        f"{tag} {st.median(t[tag]):.3f} ({100 * (st.median(t[tag]) / b - 1):+5.1f} %, instr {100 * (ins[tag] / bi - 1):+5.1f} %)" for tag in tags), flush=True)
