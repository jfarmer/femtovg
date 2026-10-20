"""Per-process footprint, CPU time, instructions and cycles on macOS through proc_pid_rusage(RUSAGE_INFO_V4),
which reads any process of the same user, platform binaries (WebKit's XPC services) included."""
import ctypes, ctypes.util

_libc = ctypes.CDLL(ctypes.util.find_library('c'))
_RUSAGE_INFO_V4 = 4


class _Timebase(ctypes.Structure):
    _fields_ = [('numer', ctypes.c_uint32), ('denom', ctypes.c_uint32)]


_tb = _Timebase()
_libc.mach_timebase_info(ctypes.byref(_tb))
_TICK_NS = _tb.numer / _tb.denom

FIELDS = ['user_time', 'system_time', 'pkg_idle_wkups', 'interrupt_wkups', 'pageins', 'wired_size', 'resident_size',
          'phys_footprint', 'proc_start_abstime', 'proc_exit_abstime', 'child_user_time', 'child_system_time',
          'child_pkg_idle_wkups', 'child_interrupt_wkups', 'child_pageins', 'child_elapsed_abstime',
          'diskio_bytesread', 'diskio_byteswritten', 'qos_default', 'qos_maintenance', 'qos_background',
          'qos_utility', 'qos_legacy', 'qos_user_initiated', 'qos_user_interactive', 'billed_system_time',
          'serviced_system_time', 'logical_writes', 'lifetime_max_phys_footprint', 'instructions', 'cycles',
          'billed_energy', 'serviced_energy', 'interval_max_phys_footprint', 'runnable_time']


class _RusageV4(ctypes.Structure):
    _fields_ = [('uuid', ctypes.c_uint8 * 16)] + [(f, ctypes.c_uint64) for f in FIELDS]


def sample(pid):
    """dict of the fields (CPU times in ms), or None when the process is gone or unreadable."""
    r = _RusageV4()
    if _libc.proc_pid_rusage(ctypes.c_int(pid), _RUSAGE_INFO_V4, ctypes.byref(r)) != 0:
        return None
    d = {f: getattr(r, f) for f in FIELDS}
    for f in ('user_time', 'system_time'):
        d[f + '_ms'] = d[f] * _TICK_NS / 1e6
    d['cpu_ms'] = d['user_time_ms'] + d['system_time_ms']
    return d


def name_of(pid):
    buf = ctypes.create_string_buffer(1024)
    n = _libc.proc_pidpath(ctypes.c_int(pid), buf, ctypes.c_uint32(1024))
    return buf.value.decode(errors='replace') if n > 0 else None


if __name__ == '__main__':
    import os, sys
    for p in [int(a) for a in sys.argv[1:]] or [os.getpid()]:
        s = sample(p)
        print(p, name_of(p), None if s is None else {k: s[k] for k in ('phys_footprint', 'lifetime_max_phys_footprint', 'cpu_ms', 'instructions', 'cycles')})
