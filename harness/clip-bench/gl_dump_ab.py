#!/usr/bin/env python3
"""gl_dump_ab.py A B SCALE[,SCALE...] FILE.svg... : gl_svg_dump of each file at each scale with the builds
$HARNESS_BIN/gl_svg_dump_A and _B, compared byte for byte. For a dump that differs it also prints how far each build's
is from the same build's with TEXT_AS_PATHS=1, which draws the text without femtovg's text code: the share of pixels
beyond 20/255. Build the tools with harness/build.sh --gl. WORKERS dumps run at a time (6)."""
import os, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from PIL import Image
B = os.environ.get('HARNESS_BIN', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'bin'))
a, b, scales, files = sys.argv[1], sys.argv[2], sys.argv[3].split(','), sys.argv[4:]
# gl_svg_dump aborts on a file it cannot read, which the system reports as a crashed application.
missing = [f for f in files if not os.path.isfile(f)]
if missing:
    sys.exit(f'no such file: {missing[0]}' + (f' and {len(missing) - 1} more' if len(missing) > 1 else ''))


def dump(build, scale, f, **env):
    with tempfile.NamedTemporaryFile(suffix='.ppm') as out:
        subprocess.run([f'{B}/gl_svg_dump_{build}', out.name, scale, f], env={**os.environ, **env}, check=True,
                       capture_output=True, timeout=300)
        return np.asarray(Image.open(out.name).convert('RGB'), dtype=np.int16)


def beyond(x, y):
    return 100 * float((np.abs(x - y).max(axis=2) > 20).mean())


def job(args):
    f, scale = args
    x, y = dump(a, scale, f), dump(b, scale, f)
    if (x == y).all():
        return None
    return f, scale, beyond(x, dump(a, scale, f, TEXT_AS_PATHS='1')), beyond(y, dump(b, scale, f, TEXT_AS_PATHS='1'))


jobs = [(f, scale) for f in files for scale in scales]
with ThreadPoolExecutor(int(os.environ.get('WORKERS', 6))) as ex:
    try:
        differ = [r for r in ex.map(job, jobs) if r]
    except BaseException:
        # One dump failed: do not start the ones still waiting.
        ex.shutdown(cancel_futures=True)
        raise
for f, scale, da, db in differ:
    print(f'{os.path.basename(f)[:-4]} at {scale}: beyond 20/255 of its text as paths, {a} {da:.2f} %, {b} {db:.2f} %')
print(f'{len(jobs)} dumps: {len(jobs) - len(differ)} the same on {a} and {b}, {len(differ)} differ')
