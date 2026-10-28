//! Investigation (OpenGL): a glyph drawn at one transform must not depend on what the canvas drew
//! before. `gl_glyph_history OUTDIR` draws the text of the wgpu test tests/glyph_atlas_history_wgpu.rs
//! as frame A then frame B on one canvas, and frame B on a fresh canvas, for each case.
use std::num::NonZeroU32;

use femtovg::{renderer::OpenGl, Canvas, Color, ImageFlags, Paint, PixelFormat, PositionedGlyph, RenderTarget};
use glutin::{
    config::ConfigTemplateBuilder,
    context::{ContextApi, ContextAttributesBuilder},
    display::GetGlDisplay,
    prelude::*,
    surface::SurfaceAttributesBuilder,
};
use glutin_winit::DisplayBuilder;
use raw_window_handle::HasWindowHandle;
use winit::application::ApplicationHandler;
use winit::event::WindowEvent;
use winit::event_loop::{ActiveEventLoop, EventLoop};
use winit::window::Window;

const W: u32 = 460;
const H: u32 = 260;
const FONT: &[u8] = include_bytes!("assets/RobotoFlex-VariableFont.ttf");
const LINES: [(f32, f32, &str); 3] = [
    (-0.3, 40.0, "Offset -0.3px"),
    (-0.7, 80.0, "Offset -0.7px"),
    (-15.4, 120.0, "Offset -15.4px"),
];

fn frames(get: &dyn Fn(&std::ffi::CStr) -> *const std::ffi::c_void, glyph_run: bool, steps: &[(f32, f32, f32)]) -> Vec<u8> {
    let renderer = unsafe { OpenGl::new_from_function_cstr(|s| get(s)) }.unwrap();
    let mut canvas = Canvas::new(renderer).unwrap();
    canvas.set_size(W, H, 1.0);
    let font = canvas.add_font_mem(FONT).unwrap();
    let paint = Paint::color(Color::rgb(0x22, 0x22, 0x22)).with_font(&[font]).with_font_size(20.0);
    let runs: Vec<Vec<PositionedGlyph>> = LINES
        .iter()
        .map(|&(x, y, text)| {
            canvas.measure_text(x, y, text, &paint).unwrap().glyphs.iter()
                .map(|g| PositionedGlyph { x: g.x, y: g.y, glyph_id: g.glyph_id }).collect()
        })
        .collect();
    let image = canvas.create_image_empty(W as usize, H as usize, PixelFormat::Rgba8, ImageFlags::empty()).unwrap();
    let mut last = Vec::new();
    for &(s, tx, ty) in steps {
        canvas.set_render_target(RenderTarget::Image(image));
        canvas.clear_rect(0, 0, W, H, Color::white());
        canvas.save();
        canvas.translate(tx, ty);
        canvas.scale(s, s);
        for (i, &(x, y, text)) in LINES.iter().enumerate() {
            if glyph_run {
                canvas.fill_glyph_run(font, &[], runs[i].iter().cloned(), &paint).unwrap();
            } else {
                canvas.fill_text(x, y, text, &paint).unwrap();
            }
        }
        canvas.restore();
        canvas.flush_to_output(());
        let shot = canvas.screenshot().unwrap();
        last = shot.pixels().flat_map(|p| [p.r, p.g, p.b]).collect();
    }
    last
}

fn harness(zoom: f32) -> (f32, f32, f32) {
    let s = 0.5 * zoom;
    (s, 230.0 + zoom * (130.0 - 230.0) + 100.0 * s, 130.0 + zoom * (30.0 - 130.0))
}

struct App {
    done: bool,
}

