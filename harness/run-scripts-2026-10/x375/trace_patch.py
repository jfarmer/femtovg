"""Experiment only, never committed: a per-pass trace in a worktree's wgpu backend.

  PASS_TRACE=<file>   every render pass of each frame (target texture, size, load op, stencil, draws, sampled
                      textures) with its GPU start/end timestamps, and every texture created or deleted.
  PASS_SLICE=<n>      with PASS_TRACE: submit after every n passes inside render() and wait for the GPU, so
                      wall time is attributed to pass ranges (no timestamps in this mode).

usage: trace_patch.py WORKTREE
"""
import pathlib, sys

wt = pathlib.Path(sys.argv[1])
f = wt / 'src/renderer/wgpu.rs'
s = f.read_text()


def sub(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old)
    s = s.replace(old, new)


# --- renderer creation: keep a queue/device for the slicing mode
sub("""    pub fn new(device: wgpu::Device, queue: wgpu::Queue) -> Self {
""", """    pub fn new(device: wgpu::Device, queue: wgpu::Queue) -> Self {
        xtrace::init(&device, &queue);
""")

# --- frame begin / query set
sub("""        let mut encoder = self
            .device
            .create_command_encoder(&wgpu::CommandEncoderDescriptor::default());

        let mut render_pass_builder = RenderPassBuilder::new(""", """        let mut encoder = self
            .device
            .create_command_encoder(&wgpu::CommandEncoderDescriptor::default());
        let x_query = xtrace::frame_begin(&self.device);

        let mut render_pass_builder = RenderPassBuilder::new(""")
sub("""        // Ensure that we have one initial render pass, in case the first command is not SetRenderTarget
        render_pass_builder.set_render_target_screen();
""", """        render_pass_builder.x_query = x_query.clone();
        // Ensure that we have one initial render pass, in case the first command is not SetRenderTarget
        render_pass_builder.set_render_target_screen();
""")
sub("""        drop(render_pass_builder);

        // write_buffer is ordered ahead of the caller's submit.""", """        drop(render_pass_builder);
        xtrace::frame_end(&self.device, &mut encoder, x_query.as_ref());

        // write_buffer is ordered ahead of the caller's submit.""")

# --- image lifetime events
sub("""        Ok(Image {
            texture: Texture::Internal(self.device.create_texture(&wgpu::TextureDescriptor {
                label: None,
                size: wgpu::Extent3d {
                    width: info.width() as u32,""", """        let x_texture = self.device.create_texture(&wgpu::TextureDescriptor {
                label: None,
                size: wgpu::Extent3d {
                    width: info.width() as u32,""")
sub("""                view_formats: &[],
            })),
            info,
        })
    }

    fn create_image_from_native_texture(""", """                view_formats: &[],
            });
        xtrace::event(format!(
            "alloc {:x} {}x{} flags={:#x}",
            xtrace::tex_id(&x_texture),
            info.width(),
            info.height(),
            info.flags().bits()
        ));
        Ok(Image {
            texture: Texture::Internal(x_texture),
            info,
        })
    }

    fn create_image_from_native_texture(""")
sub("""        if let Texture::Internal(texture) = &image.texture {
            self.stencil_buffer_for_textures.remove(texture);
        }
        drop(image);""", """        if let Texture::Internal(texture) = &image.texture {
            xtrace::event(format!("delete {:x}", xtrace::tex_id(texture)));
            self.stencil_buffer_for_textures.remove(texture);
        }
        drop(image);""")

# --- stencil creation event
sub("""                .entry(texture.clone())
                .or_insert_with(|| {
                    self.device.create_texture(&wgpu::TextureDescriptor {
                        label: Some("Stencil buffer"),""", """                .entry(texture.clone())
                .or_insert_with(|| {
                    xtrace::event(format!("stencil {:x}", xtrace::tex_id(texture)));
                    self.device.create_texture(&wgpu::TextureDescriptor {
                        label: Some("Stencil buffer"),""")

