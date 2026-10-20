//! CPU-only path cost: every path of an SVG rebuilt, filled and stroked into a Void canvas, FRAMES times.
//!   _path_cpu FILE [SCALE]   (FRAMES env, default 1; POINTS=1 prints nothing extra)
use femtovg::{renderer::Void, Canvas, Color, LineCap, LineJoin, Paint, Path, Transform2D};

fn walk(g: &usvg::Group, out: &mut Vec<usvg::Path>) {
    for node in g.children() {
        match node {
            usvg::Node::Group(g) => walk(g, out),
            usvg::Node::Path(p) => out.push((**p).clone()),
            _ => {}
        }
    }
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let data = std::fs::read(&args[1]).unwrap();
    let tree = usvg::Tree::from_data(&data, &usvg::Options::default()).unwrap();
    let zoom: f32 = args.get(2).and_then(|s| s.parse().ok()).unwrap_or(1.0);
    let frames: usize = std::env::var("FRAMES").ok().and_then(|v| v.parse().ok()).unwrap_or(1);
    let mut paths = Vec::new();
    walk(tree.root(), &mut paths);
    let size = tree.size();
    let fit = (1920.0 / size.width()).min(1080.0 / size.height()) * zoom;
    let mut canvas = Canvas::new(Void).unwrap();
    canvas.set_size(1920, 1080, 1.0);
    for _ in 0..frames {
        for p in &paths {
            let mut path = Path::new();
            for seg in p.data().segments() {
                match seg {
                    usvg::tiny_skia_path::PathSegment::MoveTo(q) => path.move_to(q.x, q.y),
                    usvg::tiny_skia_path::PathSegment::LineTo(q) => path.line_to(q.x, q.y),
                    usvg::tiny_skia_path::PathSegment::CubicTo(a, b, q) => path.bezier_to(a.x, a.y, b.x, b.y, q.x, q.y),
                    usvg::tiny_skia_path::PathSegment::QuadTo(a, q) => path.quad_to(a.x, a.y, q.x, q.y),
                    usvg::tiny_skia_path::PathSegment::Close => path.close(),
                }
            }
            canvas.save();
            canvas.scale(fit, fit);
            let t = p.abs_transform();
            canvas.set_transform(&Transform2D([t.sx, t.ky, t.kx, t.sy, t.tx, t.ty]));
            if p.fill().is_some() {
                canvas.fill_path(&path, &Paint::color(Color::rgb(10, 20, 30)));
            }
            if let Some(s) = p.stroke() {
                let mut paint = Paint::color(Color::rgb(30, 20, 10));
                paint.set_line_width(s.width().get());
                paint.set_miter_limit(s.miterlimit().get());
                paint.set_line_join(match s.linejoin() {
                    usvg::LineJoin::Round => LineJoin::Round,
                    usvg::LineJoin::Bevel => LineJoin::Bevel,
                    _ => LineJoin::Miter,
                });
                paint.set_line_cap(match s.linecap() {
                    usvg::LineCap::Round => LineCap::Round,
                    usvg::LineCap::Square => LineCap::Square,
                    _ => LineCap::Butt,
                });
                canvas.stroke_path(&path, &paint);
            }
            canvas.restore();
        }
        canvas.flush_to_output(());
    }
}
