use arclen_bench::*;
fn main() {
    for name in ["straight-1000", "cubic-1000", "multi-1000", "straight-100", "cubic-100", "multi-100", "straight-500", "cubic-500", "multi-500"] {
        let (kind, n) = name.rsplit_once('-').unwrap();
        let w = workload(kind, n.parse().unwrap());
        let total: f64 = w.segs.iter().map(|c| kurbo::ParamCurveArclen::arclen(c, 1e-6)).sum();
        let last = *w.offsets.last().unwrap();
        let p = kernel(Variant::Plain, &w.segs, &w.offsets, 0.001);
        let c = kernel(Variant::Cached, &w.segs, &w.offsets, 0.001);
        let i = kernel(Variant::Incr, &w.segs, &w.offsets, 0.001);
        let p5 = kernel(Variant::Plain, &w.segs, &w.offsets, 0.5);
        println!("{name}: path {total:.1} last offset {last:.1}  plain==cached {} incr-plain {:.3e} plain0.5-plain {:.3e}", p == c, (i - p).abs() / w.offsets.len() as f64, (p5 - p).abs() / w.offsets.len() as f64);
    }
}