# --- pass builder fields
sub("""    current_stencil_reference: Option<u32>,
    current_bound_offset: Option<u32>,
}

impl<'a> RenderPassBuilder<'a> {""", """    current_stencil_reference: Option<u32>,
    current_bound_offset: Option<u32>,
    x_query: Option<wgpu::QuerySet>,
    x_tex: u64,
}

impl<'a> RenderPassBuilder<'a> {""")
sub("""            current_pipeline_state: None,
            current_stencil_reference: None,
            current_bound_offset: None,
        }
    }
""", """            current_pipeline_state: None,
            current_stencil_reference: None,
            current_bound_offset: None,
            x_query: None,
            x_tex: 0,
        }
    }
""")
sub("""        self.texture_view = texture.create_view(&Default::default());
        self.set_viewport([texture.width() as f32, texture.height() as f32]);""", """        self.texture_view = texture.create_view(&Default::default());
        self.x_tex = xtrace::tex_id(texture);
        self.set_viewport([texture.width() as f32, texture.height() as f32]);""")
sub("""        self.texture_view = self.surface_view.clone();
        self.stencil_buffer = Some(self.screen_stencil_buffer.clone());""", """        self.texture_view = self.surface_view.clone();
        self.x_tex = 0;
        self.stencil_buffer = Some(self.screen_stencil_buffer.clone());""")

# --- the pass itself
sub("""        drop(self.rpass.take());
        let stencil_view = self""", """        drop(self.rpass.take());
        if xtrace::slice_due() {
            let finished = std::mem::replace(
                self.encoder,
                self.device
                    .create_command_encoder(&wgpu::CommandEncoderDescriptor::default()),
            );
            xtrace::submit_slice(finished);
        }
        let x_index = xtrace::begin_pass(
            if !self.rendering_to_texture {
                0
            } else if self.stencil_buffer.is_some() {
                1
            } else {
                2
            },
            self.x_tex,
            self.viewport,
            matches!(load, wgpu::LoadOp::Clear(_)),
            self.stencil_buffer.is_some(),
        );
        let x_writes = match (&self.x_query, x_index) {
            (Some(query_set), Some(index)) if index < xtrace::MAX_PASSES => Some(wgpu::RenderPassTimestampWrites {
                query_set,
                beginning_of_pass_write_index: Some(2 * index),
                end_of_pass_write_index: Some(2 * index + 1),
            }),
            _ => None,
        };
        let stencil_view = self""")
sub("""            timestamp_writes: None,
            occlusion_query_set: None,
            multiview_mask: None,
        });
        rpass.set_vertex_buffer(0, self.vertex_buffer.slice(..));""", """            timestamp_writes: x_writes,
            occlusion_query_set: None,
            multiview_mask: None,
        });
        rpass.set_vertex_buffer(0, self.vertex_buffer.slice(..));""")
sub("""    fn draw(&mut self, vertices: std::ops::Range<u32>) {
        self.rpass.as_mut().unwrap().draw(vertices, 0..1);""", """    fn draw(&mut self, vertices: std::ops::Range<u32>) {
        xtrace::draw(vertices.end - vertices.start);
        self.rpass.as_mut().unwrap().draw(vertices, 0..1);""")

# --- what each draw samples
sub("""        let bind_group_state = BindGroupState { image, glyph_texture };
""", """        if xtrace::on() {
            for id in [image, glyph_texture.image_id()].into_iter().flatten() {
                if let Some(Image {
                    texture: Texture::Internal(texture),
                    ..
                }) = images.get(id)
                {
                    xtrace::read(xtrace::tex_id(texture));
                }
            }
        }
        let bind_group_state = BindGroupState { image, glyph_texture };
""")

