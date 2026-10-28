"""Experiment only, never committed: XSTATS=1 prints, per rendered frame, the render passes begun and the stencil
textures the wgpu backend holds for image render targets.  usage: stats_patch.py WORKTREE"""
import pathlib, sys
f = pathlib.Path(sys.argv[1]) / 'src/renderer/wgpu.rs'
s = f.read_text()
def sub(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old)
    s = s.replace(old, new)
sub("""        let mut rpass = self.encoder.begin_render_pass(&wgpu::RenderPassDescriptor {""",
    """        XPASSES.fetch_add(1, std::sync::atomic::Ordering::Relaxed);
        let mut rpass = self.encoder.begin_render_pass(&wgpu::RenderPassDescriptor {""")
sub("""        let command_buffer = encoder.finish();
""", """        let command_buffer = encoder.finish();
        if std::env::var_os("XSTATS").is_some() {
            eprintln!(
                "XS passes={} stencils={}",
                XPASSES.swap(0, std::sync::atomic::Ordering::Relaxed),
                self.stencil_buffer_for_textures.len()
            );
        }
""")
s += "\nstatic XPASSES: std::sync::atomic::AtomicUsize = std::sync::atomic::AtomicUsize::new(0);\n"
f.write_text(s)
print('stats added to', f)
