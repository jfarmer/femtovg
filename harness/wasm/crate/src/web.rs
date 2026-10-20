//! The page's entry: one device and one canvas for the whole run, as an app
//! keeps them, and per frame the switches the native harness reads from its
//! environment. A frame is `load` (parse), `render` (record, flush, submit),
//! `frame_done` once the queue has run it, then `request_pixels` and
//! `pixels` for the readback.
use super::*;
use std::sync::atomic::{AtomicU32, Ordering::Relaxed};
use std::sync::{Arc, Mutex};
use wasm_bindgen::prelude::*;

static ERRORS: Mutex<Vec<String>> = Mutex::new(Vec::new());
static LOST: Mutex<Option<String>> = Mutex::new(None);
/// The last submission the queue reported done.
static DONE: AtomicU32 = AtomicU32::new(0);
/// The readback: 0 idle, 1 mapping, 2 mapped, 3 failed.
static MAP_STATE: AtomicU32 = AtomicU32::new(0);

fn now_ms() -> f64 {
    web_sys::window()
        .and_then(|w| w.performance())
        .map(|p| p.now())
        .unwrap_or(0.0)
}

fn js_err(what: &str, e: impl std::fmt::Debug) -> JsValue {
    JsValue::from_str(&format!("{what}: {e:?}"))
}

/// Library defaults, restored when a frame does not set its own.
const TRANSIENT_DEFAULT: usize = 128 << 20;
const FILTER_WORK_DEFAULT: u64 = 4 << 30;
const CLIP_MASK_DEFAULT: usize = 32 << 20;

#[wasm_bindgen]
pub struct Harness {
    device: wgpu::Device,
    queue: wgpu::Queue,
    canvas: Canvas<WGPURenderer>,
    target: Option<(u32, u32, wgpu::Texture)>,
    fonts: Arc<usvg::fontdb::Database>,
    tree: Option<usvg::Tree>,
    readback: Option<(wgpu::Buffer, u32, u32, u32)>,
    /// One readback buffer per frame size, mapped and unmapped again for every frame: a buffer made per frame
    /// is only freed by the page's garbage collector (wgpu's WebGPU backend drops nothing), and in Chromium each
    /// held about twice its size in the renderer until then - 13 GB and a renderer crash over a corpus run.
    readback_pool: std::collections::HashMap<(u32, u32), wgpu::Buffer>,
    /// WebGL's adapter comes from a canvas's context.
    surface: Option<wgpu::Surface<'static>>,
    /// The two frames of `probe_element_upload`.
    probe_targets: Option<(wgpu::Texture, wgpu::Texture)>,
    submits: u32,
    info: String,
}

#[wasm_bindgen]
pub async fn create_harness(backend: String) -> Result<Harness, JsValue> {
    console_error_panic_hook::set_once();
    let backends = match backend.as_str() {
        "webgpu" => wgpu::Backends::BROWSER_WEBGPU,
        "webgl" => wgpu::Backends::GL,
        _ => return Err(JsValue::from_str("backend: webgpu or webgl")),
    };
    let instance = wgpu::Instance::new(wgpu::InstanceDescriptor {
        backends,
        flags: wgpu::InstanceFlags::from_build_config(),
        memory_budget_thresholds: wgpu::MemoryBudgetThresholds::default(),
        backend_options: wgpu::BackendOptions::default(),
        display: None,
    });
    // wgpu's WebGL backend finds no adapter without a surface: give it an offscreen canvas.
    let surface = if backend == "webgl" {
        use wasm_bindgen::JsCast;
        let canvas = web_sys::window()
            .and_then(|w| w.document())
            .and_then(|d| d.create_element("canvas").ok())
            .and_then(|e| e.dyn_into::<web_sys::HtmlCanvasElement>().ok())
            .ok_or_else(|| JsValue::from_str("no canvas"))?;
        canvas.set_width(16);
        canvas.set_height(16);
        Some(
            instance
                .create_surface(wgpu::SurfaceTarget::Canvas(canvas))
                .map_err(|e| js_err("create_surface", e))?,
        )
    } else {
        None
    };
    let adapter = instance
        .request_adapter(&wgpu::RequestAdapterOptions {
            power_preference: wgpu::PowerPreference::HighPerformance,
            force_fallback_adapter: false,
            compatible_surface: surface.as_ref(),
            ..Default::default()
        })
        .await
        .map_err(|e| js_err("request_adapter", e))?;
    let limits = if backend == "webgl" {
        wgpu::Limits::downlevel_webgl2_defaults().using_resolution(adapter.limits())
    } else {
        device_limits(&adapter)
    };
    let (device, queue) = adapter
        .request_device(&wgpu::DeviceDescriptor {
            label: None,
            required_features: wgpu::Features::empty(),
            required_limits: limits,
            experimental_features: wgpu::ExperimentalFeatures::disabled(),
            memory_hints: wgpu::MemoryHints::MemoryUsage,
            trace: wgpu::Trace::default(),
        })
        .await
        .map_err(|e| js_err("request_device", e))?;
    device.on_uncaptured_error(Arc::new(|e: wgpu::Error| {
        ERRORS.lock().unwrap().push(e.to_string());
    }));
    device.set_device_lost_callback(|reason, message| {
        *LOST.lock().unwrap() = Some(format!("{reason:?}: {message}"));
    });
    let info = adapter.get_info();
    let info = format!(
        "{} | {:?} | {} | {}",
        info.name, info.backend, info.driver, info.driver_info
    );
    let renderer = WGPURenderer::new(device.clone(), queue.clone());
    let canvas = Canvas::new(renderer).map_err(|e| js_err("Canvas::new", e))?;
    Ok(Harness {
        device,
        queue,
        canvas,
        target: None,
        fonts: Arc::new(usvg::fontdb::Database::new()),
        tree: None,
        readback: None,
        readback_pool: std::collections::HashMap::new(),
        surface,
        probe_targets: None,
        submits: 0,
        info,
    })
}

