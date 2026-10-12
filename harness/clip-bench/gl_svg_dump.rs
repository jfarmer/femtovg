//! The OpenGL backend's pixels for SVG fills, strokes and text, without a visible window: `gl_svg_dump OUT.ppm SCALE
//! FILE.svg` draws each path of the file with its fill and stroke, in a solid colour or a gradient, and each text
//! as glyph runs from usvg's layout (`Canvas::fill_glyph_run`, `Canvas::stroke_glyph_run`), into a 1024 x 1024 image
//! target and writes it as a binary PPM. A stroke has its width and no other style. There are no clips, masks,
//! filters, group opacities, patterns, text decorations or `paint-order`. Two builds' dumps of the same file compare
//! how their fills and their text rasterize. TEXT_AS_PATHS=1 draws usvg's outlines of each text as paths instead, the
//! same glyphs without femtovg's text code.
use std::collections::HashMap;
use std::num::NonZeroU32;
use std::sync::Arc;

use femtovg::{
    renderer::OpenGl, Canvas, Color, FillRule, FontId, ImageFlags, Paint, Path, PixelFormat, PositionedGlyph,
    RenderTarget, TextContext, Transform2D,
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
use usvg::tiny_skia_path::PathSegment;
use winit::application::ApplicationHandler;
use winit::event::WindowEvent;
use winit::event_loop::{ActiveEventLoop, EventLoop};
use winit::window::Window;

const W: u32 = 1024;
const H: u32 = 1024;

fn transform(t: usvg::Transform) -> Transform2D {
    Transform2D([t.sx, t.ky, t.kx, t.sy, t.tx, t.ty])
}

fn stops(stops: &[usvg::Stop]) -> Vec<(f32, Color)> {
    stops
        .iter()
        .map(|stop| {
            let c = stop.color();
            let mut color = Color::rgb(c.red, c.green, c.blue);
            color.set_alphaf(stop.opacity().get());
            (stop.offset().get(), color)
        })
        .collect()
}

/// A fill's or a stroke's paint without its opacity, which the caller sets as the canvas's global alpha.
fn to_paint(paint: &usvg::Paint) -> Option<Paint> {
    Some(match paint {
        usvg::Paint::Color(c) => Paint::color(Color::rgb(c.red, c.green, c.blue)),
        usvg::Paint::LinearGradient(g) => {
            Paint::linear_gradient_stops(g.x1(), g.y1(), g.x2(), g.y2(), stops(g.stops()))
                .with_gradient_transform(transform(g.transform()))
        }
        usvg::Paint::RadialGradient(g) => {
            Paint::two_point_radial_gradient_stops(g.fx(), g.fy(), 0.0, g.cx(), g.cy(), g.r().get(), stops(g.stops()))
                .with_gradient_transform(transform(g.transform()))
        }
        usvg::Paint::Pattern(_) => return None,
    })
}

/// One span's glyphs as glyph runs: each stretch of glyphs that is in one font, in the text's coordinates.
type SpanRuns = Vec<(FontId, Vec<PositionedGlyph>)>;

/// The faces of usvg's font database that the file's text is set in, loaded as fonts of the canvas's text context.
struct Fonts {
    context: TextContext,
    fontdb: Arc<usvg::fontdb::Database>,
    loaded: HashMap<usvg::fontdb::ID, Option<FontId>>,
}

impl Fonts {
    /// The femtovg font for a face, loaded when it is first asked for. None if femtovg does not take the face, or
    /// if it is a variable font: usvg lays that out at the weight, width and optical size the text's style asks
    /// for, and a glyph run here is drawn at the font's defaults.
    fn font(&mut self, id: usvg::fontdb::ID) -> Option<FontId> {
        let (context, fontdb) = (&self.context, &self.fontdb);
        *self.loaded.entry(id).or_insert_with(|| {
            fontdb
                .with_face_data(id, |data, index| {
                    context.add_shared_font_with_index(data.to_vec(), index).ok()
                })
                .flatten()
                .filter(|font| context.font_variation_axes(*font).is_ok_and(|axes| axes.is_empty()))
        })
    }

    /// The glyph runs of each span of `text`, or None if a glyph run cannot hold one of its glyphs. A glyph run
    /// places a glyph by its origin and draws it upright at one font size, so a glyph that usvg turned or stretched
    /// (`rotate`, text on a path, vertical text, `lengthAdjust`) does not fit, and neither does a glyph of a font
    /// that `font` does not load.
    fn glyph_runs(&mut self, text: &usvg::Text) -> Option<Vec<SpanRuns>> {
        text.layouted()
            .iter()
            .map(|span| {
                let mut runs = SpanRuns::new();
                let mut run_font = None;
                for glyph in &span.positioned_glyphs {
                    // Maps the glyph's outline, in font units, into the text's coordinates.
                    let t = glyph.transform();
                    let slack = 1e-6 * t.sx;
                    if t.sx <= 0.0 || t.kx.abs() > slack || t.ky.abs() > slack || (t.sx - t.sy).abs() > slack {
                        return None;
                    }
                    if run_font != Some(glyph.font) {
                        runs.push((self.font(glyph.font)?, Vec::new()));
                        run_font = Some(glyph.font);
                    }
                    runs.last_mut()?.1.push(PositionedGlyph {
                        x: t.tx,
                        y: t.ty,
                        glyph_id: u16::try_from(glyph.id.0).ok()?,
                    });
                }
                Some(runs)
            })
            .collect()
    }
}

fn draw(canvas: &mut Canvas<OpenGl>, group: &usvg::Group, base: Transform2D, fonts: &mut Fonts) {
    for node in group.children() {
        match node {
            usvg::Node::Group(g) => draw(canvas, g, base, fonts),
            usvg::Node::Path(p) => {
                let mut path = Path::new();
                for seg in p.data().segments() {
                    match seg {
                        PathSegment::MoveTo(a) => path.move_to(a.x, a.y),
                        PathSegment::LineTo(a) => path.line_to(a.x, a.y),
                        PathSegment::QuadTo(a, b) => path.quad_to(a.x, a.y, b.x, b.y),
                        PathSegment::CubicTo(a, b, c) => path.bezier_to(a.x, a.y, b.x, b.y, c.x, c.y),
                        PathSegment::Close => path.close(),
                    }
                }
                canvas.save();
                canvas.reset_transform();
                canvas.set_transform(&(transform(p.abs_transform()) * base));
                if let Some(fill) = p.fill() {
                    if let Some(mut paint) = to_paint(fill.paint()) {
                        paint.set_fill_rule(match fill.rule() {
                            usvg::FillRule::NonZero => FillRule::NonZero,
                            usvg::FillRule::EvenOdd => FillRule::EvenOdd,
                        });
                        canvas.set_global_alpha(fill.opacity().get());
                        canvas.fill_path(&path, &paint);
                    }
                }
                if let Some(stroke) = p.stroke() {
                    if let Some(paint) = to_paint(stroke.paint()) {
                        canvas.set_global_alpha(stroke.opacity().get());
                        canvas.stroke_path(&path, &paint.with_line_width(stroke.width().get()));
                    }
                }
                canvas.restore();
            }
            usvg::Node::Text(text) => {
                let runs = if std::env::var_os("TEXT_AS_PATHS").is_some() {
                    None
                } else {
                    fonts.glyph_runs(text)
                };
                let Some(runs) = runs else {
                    draw(canvas, text.flattened(), base, fonts);
                    continue;
                };
                canvas.save();
                canvas.reset_transform();
                canvas.set_transform(&(transform(text.abs_transform()) * base));
                for (span, runs) in text.layouted().iter().zip(runs) {
                    if !span.visible {
                        continue;
                    }
                    let fill = span
                        .fill
                        .as_ref()
                        .and_then(|fill| Some((false, to_paint(fill.paint())?, fill.opacity())));
                    let stroke = span.stroke.as_ref().and_then(|stroke| {
                        let paint = to_paint(stroke.paint())?.with_line_width(stroke.width().get());
                        Some((true, paint, stroke.opacity()))
                    });
                    for (stroked, paint, opacity) in [fill, stroke].into_iter().flatten() {
                        let paint = paint.with_font_size(span.font_size.get());
                        canvas.set_global_alpha(opacity.get());
                        for (font, glyphs) in &runs {
                            let glyphs = glyphs.iter().cloned();
                            if stroked {
                                canvas.stroke_glyph_run(*font, &[], glyphs, &paint).unwrap();
                            } else {
                                canvas.fill_glyph_run(*font, &[], glyphs, &paint).unwrap();
                            }
                        }
                    }
                }
                canvas.restore();
            }
            _ => {}
        }
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
        let out = args[1].clone();
        let scale: f32 = args[2].parse().unwrap();
        // usvg lays text out in the system's fonts, and drops a text when it has none.
        let mut options = usvg::Options::default();
        options.fontdb_mut().load_system_fonts();
        let tree = usvg::Tree::from_data(&std::fs::read(&args[3]).unwrap(), &options).unwrap();
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
        let mut fonts = Fonts {
            context: TextContext::default(),
            fontdb: tree.fontdb().clone(),
            loaded: HashMap::new(),
        };
        let mut canvas = Canvas::new_with_text_context(renderer, fonts.context.clone()).unwrap();
        canvas.set_size(W, H, 1.0);
        let image = canvas
            .create_image_empty(W as usize, H as usize, PixelFormat::Rgba8, ImageFlags::empty())
            .unwrap();
        canvas.set_render_target(RenderTarget::Image(image));
        canvas.clear_rect(0, 0, W, H, Color::white());
        let size = tree.size();
        let fit = (W as f32 / size.width()).min(H as f32 / size.height()) * scale;
        draw(&mut canvas, tree.root(), Transform2D::scaling(fit, fit), &mut fonts);
        canvas.flush_to_output(());
        let shot = canvas.screenshot().unwrap();
        let mut ppm = format!("P6\n{W} {H}\n255\n").into_bytes();
        for p in shot.pixels() {
            ppm.extend_from_slice(&[p.r, p.g, p.b]);
        }
        std::fs::write(&out, ppm).unwrap();
        event_loop.exit();
    }

    fn window_event(&mut self, _: &ActiveEventLoop, _: winit::window::WindowId, _: WindowEvent) {}
}

fn main() {
    let event_loop = EventLoop::new().unwrap();
    event_loop.run_app(&mut App { done: false }).unwrap();
}