s += r'''
// ---- experiment only, never committed: per-pass trace ----
#[allow(dead_code)]
pub(crate) mod xtrace {
    use std::hash::{Hash, Hasher};
    use std::io::Write;
    use std::sync::{Mutex, OnceLock};

    pub const MAX_PASSES: u32 = 2048;

    #[derive(Default, Clone)]
    pub struct Pass {
        pub kind: u8,
        pub tex: u64,
        pub w: u32,
        pub h: u32,
        pub clear: bool,
        pub stencil: bool,
        pub draws: u32,
        pub verts: u32,
        pub reads: Vec<u64>,
        /// Slice mode: the slice this pass was submitted in.
        pub slice: u32,
    }

    #[derive(Default)]
    pub struct State {
        pub frame: usize,
        pub passes: Vec<Pass>,
        pub events: Vec<String>,
        /// Slice mode: per slice (submit ns, wait ns, passes).
        pub slices: Vec<(u64, u64, u32)>,
        pub since_slice: u32,
        pub pending: Option<(wgpu::Buffer, u32)>,
        pub device: Option<wgpu::Device>,
        pub queue: Option<wgpu::Queue>,
    }

    static STATE: Mutex<Option<State>> = Mutex::new(None);

    fn path() -> Option<&'static str> {
        static PATH: OnceLock<Option<String>> = OnceLock::new();
        PATH.get_or_init(|| std::env::var("PASS_TRACE").ok()).as_deref()
    }

    fn slice_every() -> Option<u32> {
        static EVERY: OnceLock<Option<u32>> = OnceLock::new();
        *EVERY.get_or_init(|| std::env::var("PASS_SLICE").ok().and_then(|v| v.parse().ok()))
    }

    pub fn on() -> bool {
        path().is_some()
    }

    pub fn tex_id(texture: &wgpu::Texture) -> u64 {
        let mut hasher = std::collections::hash_map::DefaultHasher::new();
        texture.hash(&mut hasher);
        hasher.finish() & 0xffff_ffff
    }

    fn with<R>(f: impl FnOnce(&mut State) -> R) -> Option<R> {
        if !on() {
            return None;
        }
        let mut guard = STATE.lock().unwrap();
        Some(f(guard.get_or_insert_with(State::default)))
    }

    pub fn init(device: &wgpu::Device, queue: &wgpu::Queue) {
        with(|state| {
            state.device = Some(device.clone());
            state.queue = Some(queue.clone());
        });
    }

    pub fn event(text: String) {
        with(|state| {
            let at = state.passes.len();
            state.events.push(format!("{at} {text}"));
        });
    }

    /// Dumps the previous frame (its timestamps are resolved by now) and
    /// starts a new one; the query set for this frame's passes.
    pub fn frame_begin(device: &wgpu::Device) -> Option<wgpu::QuerySet> {
        if !on() {
            return None;
        }
        dump(device);
        if slice_every().is_some() || !device.features().contains(wgpu::Features::TIMESTAMP_QUERY) {
            return None;
        }
        Some(device.create_query_set(&wgpu::QuerySetDescriptor {
            label: None,
            ty: wgpu::QueryType::Timestamp,
            count: 2 * MAX_PASSES,
        }))
    }

    pub fn begin_pass(kind: u8, tex: u64, viewport: [f32; 2], clear: bool, stencil: bool) -> Option<u32> {
        with(|state| {
            state.since_slice += 1;
            let slice = state.slices.len() as u32;
            state.passes.push(Pass {
                kind,
                tex,
                w: viewport[0] as u32,
                h: viewport[1] as u32,
                clear,
                stencil,
                slice,
                ..Default::default()
            });
            state.passes.len() as u32 - 1
        })
    }

    pub fn draw(verts: u32) {
        with(|state| {
            if let Some(pass) = state.passes.last_mut() {
                pass.draws += 1;
                pass.verts += verts;
            }
        });
    }

    pub fn read(tex: u64) {
        with(|state| {
            if let Some(pass) = state.passes.last_mut() {
                if !pass.reads.contains(&tex) {
                    pass.reads.push(tex);
                }
            }
        });
    }

    pub fn slice_due() -> bool {
        let Some(every) = slice_every() else {
            return false;
        };
        with(|state| state.since_slice >= every).unwrap_or(false)
    }

    /// Submits the passes encoded so far and waits for the GPU.
    pub fn submit_slice(encoder: wgpu::CommandEncoder) {
        let (device, queue) = {
            let guard = STATE.lock().unwrap();
            let state = guard.as_ref().unwrap();
            (state.device.clone().unwrap(), state.queue.clone().unwrap())
        };
        let started = std::time::Instant::now();
        queue.submit(Some(encoder.finish()));
        let submitted = started.elapsed();
        device.poll(wgpu::PollType::wait_indefinitely()).unwrap();
        let waited = started.elapsed() - submitted;
        with(|state| {
            state
                .slices
                .push((submitted.as_nanos() as u64, waited.as_nanos() as u64, state.since_slice));
            state.since_slice = 0;
        });
    }

    pub fn frame_end(device: &wgpu::Device, encoder: &mut wgpu::CommandEncoder, query_set: Option<&wgpu::QuerySet>) {
        let Some(query_set) = query_set else {
            return;
        };
        let count = with(|state| (state.passes.len() as u32).min(MAX_PASSES) * 2).unwrap_or(0);
        if count == 0 {
            return;
        }
        let size = u64::from(count) * 8;
        let resolve = device.create_buffer(&wgpu::BufferDescriptor {
            label: None,
            size,
            usage: wgpu::BufferUsages::QUERY_RESOLVE | wgpu::BufferUsages::COPY_SRC,
            mapped_at_creation: false,
        });
        let read = device.create_buffer(&wgpu::BufferDescriptor {
            label: None,
            size,
            usage: wgpu::BufferUsages::COPY_DST | wgpu::BufferUsages::MAP_READ,
            mapped_at_creation: false,
        });
        encoder.resolve_query_set(query_set, 0..count, &resolve, 0);
        encoder.copy_buffer_to_buffer(&resolve, 0, &read, 0, size);
        with(|state| state.pending = Some((read, count)));
    }

    fn dump(device: &wgpu::Device) {
        let Some((passes, events, slices, pending, frame, queue)) = with(|state| {
            let frame = state.frame;
            state.frame += 1;
            state.since_slice = 0;
            (
                std::mem::take(&mut state.passes),
                std::mem::take(&mut state.events),
                std::mem::take(&mut state.slices),
                state.pending.take(),
                frame,
                state.queue.clone(),
            )
        }) else {
            return;
        };
        if passes.is_empty() && events.is_empty() {
            return;
        }
        let mut stamps: Vec<u64> = Vec::new();
        if let Some((buffer, count)) = pending {
            let slice = buffer.slice(..);
            slice.map_async(wgpu::MapMode::Read, |_| {});
            device.poll(wgpu::PollType::wait_indefinitely()).unwrap();
            let mapped = slice.get_mapped_range().unwrap();
            let period = queue.map_or(1.0, |queue| f64::from(queue.get_timestamp_period()));
            stamps = mapped
                .chunks_exact(8)
                .take(count as usize)
                .map(|bytes| (u64::from_le_bytes(bytes.try_into().unwrap()) as f64 * period) as u64)
                .collect();
        }
        let mut out = String::new();
        out.push_str(&format!("F {frame} passes={} slices={}\n", passes.len(), slices.len()));
        for event in &events {
            out.push_str(&format!("E {event}\n"));
        }
        for (index, (submit, wait, count)) in slices.iter().enumerate() {
            out.push_str(&format!("S {index} submit={submit} wait={wait} passes={count}\n"));
        }
        for (index, pass) in passes.iter().enumerate() {
            let reads: Vec<String> = pass.reads.iter().map(|tex| format!("{tex:x}")).collect();
            let (t0, t1) = (
                stamps.get(2 * index).copied().unwrap_or(0),
                stamps.get(2 * index + 1).copied().unwrap_or(0),
            );
            out.push_str(&format!(
                "P {index} k={} t={:x} {}x{} clear={} st={} d={} v={} r={} t0={t0} t1={t1} sl={}\n",
                pass.kind,
                pass.tex,
                pass.w,
                pass.h,
                u8::from(pass.clear),
                u8::from(pass.stencil),
                pass.draws,
                pass.verts,
                reads.join(","),
                pass.slice,
            ));
        }
        if let Some(path) = path() {
            if let Ok(mut file) = std::fs::OpenOptions::new().create(true).append(true).open(path) {
                let _ = file.write_all(out.as_bytes());
            }
        }
    }
}
'''
f.write_text(s)
print('patched', f)
