//! Experiment only: what a texture costs on Metal when it is rendered sometimes with a stencil attachment
//! and sometimes without, inside one command buffer. No femtovg involved - raw wgpu render passes shaped like a
//! blurred layer's: capture (colour loaded, stencil loaded and stored), horizontal draw into a scratch, vertical
//! draw into the result, composite into the root.
//!
//! xalt WIDTH HEIGHT LAYERS FRAMES MODE [fresh]
//!   MODE  stable       the capture is always texture A, the result always texture B
//!         swap         capture and result trade places every layer (what one pool bucket does)
//!         swap-none    as swap, the capture pass without a stencil attachment
//!         swap-all     as swap, the result pass with the stencil attachment too
//!         stable-all   as stable, the result pass with a stencil attachment too
//!         swap-shared  as swap, one stencil texture serves both
//!   fresh the layer's textures are created again every frame, as a transient pool does
//! Prints per frame the wall time of submit + wait and the process's minor page faults over it.

#[repr(C)]
struct Timeval {
    tv_sec: i64,
    tv_usec: i32,
}
#[repr(C)]
struct Rusage {
    ru_utime: Timeval,
    ru_stime: Timeval,
    ru_maxrss: i64,
    rest: [i64; 13],
}
extern "C" {
    fn getrusage(who: i32, usage: *mut Rusage) -> i32;
}
/// (minor page faults, system CPU ms) of the process so far.
fn usage() -> (i64, f64) {
    let mut r = Rusage {
        ru_utime: Timeval { tv_sec: 0, tv_usec: 0 },
        ru_stime: Timeval { tv_sec: 0, tv_usec: 0 },
        ru_maxrss: 0,
        rest: [0; 13],
    };
    unsafe { getrusage(0, &mut r) };
    (
        r.rest[3],
        r.ru_stime.tv_sec as f64 * 1000.0 + r.ru_stime.tv_usec as f64 / 1000.0,
    )
}

const SHADER: &str = r#"
@group(0) @binding(0) var tex: texture_2d<f32>;
@group(0) @binding(1) var samp: sampler;
struct Out { @builtin(position) pos: vec4<f32>, @location(0) uv: vec2<f32> };
@vertex fn vs(@builtin(vertex_index) i: u32) -> Out {
    var o: Out;
    let p = vec2<f32>(f32((i << 1u) & 2u), f32(i & 2u));
    o.pos = vec4<f32>(p * 2.0 - 1.0, 0.0, 1.0);
    o.uv = p;
    return o;
}
@fragment fn fs(in: Out) -> @location(0) vec4<f32> {
    return textureSample(tex, samp, in.uv) * 0.5 + vec4<f32>(0.1, 0.2, 0.3, 0.4);
}
"#;

struct Target {
    view: wgpu::TextureView,
    stencil: Option<wgpu::TextureView>,
    bind: wgpu::BindGroup,
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let width: u32 = args[1].parse().unwrap();
    let height: u32 = args[2].parse().unwrap();
    let layers: usize = args[3].parse().unwrap();
    let frames: usize = args[4].parse().unwrap();
    let mode = args[5].as_str();
    let fresh = args.get(6).map(String::as_str) == Some("fresh");

    let instance = wgpu::Instance::default();
    let adapter = pollster::block_on(instance.request_adapter(&wgpu::RequestAdapterOptions::default())).unwrap();
    let (device, queue) = pollster::block_on(adapter.request_device(&wgpu::DeviceDescriptor {
        memory_hints: wgpu::MemoryHints::MemoryUsage,
        ..Default::default()
    }))
    .unwrap();

