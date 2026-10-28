"""gate.py  - quiet(): waits (up to BUSY_WAIT seconds) until the other processes use less than BUSY_LIMIT % CPU."""
import os, subprocess, time
def busy():
    out = subprocess.run(['ps', '-Ao', 'pcpu=,comm='], capture_output=True, text=True).stdout
    return sum(float(l.split(None, 1)[0]) for l in out.splitlines() if l.strip() and '_logos_full_' not in l)
def quiet(limit=float(os.environ.get('BUSY_LIMIT', 350)), longest=float(os.environ.get('BUSY_WAIT', 120))):
    start = time.time()
    while time.time() - start < longest:
        if busy() < limit:
            time.sleep(2)
            if busy() < limit:
                break
        time.sleep(5)
    return busy()