#[wasm_bindgen]
impl Harness {
    pub fn info(&self) -> String {
        self.info.clone()
    }

    pub fn set_env(&mut self, key: &str, value: &str) {
        crate::env_shim::set(key, value);
    }

    pub fn clear_env(&mut self) {
        crate::env_shim::clear();
    }

    /// Fonts for usvg's text: wasm has no system fonts, so the page loads the
    /// files the native harness resolves the corpus's families to.
    pub fn add_font(&mut self, data: Vec<u8>) {
        Arc::make_mut(&mut self.fonts).load_font_data(data);
    }

    pub fn font_faces(&self) -> usize {
        self.fonts.len()
    }

    /// The counters a native run starts from zero in its own process.
    pub fn reset_counters(&mut self) {
        for counter in [
            &LAYERS,
            &PASS_THROUGH,
            &FILTERS_SKIPPED,
            &INVALID_FILTER_REFS_DROPPED,
            &TURBULENCE_UNSUPPORTED,
            &CLIPS_UNSUPPORTED,
            &CLIP_COVERAGE_LAYERS,
            &TRANSIENT_AT_FLUSH,
            &FILLS,
            &MASKED_FILLS,
            &PATH_COUNTER,
            &DEPTH,
            &FRAME_INDEX,
        ] {
            counter.store(0, Relaxed);
        }
    }

    /// Parses an SVG as the native harness does; returns the milliseconds.
    pub fn load(&mut self, svg: &str) -> Result<f64, JsValue> {
        let started = now_ms();
        self.tree = None;
        let mut opt = usvg::Options::default();
        opt.fontdb = self.fonts.clone();
        let text = if crate::env_shim::var("KEEP_INVALID_FILTERS").is_ok() {
            std::borrow::Cow::Borrowed(svg)
        } else {
            drop_invalid_filter_references(svg)
        };
        let tree = usvg::Tree::from_str(&text, &opt).map_err(|e| js_err("usvg", e))?;
        self.tree = Some(tree);
        Ok(now_ms() - started)
    }