impl ApplicationHandler for App {
    fn resumed(&mut self, event_loop: &ActiveEventLoop) {
        if self.done {
            return;
        }
        self.done = true;
        let window_attrs = Window::default_attributes()
            .with_inner_size(winit::dpi::PhysicalSize::new(64, 64))
            .with_visible(false);
        let template = ConfigTemplateBuilder::new().with_alpha_size(8).with_stencil_size(8);
        let (window, gl_config) = DisplayBuilder::new()
            .with_window_attributes(Some(window_attrs))
            .build(event_loop, template, |mut configs| configs.next().unwrap())
            .unwrap();
        let window = window.unwrap();
        let raw = window.window_handle().unwrap().as_raw();
        let gl_display = gl_config.display();
        let attributes = ContextAttributesBuilder::new().build(Some(raw));
        let fallback = ContextAttributesBuilder::new().with_context_api(ContextApi::Gles(None)).build(Some(raw));
        let context = unsafe {
            gl_display
                .create_context(&gl_config, &attributes)
                .unwrap_or_else(|_| gl_display.create_context(&gl_config, &fallback).unwrap())
        };
        let attrs = SurfaceAttributesBuilder::<glutin::surface::WindowSurface>::new().build(
            raw,
            NonZeroU32::new(64).unwrap(),
            NonZeroU32::new(64).unwrap(),
        );
        let surface = unsafe { gl_display.create_window_surface(&gl_config, &attrs).unwrap() };
        let _context = context.make_current(&surface).unwrap();
        let get = |s: &std::ffi::CStr| gl_display.get_proc_address(s).cast();
        let out = std::env::args().nth(1).unwrap();
        let cases: Vec<(&str, Vec<(f32, f32, f32)>)> = vec![
            ("harness_z1_to_z1.25", vec![harness(1.0), harness(1.25)]),
            ("harness_z1.2_to_z1.25", vec![harness(1.2), harness(1.25)]),
            ("s0.5_to_s0.625_tx167.5", vec![(0.5, 180.0, 30.0), (0.625, 167.5, 5.0)]),
            ("s0.5_to_s0.625_tx167", vec![(0.5, 180.0, 30.0), (0.625, 167.0, 5.0)]),
            ("s0.5_to_s0.625_tx167.25", vec![(0.5, 180.0, 30.0), (0.625, 167.25, 5.0)]),
            ("s0.5_to_s0.625_tx10.5", vec![(0.5, 180.0, 30.0), (0.625, 10.5, 5.0)]),
            ("s0.5_to_s0.625_ty5.5", vec![(0.5, 180.0, 30.0), (0.625, 167.0, 5.5)]),
            ("s0.25_to_s0.625_tx167.5", vec![(0.25, 180.0, 30.0), (0.625, 167.5, 5.0)]),
            ("s0.5_to_s1_tx100.5", vec![(0.5, 180.0, 30.0), (1.0, 100.5, 5.0)]),
        ];
        for glyph_run in [true, false] {
            for (name, steps) in &cases {
                let ladder = frames(&get, glyph_run, steps);
                let fresh = frames(&get, glyph_run, &steps[steps.len() - 1..]);
                let (mut n, mut m) = (0, 0u8);
                for (a, b) in ladder.chunks_exact(3).zip(fresh.chunks_exact(3)) {
                    let d = (0..3).map(|i| a[i].abs_diff(b[i])).max().unwrap();
                    if d > 0 { n += 1; m = m.max(d); }
                }
                let api = if glyph_run { "GlyphRun" } else { "FillText" };
                println!("GL {api} {name}: ladder vs fresh {n} px, max {m}");
                for (kind, px) in [("ladder", &ladder), ("fresh", &fresh)] {
                    let mut ppm = format!("P6\n{W} {H}\n255\n").into_bytes();
                    ppm.extend_from_slice(px);
                    std::fs::write(format!("{out}/GL_{api}_{name}_{kind}.ppm"), ppm).unwrap();
                }
            }
        }
        event_loop.exit();
    }

    fn window_event(&mut self, _: &ActiveEventLoop, _: winit::window::WindowId, _: WindowEvent) {}
}

fn main() {
    let event_loop = EventLoop::new().unwrap();
    event_loop.run_app(&mut App { done: false }).unwrap();
}
