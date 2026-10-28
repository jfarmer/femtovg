"""Experiment only, never committed: more knobs on top of knobs_patch.py + trace_patch.py.
  X_NO_STENCIL=1      image render targets get no stencil attachment (wrong pixels for stencil fills; timing only)
  X_FILTER_STENCIL=1  filter targets get a stencil attachment too, like image render targets
  X_ROT3=1            a FLIP_Y pool bucket keeps one spare and hands out its oldest image: capture and result rotate
                      through three textures, and a capture never takes the image the composite before it read
usage: knobs2_patch.py WORKTREE"""
import pathlib, sys
wt = pathlib.Path(sys.argv[1])
def edit(rel, pairs):
    f = wt / rel; s = f.read_text()
    for old, new in pairs:
        assert s.count(old) == 1, (rel, s.count(old), old)
        s = s.replace(old, new)
    f.write_text(s)
edit('src/transient.rs', [
    ('["X_RELEASE", "X_TAG", "X_FIFO", "X_SPARE"]', '["X_RELEASE", "X_TAG", "X_FIFO", "X_NO_STENCIL", "X_FILTER_STENCIL", "X_ROT3", "X_S6", "X_S7"]'),
    ('static KNOBS: std::sync::OnceLock<[bool; 4]>', 'static KNOBS: std::sync::OnceLock<[bool; 8]>'),
    ("""        let id = if xknob(2) {""", """        let id = if xknob(5) && info.flags().contains(ImageFlags::FLIP_Y) {
            if bucket.len() < 2 {
                return None;
            }
            bucket.remove(0)
        } else if xknob(2) {"""),
])
edit('src/renderer/wgpu.rs', [
    ("""        if let Texture::Internal(texture) = &image.texture {
            let stencil_buffer = self
                .stencil_buffer_for_textures""", """        if let Texture::Internal(texture) = &image.texture {
            if crate::transient::xknob(3) {
                self.set_render_target_texture(&texture.clone(), None, load);
                return;
            }
            let stencil_buffer = self
                .stencil_buffer_for_textures"""),
    ("""        if let Texture::Internal(texture) = &image.texture {
            self.set_render_target_texture(texture, None, load);
        }""", """        if let Texture::Internal(texture) = &image.texture {
            if crate::transient::xknob(4) {
                let stencil_buffer = self
                    .stencil_buffer_for_textures
                    .entry(texture.clone())
                    .or_insert_with(|| {
                        xtrace::event(format!("stencil {:x}", xtrace::tex_id(texture)));
                        self.device.create_texture(&wgpu::TextureDescriptor {
                            label: Some("Stencil buffer"),
                            size: wgpu::Extent3d {
                                width: texture.width(),
                                height: texture.height(),
                                depth_or_array_layers: 1,
                            },
                            mip_level_count: 1,
                            sample_count: 1,
                            dimension: wgpu::TextureDimension::D2,
                            format: wgpu::TextureFormat::Stencil8,
                            view_formats: &[],
                            usage: wgpu::TextureUsages::RENDER_ATTACHMENT,
                        })
                    })
                    .clone();
                self.set_render_target_texture(texture, Some(stencil_buffer), load);
                return;
            }
            self.set_render_target_texture(texture, None, load);
        }"""),
])
print('knobs2 added to', wt)
