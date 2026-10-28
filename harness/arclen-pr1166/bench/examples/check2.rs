use arclen_bench::*;
use kurbo::{CubicBez, ParamCurve, ParamCurveArclen, Point};
use std::cell::Cell;
struct Cnt<'a> { curve: CubicBez, n: &'a Cell<u64> }
impl<'a> ParamCurve for Cnt<'a> {
    fn eval(&self, t: f64) -> Point { self.curve.eval(t) }
    fn subsegment(&self, r: std::ops::Range<f64>) -> Self { Cnt { curve: self.curve.subsegment(r), n: self.n } }
}
impl<'a> ParamCurveArclen for Cnt<'a> {
    fn arclen(&self, a: f64) -> f64 { self.n.set(self.n.get() + 1); self.curve.arclen(a) }
}
/// position of each glyph for the kernel's variants, to compare against kurbo's solve at 1e-9
fn positions(variant: Variant, w: &Workload, acc: f64) -> Vec<Point> {
    let mut out = Vec::new();
    let mut n = 0usize; let mut length = 0.0;
    for curve in &w.segs {
        let len = curve.arclen(acc);
        let (mut tp, mut sp, mut since) = (0.0, 0.0, 0);
        for off in &w.offsets[n..] {
            if *off >= length && *off <= length + len {
                let target = off - length;
                let t = match variant {
                    Variant::Incr => match arclen_bench::inv_arclen_from_pub(curve, tp, sp, target, acc) {
                        Some((t, s)) => { tp = t; sp = s; since += 1; if since >= 16 { sp = curve.subsegment(0.0..t).arclen(acc * 0.25); since = 0; } t }
                        None => { let t = curve.inv_arclen(target, acc); tp = t; sp = curve.subsegment(0.0..t).arclen(acc * 0.25); t }
                    },
                    _ => curve.inv_arclen(target, acc),
                };
                out.push(curve.eval(t.clamp(0.0, 1.0)));
                n += 1; if n == w.offsets.len() { break; }
            }
        }
        length += len;
    }
    out
}
fn main() {
    println!("{:14} {:>12} {:>12}   position error vs kurbo at 1e-9: max / mean (user units)", "workload", "arclen/glyph", "(0.001)");
    for name in ["straight-100", "straight-500", "straight-1000", "cubic-100", "cubic-500", "cubic-1000", "multi-100", "multi-500", "multi-1000"] {
        let (kind, n) = name.rsplit_once('-').unwrap();
        let w = workload(kind, n.parse().unwrap());
        // calls: plain
        let cnt = Cell::new(0u64);
        let mut calls_plain = 0.0; let mut calls_cached = 0.0;
        {
            let mut ng = 0usize; let mut length = 0.0;
            for c in &w.segs {
                let len = c.arclen(0.001);
                for off in &w.offsets[ng..] {
                    if *off >= length && *off <= length + len {
                        let k = Cnt { curve: *c, n: &cnt };
                        cnt.set(0); let _ = k.inv_arclen(off - length, 0.001);
                        calls_plain += cnt.get() as f64; calls_cached += (cnt.get() - 1) as f64; ng += 1;
                        if ng == w.offsets.len() { break; }
                    }
                }
                length += len;
            }
        }
        let g = w.offsets.len() as f64;
        let reference = positions(Variant::Plain, &w, 1e-9);
        let mut line = format!("{name:14} {:12.1} {:>12.1}   ", calls_plain / g, calls_cached / g);
        for (label, v, acc) in [("0.5", Variant::Plain, 0.5), ("0.001", Variant::Plain, 0.001), ("incr", Variant::Incr, 0.001)] {
            let p = positions(v, &w, acc);
            let errs: Vec<f64> = p.iter().zip(&reference).map(|(a, b)| (*a - *b).hypot()).collect();
            let max = errs.iter().cloned().fold(0.0, f64::max); let mean = errs.iter().sum::<f64>() / errs.len() as f64;
            line += &format!("{label}: {max:.4}/{mean:.4}  ");
        }
        println!("{line}");
    }
}
