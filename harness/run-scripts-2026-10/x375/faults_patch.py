"""Experiment only, never committed: page faults (ru_minflt) per slice and per frame in the pass trace.
usage: faults_patch.py WORKTREE"""
import pathlib, sys
f = pathlib.Path(sys.argv[1]) / 'src/renderer/wgpu.rs'
s = f.read_text()
def sub(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old)
    s = s.replace(old, new)
sub("""        /// Slice mode: per slice (submit ns, wait ns, passes).
        pub slices: Vec<(u64, u64, u32)>,""", """        /// Slice mode: per slice (submit ns, wait ns, passes, page faults).
        pub slices: Vec<(u64, u64, u32, i64)>,
        pub faults_at_frame: i64,""")
sub("""        let started = std::time::Instant::now();
        queue.submit(Some(encoder.finish()));""", """        let faults = minor_faults();
        let started = std::time::Instant::now();
        queue.submit(Some(encoder.finish()));""")
sub("""            state
                .slices
                .push((submitted.as_nanos() as u64, waited.as_nanos() as u64, state.since_slice));""", """            state.slices.push((
                submitted.as_nanos() as u64,
                waited.as_nanos() as u64,
                state.since_slice,
                minor_faults() - faults,
            ));""")
sub("""        for (index, (submit, wait, count)) in slices.iter().enumerate() {
            out.push_str(&format!("S {index} submit={submit} wait={wait} passes={count}\\n"));
        }""", """        for (index, (submit, wait, count, faults)) in slices.iter().enumerate() {
            out.push_str(&format!("S {index} submit={submit} wait={wait} passes={count} faults={faults}\\n"));
        }""")
sub("""        out.push_str(&format!("F {frame} passes={} slices={}\\n", passes.len(), slices.len()));""",
    """        let faults_now = minor_faults();
        let frame_faults = with(|state| {
            let delta = faults_now - state.faults_at_frame;
            state.faults_at_frame = faults_now;
            delta
        })
        .unwrap_or(0);
        out.push_str(&format!(
            "F {frame} passes={} slices={} faults={frame_faults}\\n",
            passes.len(),
            slices.len()
        ));""")
sub("""    pub fn on() -> bool {
        path().is_some()
    }""", """    pub fn on() -> bool {
        path().is_some()
    }

    #[repr(C)]
    struct RUsage {
        times: [i64; 4],
        longs: [i64; 14],
    }
    extern "C" {
        fn getrusage(who: i32, usage: *mut RUsage) -> i32;
    }
    /// The process's minor page faults so far (ru_minflt).
    pub fn minor_faults() -> i64 {
        let mut usage = RUsage {
            times: [0; 4],
            longs: [0; 14],
        };
        unsafe { getrusage(0, &mut usage) };
        usage.longs[4]
    }""")
f.write_text(s)
print('faults added to', f)