    let module = device.create_shader_module(wgpu::ShaderModuleDescriptor {
        label: None,
        source: wgpu::ShaderSource::Wgsl(SHADER.into()),
    });
    let layout = device.create_bind_group_layout(&wgpu::BindGroupLayoutDescriptor {
        label: None,
        entries: &[
            wgpu::BindGroupLayoutEntry {
                binding: 0,
                visibility: wgpu::ShaderStages::FRAGMENT,
                ty: wgpu::BindingType::Texture {
                    sample_type: wgpu::TextureSampleType::Float { filterable: true },
                    view_dimension: wgpu::TextureViewDimension::D2,
                    multisampled: false,
                },
                count: None,
            },
            wgpu::BindGroupLayoutEntry {
                binding: 1,
                visibility: wgpu::ShaderStages::FRAGMENT,
                ty: wgpu::BindingType::Sampler(wgpu::SamplerBindingType::Filtering),
                count: None,
            },
        ],
    });
    let pipeline_layout = device.create_pipeline_layout(&wgpu::PipelineLayoutDescriptor {
        label: None,
        bind_group_layouts: &[Some(&layout)],
        immediate_size: 0,
    });
    let pipeline = |stencil: bool| {
        device.create_render_pipeline(&wgpu::RenderPipelineDescriptor {
            label: None,
            layout: Some(&pipeline_layout),
            vertex: wgpu::VertexState {
                module: &module,
                entry_point: Some("vs"),
                buffers: &[],
                compilation_options: Default::default(),
            },
            fragment: Some(wgpu::FragmentState {
                module: &module,
                entry_point: Some("fs"),
                compilation_options: Default::default(),
                targets: &[Some(wgpu::ColorTargetState {
                    format: wgpu::TextureFormat::Rgba8Unorm,
                    blend: None,
                    write_mask: wgpu::ColorWrites::ALL,
                })],
            }),
            primitive: wgpu::PrimitiveState::default(),
            depth_stencil: stencil.then(|| wgpu::DepthStencilState {
                format: wgpu::TextureFormat::Stencil8,
                depth_write_enabled: Some(false),
                depth_compare: Some(wgpu::CompareFunction::Always),
                stencil: wgpu::StencilState {
                    front: wgpu::StencilFaceState::IGNORE,
                    back: wgpu::StencilFaceState::IGNORE,
                    read_mask: !0,
                    write_mask: !0,
                },
                bias: Default::default(),
            }),
            multisample: wgpu::MultisampleState::default(),
            multiview_mask: None,
            cache: None,
        })
    };
    let (with_stencil, without_stencil) = (pipeline(true), pipeline(false));
    let sampler = device.create_sampler(&wgpu::SamplerDescriptor::default());

    let make = |w: u32, h: u32, with_stencil: bool| -> Target {
        let size = wgpu::Extent3d {
            width: w,
            height: h,
            depth_or_array_layers: 1,
        };
        let color = device.create_texture(&wgpu::TextureDescriptor {
            label: None,
            size,
            mip_level_count: 1,
            sample_count: 1,
            dimension: wgpu::TextureDimension::D2,
            format: wgpu::TextureFormat::Rgba8Unorm,
            usage: wgpu::TextureUsages::TEXTURE_BINDING
                | wgpu::TextureUsages::COPY_DST
                | wgpu::TextureUsages::RENDER_ATTACHMENT,
            view_formats: &[],
        });
        let stencil = with_stencil.then(|| {
            device.create_texture(&wgpu::TextureDescriptor {
                label: None,
                size,
                mip_level_count: 1,
                sample_count: 1,
                dimension: wgpu::TextureDimension::D2,
                format: wgpu::TextureFormat::Stencil8,
                usage: wgpu::TextureUsages::RENDER_ATTACHMENT,
                view_formats: &[],
            })
        });
        let view = color.create_view(&Default::default());
        let bind = device.create_bind_group(&wgpu::BindGroupDescriptor {
            label: None,
            layout: &layout,
            entries: &[
                wgpu::BindGroupEntry {
                    binding: 0,
                    resource: wgpu::BindingResource::TextureView(&view),
                },
                wgpu::BindGroupEntry {
                    binding: 1,
                    resource: wgpu::BindingResource::Sampler(&sampler),
                },
            ],
        });
        Target {
            view,
            stencil: stencil.map(|stencil| stencil.create_view(&Default::default())),
            bind,
        }
    };

    // The root target and its stencil live for the whole run, like a canvas's.
    let root = make(460, 260, true);
    let dummy = make(1, 1, false);
    // SIZES=n: n sets of textures per frame, each of its own size (the first WIDTH x HEIGHT), LAYERS layers each.
    let sizes: u32 = std::env::var("SIZES").ok().and_then(|v| v.parse().ok()).unwrap_or(1);
    let a_stencil = mode != "swap-none";
    let b_stencil = matches!(mode, "swap" | "swap-all" | "stable-all");
    let mut held: Vec<[Target; 3]> = Vec::new();
    // SUMMARY=1: one line, the medians over the last six frames.
    let summary = std::env::var_os("SUMMARY").is_some();
    let mut last: Vec<(i64, f64, f64)> = Vec::new();