    /// Records, flushes and submits one frame at `scale`; returns the
    /// milliseconds spent before the submit (record + encode).
    pub fn render(&mut self, scale: f32, dark: bool) -> Result<f64, JsValue> {
        let (w, h) = (frame_w(), frame_h());
        if self.target.as_ref().map(|t| (t.0, t.1)) != Some((w, h)) {
            let texture = self.device.create_texture(&wgpu::TextureDescriptor {
                label: None,
                size: wgpu::Extent3d {
                    width: w,
                    height: h,
                    depth_or_array_layers: 1,
                },
                mip_level_count: 1,
                sample_count: 1,
                dimension: wgpu::TextureDimension::D2,
                format: wgpu::TextureFormat::Rgba8Unorm,
                usage: wgpu::TextureUsages::RENDER_ATTACHMENT | wgpu::TextureUsages::COPY_SRC,
                view_formats: &[],
            });
            self.target = Some((w, h, texture));
        }
        self.canvas.set_size(w, h, 1.0);
        // What the native main sets once per process, per frame here.
        #[cfg(harness_slices)]
        {
            let slicing = crate::env_shim::var_os("NO_SLICES").is_none().then(slicing_from_env);
            self.canvas.renderer_mut().set_submission_slicing(slicing);
        }
        #[cfg(harness_thin_fill_masks)]
        self.canvas
            .set_thin_fill_masks(crate::env_shim::var_os("NO_THIN_FILL_MASKS").is_none());
        #[cfg(harness_clip_paths)]
        self.canvas.set_clip_mask_budget(
            crate::env_shim::var("CLIP_MASK_BUDGET_MB")
                .ok()
                .and_then(|v| v.parse::<usize>().ok())
                .map_or(CLIP_MASK_DEFAULT, |mb| mb << 20),
        );
        self.canvas.set_transient_image_budget(
            crate::env_shim::var("TRANSIENT_BUDGET_MB")
                .ok()
                .and_then(|v| v.parse::<usize>().ok())
                .map_or(TRANSIENT_DEFAULT, |mb| mb << 20),
        );
        self.canvas.set_filter_work_budget(
            crate::env_shim::var("FILTER_WORK_GSAMPLES")
                .ok()
                .and_then(|v| v.parse::<u64>().ok())
                .map_or(FILTER_WORK_DEFAULT, |gs| gs << 30),
        );
        let tree = self.tree.as_ref().ok_or_else(|| JsValue::from_str("render: no tree"))?;
        let bg = if dark { Color::rgb(32, 34, 37) } else { Color::white() };
        let started = now_ms();
        render_scene(&mut self.canvas, tree, scale, bg);
        TRANSIENT_AT_FLUSH.store(self.canvas.transient_image_bytes(), Relaxed);
        let commands = self.canvas.flush_to_output(&self.target.as_ref().unwrap().2);
        let encode = now_ms() - started;
        self.queue.submit(commands);
        self.submits += 1;
        let submitted = self.submits;
        self.queue.on_submitted_work_done(move || {
            DONE.fetch_max(submitted, Relaxed);
        });
        Ok(encode)
    }

    /// Whether the queue has run everything submitted so far.
    pub fn frame_done(&self) -> bool {
        // WebGL runs wgpu-core in the page, whose callbacks fire only when the device is polled; WebGPU ignores it.
        let _ = self.device.poll(wgpu::PollType::Poll);
        DONE.load(Relaxed) >= self.submits
    }

    pub fn request_pixels(&mut self) -> Result<(), JsValue> {
        let (w, h, texture) = self.target.as_ref().ok_or_else(|| JsValue::from_str("no frame"))?;
        let (w, h) = (*w, *h);
        let padded = (w * 4).div_ceil(wgpu::COPY_BYTES_PER_ROW_ALIGNMENT) * wgpu::COPY_BYTES_PER_ROW_ALIGNMENT;
        let device = &self.device;
        let buffer = self
            .readback_pool
            .entry((w, h))
            .or_insert_with(|| {
                device.create_buffer(&wgpu::BufferDescriptor {
                    label: None,
                    size: (padded * h) as u64,
                    usage: wgpu::BufferUsages::COPY_DST | wgpu::BufferUsages::MAP_READ,
                    mapped_at_creation: false,
                })
            })
            .clone();
        let mut encoder = self
            .device
            .create_command_encoder(&wgpu::CommandEncoderDescriptor { label: None });
        encoder.copy_texture_to_buffer(
            wgpu::TexelCopyTextureInfo {
                texture,
                mip_level: 0,
                origin: wgpu::Origin3d::ZERO,
                aspect: wgpu::TextureAspect::All,
            },
            wgpu::TexelCopyBufferInfo {
                buffer: &buffer,
                layout: wgpu::TexelCopyBufferLayout {
                    offset: 0,
                    bytes_per_row: Some(padded),
                    rows_per_image: Some(h),
                },
            },
            wgpu::Extent3d {
                width: w,
                height: h,
                depth_or_array_layers: 1,
            },
        );
        self.queue.submit(Some(encoder.finish()));
        MAP_STATE.store(1, Relaxed);
        buffer.slice(..).map_async(wgpu::MapMode::Read, |result| {
            MAP_STATE.store(if result.is_ok() { 2 } else { 3 }, Relaxed);
        });
        self.readback = Some((buffer, w, h, padded));
        Ok(())
    }

    /// The frame's RGBA rows once mapped; `None` while the map is pending.
    pub fn pixels(&mut self) -> Result<Option<Vec<u8>>, JsValue> {
        let _ = self.device.poll(wgpu::PollType::Poll);
        match MAP_STATE.load(Relaxed) {
            1 => return Ok(None),
            3 => {
                MAP_STATE.store(0, Relaxed);
                self.readback = None;
                return Err(JsValue::from_str("readback map failed"));
            }
            _ => {}
        }
        let (buffer, w, h, padded) = self
            .readback
            .take()
            .ok_or_else(|| JsValue::from_str("no readback"))?;
        let mut rgba = Vec::with_capacity((w * h * 4) as usize);
        {
            let mapped = buffer.slice(..).get_mapped_range().map_err(|e| js_err("map range", e))?;
            for row in 0..h as usize {
                let start = row * padded as usize;
                rgba.extend_from_slice(&mapped[start..start + (w * 4) as usize]);
            }
        }
        buffer.unmap();
        MAP_STATE.store(0, Relaxed);
        Ok(Some(rgba))
    }

