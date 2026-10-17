//! The OpenGL backend's pixels for small Canvas 2D scenes, without a visible window: `gl_scenes SCENES.json OUT_DIR`
//! draws each scene of the file - save, restore, clip to a polygon, set the composite operation, fill a polygon -
//! into a transparent image target, as a canvas starts, and writes it over white as OUT_DIR/<index>.png. The same
//! file drawn on a Chromium canvas (hard-mask-scenes/scenes_chromium.py) is the reference.
use std::num::NonZeroU32;

use femtovg::{
    renderer::OpenGl, Canvas, Color, CompositeOperation, FillRule, ImageFlags, Paint, Path, PixelFormat, RenderTarget,
};
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

fn polygon(points: &[serde_json::Value]) -> Path {
    let mut path = Path::new();
    for (i, p) in points.iter().enumerate() {
        let (x, y) = (p[0].as_f64().unwrap() as f32, p[1].as_f64().unwrap() as f32);
        if i == 0 {
            path.move_to(x, y);
        } else {
            path.line_to(x, y);
        }
    }
    path.close();
    path
}

/// A path of several closed contours, each a list of points.
fn contours(contours: &[serde_json::Value]) -> Path {
    let mut path = Path::new();
    for contour in contours {
        for (i, p) in contour.as_array().unwrap().iter().enumerate() {
            let (x, y) = (p[0].as_f64().unwrap() as f32, p[1].as_f64().unwrap() as f32);
            if i == 0 {
                path.move_to(x, y);
            } else {
                path.line_to(x, y);
            }
        }
        path.close();
    }
    path
}

/// The fill rule an op names, as the argument of ctx.fill() and ctx.clip(): non-zero unless "evenodd".
fn rule(name: Option<&serde_json::Value>) -> FillRule {
    match name.and_then(|rule| rule.as_str()) {
        Some("evenodd") => FillRule::EvenOdd,
        _ => FillRule::NonZero,
    }
}

fn operation(name: &str) -> CompositeOperation {
    match name {
        "source-over" => CompositeOperation::SourceOver,
        "source-in" => CompositeOperation::SourceIn,
        "source-out" => CompositeOperation::SourceOut,
        "source-atop" => CompositeOperation::Atop,
        "destination-over" => CompositeOperation::DestinationOver,
        "destination-in" => CompositeOperation::DestinationIn,
        "destination-out" => CompositeOperation::DestinationOut,
        "destination-atop" => CompositeOperation::DestinationAtop,
        "lighter" => CompositeOperation::Lighter,
        "copy" => CompositeOperation::Copy,
        "xor" => CompositeOperation::Xor,
        // Chromium's legacy `clear` keeps none of source or destination: for the opaque fills of the
        // scenes that is destination-out.
        "clear" => CompositeOperation::DestinationOut,
        other => panic!("no composite operation {other}"),
    }
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
        let args: Vec<String> = std::env::args().collect();
        let spec: serde_json::Value = serde_json::from_str(&std::fs::read_to_string(&args[1]).unwrap()).unwrap();
        let out = args[2].clone();
        let (w, h) = (spec["width"].as_u64().unwrap() as u32, spec["height"].as_u64().unwrap() as u32);
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
        let renderer = unsafe { OpenGl::new_from_function_cstr(|s| gl_display.get_proc_address(s).cast()) }.unwrap();
        let mut canvas = Canvas::new(renderer).unwrap();
        canvas.set_size(w, h, 1.0);
        for (index, scene) in spec["scenes"].as_array().unwrap().iter().enumerate() {
            let image = canvas
                .create_image_empty(w as usize, h as usize, PixelFormat::Rgba8, ImageFlags::empty())
                .unwrap();
            canvas.set_render_target(RenderTarget::Image(image));
            canvas.clear_rect(0, 0, w, h, Color::rgbaf(0.0, 0.0, 0.0, 0.0));
            for op in scene["ops"].as_array().unwrap() {
                match op[0].as_str().unwrap() {
                    "save" => canvas.save(),
                    "restore" => canvas.restore(),
                    "clip" => canvas.clip_path(&polygon(op[1].as_array().unwrap()), FillRule::NonZero),
                    "composite" => canvas.global_composite_operation(operation(op[1].as_str().unwrap())),
                    "fill" => canvas.fill_path(
                        &polygon(op[2].as_array().unwrap()),
                        &Paint::color(Color::hex(op[1].as_str().unwrap())),
                    ),
                    "fillpath" => canvas.fill_path(
                        &contours(op[2].as_array().unwrap()),
                        &Paint::color(Color::hex(op[1].as_str().unwrap())).with_fill_rule(rule(op.get(3))),
                    ),
                    "clippath" => canvas.clip_path(&contours(op[1].as_array().unwrap()), rule(op.get(2))),
                    other => panic!("unknown op {other}"),
                }
            }
            canvas.flush_to_output(());
            let shot = canvas.screenshot().unwrap();
            // Premultiplied over white.
            let mut rgb = image::RgbImage::new(w, h);
            for (p, px) in shot.pixels().zip(rgb.pixels_mut()) {
                let a = p.a as f32 / 255.0;
                for (c, v) in [p.r, p.g, p.b].into_iter().enumerate() {
                    px[c] = (v as f32 + (1.0 - a) * 255.0).round().min(255.0) as u8;
                }
            }
            rgb.save(format!("{out}/{index}.png")).unwrap();
            canvas.set_render_target(RenderTarget::Screen);
            canvas.delete_image(image);
        }
        event_loop.exit();
    }

    fn window_event(&mut self, _: &ActiveEventLoop, _: winit::window::WindowId, _: WindowEvent) {}
}

fn main() {
    let event_loop = EventLoop::new().unwrap();
    event_loop.run_app(&mut App { done: false }).unwrap();
}
