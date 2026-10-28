
#[cfg(test)]
mod cache_bench {
    use super::*;
    use crate::Path;

    fn walk(g: &usvg::Group, out: &mut Vec<(Path, Transform2D)>) {
        for node in g.children() {
            match node {
                usvg::Node::Group(g) => walk(g, out),
                usvg::Node::Path(p) => {
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
                    let t = p.abs_transform();
                    out.push((path, Transform2D([t.sx, t.ky, t.kx, t.sy, t.tx, t.ty])));
                }
                _ => {}
            }
        }
    }

    #[test]
    fn cache_bench() {
        let Ok(file) = std::env::var("CB_FILE") else { return };
        let n: usize = std::env::var("CB_N").unwrap().parse().unwrap();
        let tree = usvg::Tree::from_data(&std::fs::read(file).unwrap(), &usvg::Options::default()).unwrap();
        let mut paths = Vec::new();
        walk(tree.root(), &mut paths);
        let fit = (1920.0 / tree.size().width()).min(1080.0 / tree.size().height());
        let tol: f32 = std::env::var("CB_TOL").ok().and_then(|v| v.parse().ok()).unwrap_or(0.25);
        let mut points = 0;
        for _ in 0..n {
            for (path, t) in &paths {
                let mut m = Transform2D::scaling(fit, fit);
                m.premultiply(t);
                let cache = PathCache::new(path.verbs(), &m, tol, 0.01);
                points += std::hint::black_box(cache.points.len());
            }
        }
        eprintln!("CB points/iter {}", points / n.max(1));
    }
}
