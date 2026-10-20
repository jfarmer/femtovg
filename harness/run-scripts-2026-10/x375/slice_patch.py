"""Experiment only, never committed: XSLICE=n submits the frame's command encoder every n render passes, the way
#368's submission slices do (timing only: an early slice reads the previous frame's uniforms, which in a harness run
of one scene repeated are the same).  usage: slice_patch.py WORKTREE"""
import pathlib, sys
f = pathlib.Path(sys.argv[1]) / 'src/renderer/wgpu.rs'
s = f.read_text()
def sub(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old)
    s = s.replace(old, new)
sub("""        XPASSES.fetch_add(1, std::sync::atomic::Ordering::Relaxed);
""", """        let begun = XPASSES.fetch_add(1, std::sync::atomic::Ordering::Relaxed);
        if let (Some(every), Some(queue)) = (xslice(), XQUEUE.get()) {
            if begun > 0 && begun % every == 0 {
                let finished = std::mem::replace(
                    self.encoder,
                    self.device.create_command_encoder(&wgpu::CommandEncoderDescriptor::default()),
                );
                queue.submit(Some(finished.finish()));
            }
        }
""")
sub("""    pub fn new(device: wgpu::Device, queue: wgpu::Queue) -> Self {
""", """    pub fn new(device: wgpu::Device, queue: wgpu::Queue) -> Self {
        let _ = XQUEUE.set(queue.clone());
""")
s += """static XQUEUE: std::sync::OnceLock<wgpu::Queue> = std::sync::OnceLock::new();
fn xslice() -> Option<usize> {
    static EVERY: std::sync::OnceLock<Option<usize>> = std::sync::OnceLock::new();
    *EVERY.get_or_init(|| std::env::var("XSLICE").ok().and_then(|v| v.parse().ok()))
}
"""
f.write_text(s)
print('slicing added to', f)