    for frame in 0..frames {
        if fresh || held.is_empty() {
            held = (0..sizes)
                .map(|i| {
                    // UNIFORM=1: every set at WIDTH x HEIGHT.
                    let (w, h) = if std::env::var_os("UNIFORM").is_some() {
                        (width, height)
                    } else {
                        (width + 64 * (i % 4), height + 64 * (i / 4))
                    };
                    [make(w, h, a_stencil), make(w, h, b_stencil), make(w, h, false)]
                })
                .collect();
        }
        // SLICE=n: a new command buffer every n passes; the frame's buffers are submitted together.
        let slice: usize = std::env::var("SLICE").ok().and_then(|v| v.parse().ok()).unwrap_or(usize::MAX);
        let mut encoders = vec![device.create_command_encoder(&Default::default())];
        let mut begun = 0usize;
        let mut pass = |target: &Target, stencil: Option<&wgpu::TextureView>, clear: bool, source: &Target| {
            if begun > 0 && begun % slice == 0 {
                encoders.push(device.create_command_encoder(&Default::default()));
            }
            begun += 1;
            let encoder = encoders.last_mut().unwrap();
            let mut rpass = encoder.begin_render_pass(&wgpu::RenderPassDescriptor {
                label: None,
                color_attachments: &[Some(wgpu::RenderPassColorAttachment {
                    view: &target.view,
                    resolve_target: None,
                    ops: wgpu::Operations {
                        load: if clear {
                            wgpu::LoadOp::Clear(wgpu::Color::default())
                        } else {
                            wgpu::LoadOp::Load
                        },
                        store: wgpu::StoreOp::Store,
                    },
                    depth_slice: None,
                })],
                depth_stencil_attachment: stencil.map(|view| wgpu::RenderPassDepthStencilAttachment {
                    view,
                    depth_ops: None,
                    stencil_ops: Some(wgpu::Operations {
                        load: wgpu::LoadOp::Load,
                        store: wgpu::StoreOp::Store,
                    }),
                }),
                timestamp_writes: None,
                occlusion_query_set: None,
                multiview_mask: None,
            });
            rpass.set_pipeline(if stencil.is_some() {
                &with_stencil
            } else {
                &without_stencil
            });
            rpass.set_bind_group(0, &source.bind, &[]);
            rpass.draw(0..3, 0..1);
        };
        pass(&root, root.stencil.as_ref(), false, &dummy);
        for layer in 0..layers * held.len() {
            let [a, b, scratch] = &held[layer / layers];
            let swap = mode.starts_with("swap") && layer % 2 == 1;
            let (capture, result) = if swap { (b, a) } else { (a, b) };
            let capture_stencil = match mode {
                "swap-none" => None,
                "swap-shared" => a.stencil.as_ref(),
                _ => capture.stencil.as_ref(),
            };
            let result_stencil = match mode {
                "swap-all" | "stable-all" => result.stencil.as_ref(),
                _ => None,
            };
            // The capture: loaded, like a layer's store after its clear_rect draw.
            pass(capture, capture_stencil, false, &dummy);
            pass(scratch, None, true, capture);
            pass(result, result_stencil, true, scratch);
            pass(&root, root.stencil.as_ref(), false, result);
        }
        drop(pass);
        let (faults, sys) = usage();
        let started = std::time::Instant::now();
        queue.submit(encoders.into_iter().map(|encoder| encoder.finish()));
        device.poll(wgpu::PollType::wait_indefinitely()).unwrap();
        let wall = started.elapsed().as_secs_f64() * 1000.0;
        let (faults_after, sys_after) = usage();
        if frame + 6 >= frames {
            last.push((faults_after - faults, wall, sys_after - sys));
        }
        if frame + 6 >= frames && !summary {
            println!(
                "{mode}{} {width}x{height} sizes={sizes} layers={layers} frame={frame} wait_ms={wall:.2} faults={} sys_ms={:.2}",
                if fresh { " fresh" } else { "" },
                faults_after - faults,
                sys_after - sys
            );
        }
    }
    if summary {
        let passes = 1 + 4 * layers * held.len();
        let stencils = 1 + held.len() * (usize::from(a_stencil) + usize::from(b_stencil));
        last.sort_by(|a, b| a.0.cmp(&b.0));
        let faults = last[last.len() / 2].0;
        last.sort_by(|a, b| a.1.total_cmp(&b.1));
        let wall = last[last.len() / 2].1;
        last.sort_by(|a, b| a.2.total_cmp(&b.2));
        let sys = last[last.len() / 2].2;
        println!(
            "{mode} {width}x{height} sets={sizes} layers={layers} passes={passes} stencils={stencils} faults={faults} wait_ms={wall:.2} sys_ms={sys:.2}"
        );
    }
}