    /// The frame's counters as JSON, as the native LAYER_STATS lines report them.
    pub fn stats(&self) -> String {
        let (passes, command_buffers) = frame_passes(&self.canvas);
        format!(
            "{{\"layers\":{},\"pass_through\":{},\"skipped\":{},\"invalid_dropped\":{},\
             \"turbulence_unsupported\":{},\"clips_unsupported\":{},\"clip_coverage_layers\":{},\
             \"transient_at_flush\":{},\"passes\":{},\"command_buffers\":{},\"fills\":{},\"masked_fills\":{}}}",
            LAYERS.load(Relaxed),
            PASS_THROUGH.load(Relaxed),
            FILTERS_SKIPPED.load(Relaxed),
            INVALID_FILTER_REFS_DROPPED.load(Relaxed),
            TURBULENCE_UNSUPPORTED.load(Relaxed),
            CLIPS_UNSUPPORTED.load(Relaxed),
            CLIP_COVERAGE_LAYERS.load(Relaxed),
            TRANSIENT_AT_FLUSH.load(Relaxed),
            passes,
            command_buffers,
            FILLS.load(Relaxed),
            MASKED_FILLS.load(Relaxed),
        )
    }

    /// The order of an element upload against a frame flushed before it and
    /// submitted after it, with slicing off: an image given red bytes, frame
    /// A drawing it flushed and held, the image given `element`, frame B
    /// drawing it flushed, A and B submitted together. A should draw red and
    /// B the element; `select_probe_target` then `request_pixels` read them.
    pub fn probe_element_upload(&mut self, element: web_sys::HtmlCanvasElement) -> Result<(), JsValue> {
        let (w, h) = (16u32, 16u32);
        let make = |device: &wgpu::Device| {
            device.create_texture(&wgpu::TextureDescriptor {
                label: None,
                size: wgpu::Extent3d { width: w, height: h, depth_or_array_layers: 1 },
                mip_level_count: 1,
                sample_count: 1,
                dimension: wgpu::TextureDimension::D2,
                format: wgpu::TextureFormat::Rgba8Unorm,
                usage: wgpu::TextureUsages::RENDER_ATTACHMENT | wgpu::TextureUsages::COPY_SRC,
                view_formats: &[],
            })
        };
        let (first, second) = (make(&self.device), make(&self.device));
        self.canvas.set_size(w, h, 1.0);
        #[cfg(harness_slices)]
        self.canvas.renderer_mut().set_submission_slicing(None);
        let red = vec![femtovg::rgb::RGBA8::new(255, 0, 0, 255); 16];
        let image = self
            .canvas
            .create_image(femtovg::imgref::Img::new(red.as_slice(), 4, 4), ImageFlags::NEAREST)
            .map_err(|e| js_err("create_image", e))?;
        let mut whole = Path::new();
        whole.rect(0.0, 0.0, w as f32, h as f32);
        let paint = Paint::image(image, 0.0, 0.0, w as f32, h as f32, 0.0, 1.0);
        self.canvas.fill_path(&whole, &paint);
        let a = self.canvas.flush_to_output(&first);
        self.canvas
            .update_image(image, femtovg::ImageSource::HtmlCanvasElement(&element), 0, 0)
            .map_err(|e| js_err("update_image", e))?;
        self.canvas.fill_path(&whole, &paint);
        let b = self.canvas.flush_to_output(&second);
        self.queue.submit(a.into_iter().chain(b));
        self.canvas.delete_image(image);
        self.probe_targets = Some((first, second));
        Ok(())
    }

    /// Makes frame A (0) or B (1) of the last probe what `request_pixels` reads.
    pub fn select_probe_target(&mut self, which: u32) -> Result<(), JsValue> {
        let (a, b) = self.probe_targets.as_ref().ok_or_else(|| JsValue::from_str("no probe"))?;
        let texture = if which == 0 { a.clone() } else { b.clone() };
        self.target = Some((16, 16, texture));
        Ok(())
    }

    /// Uncaptured device errors since the last call.
    pub fn take_errors(&mut self) -> Vec<String> {
        std::mem::take(&mut *ERRORS.lock().unwrap())
    }

    /// Why the device was lost, if it was.
    pub fn lost(&self) -> Option<String> {
        LOST.lock().unwrap().clone()
    }
}
