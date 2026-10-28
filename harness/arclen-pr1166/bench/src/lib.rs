//! The text-on-path positioning kernel of usvg's `collect_normals` (crates/usvg/src/text/layout.rs),
//! reproduced against kurbo 0.13.1 (resvg's Cargo.lock) so it can be counted on a phone's E-cores.
//! Variants: `plain` = master / unoptimized (curve.inv_arclen), `cached` = PR #1166's second commit
//! (CurveWithLength), `incr` = candidate: ascending offsets resume from the previous glyph.
#![allow(clippy::all)]
use kurbo::{CubicBez, Line, ParamCurve, ParamCurveArclen, ParamCurveDeriv, Point, Vec2};
use std::ffi::{c_char, c_void, CStr, CString};
use std::sync::OnceLock;

// ---- verbatim from Cees-Kettenis/resvg@2acf581 ---------------------------------------------------------
pub struct CurveWithLength {
    pub curve: CubicBez,
    pub cached_length: Option<(f64, f64)>,
}
impl ParamCurve for CurveWithLength {
    fn eval(&self, t: f64) -> Point {
        self.curve.eval(t)
    }
    fn subsegment(&self, range: std::ops::Range<f64>) -> Self {
        Self { curve: self.curve.subsegment(range), cached_length: None }
    }
}
impl ParamCurveArclen for CurveWithLength {
    fn arclen(&self, accuracy: f64) -> f64 {
        match self.cached_length {
            Some((a, l)) if accuracy == a => l,
            _ => self.curve.arclen(accuracy),
        }
    }
}

#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub enum Variant {
    Plain,
    Cached,
    Incr,
}

/// What `collect_normals` does per glyph after solving: eval, deriv, angle. Returns a checksum.
#[inline(always)]
fn normal(curve: &CubicBez, t: f64) -> f64 {
    let pos = curve.eval(t);
    let d = curve.deriv().eval(t);
    let d = Vec2::new(-d.y, d.x);
    let angle = d.atan2().to_degrees() - 90.0;
    (pos.x as f32 as f64) + (pos.y as f32 as f64) + (angle as f32 as f64)
}

/// Candidate: glyph offsets ascend, so resume from the previous glyph: Newton on the arc length
/// measured from the previous point (short pieces), with kurbo's inv_arclen as the safety net.
#[inline(always)]
fn inv_arclen_from(curve: &CubicBez, t0: f64, s0: f64, target: f64, acc: f64) -> Option<(f64, f64)> {
    // target arc length measured from the curve start; s0 = arc length at t0.
    let d = target - s0;
    if d < 0.0 {
        return None;
    }
    let deriv = curve.deriv();
    let mut t = t0;
    let mut piece = 0.0; // arc length from t0 to t
    let inner = acc * 0.25;
    for _ in 0..6 {
        let dp = deriv.eval(t);
        let speed = dp.x.hypot(dp.y);
        if !(speed > 1e-9) {
            return None;
        }
        let err = piece - d;
        if err.abs() <= inner {
            return Some((t, s0 + piece));
        }
        let nt = t - err / speed;
        if !(nt >= t0 && nt <= 1.0) {
            return None;
        }
        t = nt;
        piece = curve.subsegment(t0..t).arclen(inner);
    }
    ((piece - d).abs() <= inner).then_some((t, s0 + piece))
}

pub fn inv_arclen_from_pub(curve: &CubicBez, t0: f64, s0: f64, target: f64, acc: f64) -> Option<(f64, f64)> {
    inv_arclen_from(curve, t0, s0, target, acc)
}

#[inline(never)]
pub fn kernel(variant: Variant, segs: &[CubicBez], offsets: &[f64], acc: f64) -> f64 {
    let mut sum = 0.0;
    let mut n = 0usize; // normals.len()
    let mut length = 0.0f64;
    for curve in segs {
        let curve_len = curve.arclen(acc);
        let measured = CurveWithLength { curve: *curve, cached_length: Some((acc, curve_len)) };
        let mut t_prev = 0.0;
        let mut s_prev = 0.0;
        for offset in &offsets[n..] {
            if *offset >= length && *offset <= length + curve_len {
                let mut t = match variant {
                    Variant::Plain => curve.inv_arclen(offset - length, acc),
                    Variant::Cached => measured.inv_arclen(offset - length, acc),
                    Variant::Incr => {
                        let target = offset - length;
                        match inv_arclen_from(curve, t_prev, s_prev, target, acc) {
                            Some((t, s)) => {
                                t_prev = t;
                                s_prev = s;
                                t
                            }
                            None => {
                                let t = curve.inv_arclen(target, acc);
                                t_prev = t;
                                s_prev = curve.subsegment(0.0..t).arclen(acc * 0.25);
                                t
                            }
                        }
                    }
                };
                t = t.clamp(0.0, 1.0);
                sum += normal(curve, t);
                n += 1;
                if n == offsets.len() {
                    break;
                }
            }
        }
        length += curve_len;
    }
    sum
}

// ---- workloads (the nine of the PR's stress table: 100/500/1000 glyphs x straight/one cubic/32 cubics) ----
pub struct Workload {
    pub name: String,
    pub segs: Vec<CubicBez>,
    pub offsets: Vec<f64>,
}

fn line_cubic(p0: Point, p1: Point) -> CubicBez {
    // usvg: create_curve_from_line (control points at 0.33 and 0.66, so the parameterization is not uniform)
    let line = Line::new(p0, p1);
    CubicBez { p0: line.p0, p1: line.eval(0.33), p2: line.eval(0.66), p3: line.p1 }
}

pub fn workload(kind: &str, glyphs: usize) -> Workload {
    let advance = 9.0; // a 16 px sans glyph
    let run = advance * glyphs as f64;
    let len = run * 1.05;
    let segs: Vec<CubicBez> = match kind {
        "straight" => vec![line_cubic(Point::new(10.0, 300.0), Point::new(10.0 + len, 300.0))],
        "cubic" => {
            // an S curve whose arc length is about 1.05 x the run
            let w = len / 1.25;
            vec![CubicBez::new((10.0, 300.0), (10.0 + 0.3 * w, 300.0 - 0.45 * w), (10.0 + 0.7 * w, 300.0 + 0.45 * w), (10.0 + w, 300.0))]
        }
        "multi" => {
            let n = 32;
            let w = len / 1.1 / n as f64;
            (0..n)
                .map(|i| {
                    let x = 10.0 + i as f64 * w;
                    let s = if i % 2 == 0 { 1.0 } else { -1.0 };
                    CubicBez::new((x, 300.0), (x + 0.33 * w, 300.0 - s * 0.3 * w), (x + 0.66 * w, 300.0 - s * 0.3 * w), (x + w, 300.0))
                })
                .collect()
        }
        _ => panic!("kind"),
    };
    // scale curved shapes so the run fits on the path
    let total: f64 = segs.iter().map(|c| c.arclen(1e-6)).sum();
    let scale = (total / run).min(1.0);
    let _ = scale;
    let offsets = (0..glyphs).map(|i| (i as f64 + 0.5) * advance * (total / (run * 1.05)).min(1.0)).collect();
    Workload { name: format!("{kind}-{glyphs}"), segs, offsets }
}

// ---- counters (the same thread_selfcounts shim as the soak library) ---------------------------------------
type ThscFn = unsafe extern "C" fn(i32, *mut c_void, usize) -> i32;
extern "C" {
    fn dlsym(handle: *mut c_void, symbol: *const c_char) -> *mut c_void;
}
const RTLD_DEFAULT: *mut c_void = -2isize as *mut c_void;

#[derive(Clone, Copy, Default)]
pub struct Counts {
    pub instr: [u64; 2],
    pub cycles: [u64; 2],
}
pub fn thread_counts() -> Counts {
    static F: OnceLock<Option<ThscFn>> = OnceLock::new();
    let f = *F.get_or_init(|| {
        let c = CString::new("thread_selfcounts").unwrap();
        let p = unsafe { dlsym(RTLD_DEFAULT, c.as_ptr()) };
        (!p.is_null()).then(|| unsafe { std::mem::transmute_copy::<*mut c_void, ThscFn>(&p) })
    });
    let Some(f) = f else { return Counts::default() };
    let mut buf = [[0u64; 4]; 4];
    if unsafe { f(4, buf.as_mut_ptr() as *mut c_void, std::mem::size_of_val(&buf)) } != 0 {
        return Counts::default();
    }
    Counts { instr: [buf[0][0], buf[1][0]], cycles: [buf[0][1], buf[1][1]] }
}

static MARKER: OnceLock<extern "C" fn(i32, *const c_char)> = OnceLock::new();
#[no_mangle]
pub extern "C" fn arclen_set_marker(f: extern "C" fn(i32, *const c_char)) {
    let _ = MARKER.set(f);
}
fn mark(begin: bool, name: &str) {
    if let Some(f) = MARKER.get() {
        let c = CString::new(name).unwrap();
        f(begin as i32, c.as_ptr());
    }
}

const VARIANTS: [(Variant, &str, f64); 4] = [
    (Variant::Plain, "plain0.5", 0.5),
    (Variant::Plain, "plain0.001", 0.001),
    (Variant::Cached, "cached0.001", 0.001),
    (Variant::Incr, "incr0.001", 0.001),
];

/// Runs `rounds` rounds; each round runs every (workload, variant) once for `inner` calls, rotating the
/// variant order per round (ABBA-ish), counting each with thread_selfcounts. CSV: workload,variant,round,
/// inner,instr_e,cyc_e,instr_p,cyc_p,checksum. `signposts` != 0 wraps each block in a Points of Interest interval
/// named "<workload>/<variant>".
/// `kinds_csv` like "straight-1000,cubic-1000"; `variants_csv` like "plain0.001,cached0.001" (empty = all).
#[no_mangle]
pub extern "C" fn arclen_bench_run(out_csv: *const c_char, kinds_csv: *const c_char, variants_csv: *const c_char, rounds: u32, inner: u32, signposts: i32) -> i32 {
    let out = unsafe { CStr::from_ptr(out_csv) }.to_string_lossy().into_owned();
    let kinds = unsafe { CStr::from_ptr(kinds_csv) }.to_string_lossy().into_owned();
    let vs = unsafe { CStr::from_ptr(variants_csv) }.to_string_lossy().into_owned();
    let want: Vec<&str> = vs.split(',').filter(|s| !s.is_empty()).collect();
    let vars: Vec<(Variant, &str, f64)> = VARIANTS.iter().copied().filter(|v| want.is_empty() || want.contains(&v.1)).collect();
    let loads: Vec<Workload> = kinds
        .split(',')
        .filter(|s| !s.is_empty())
        .map(|k| {
            let (kind, n) = k.rsplit_once('-').unwrap();
            workload(kind, n.parse().unwrap())
        })
        .collect();
    let mut csv = String::from("workload,variant,round,inner,instr_e,cyc_e,instr_p,cyc_p,checksum\n");
    // warm up: code and the allocator
    for w in &loads {
        for v in &vars {
            for _ in 0..3 {
                std::hint::black_box(kernel(v.0, &w.segs, &w.offsets, v.2));
            }
        }
    }
    for round in 0..rounds as usize {
        for w in &loads {
            for k in 0..vars.len() {
                let v = vars[(k + round) % vars.len()];
                let name = format!("{}-{}/r", w.name, v.1);
                if signposts != 0 {
                    mark(true, &name);
                }
                let c0 = thread_counts();
                let mut acc = 0.0;
                for _ in 0..inner {
                    acc += std::hint::black_box(kernel(v.0, std::hint::black_box(&w.segs), std::hint::black_box(&w.offsets), v.2));
                }
                let c1 = thread_counts();
                if signposts != 0 {
                    mark(false, &name);
                }
                csv += &format!(
                    "{},{},{},{},{},{},{},{},{:.6}\n",
                    w.name, v.1, round, inner,
                    c1.instr[1] - c0.instr[1], c1.cycles[1] - c0.cycles[1],
                    c1.instr[0] - c0.instr[0], c1.cycles[0] - c0.cycles[0], acc / inner as f64
                );
            }
        }
    }
    match std::fs::write(&out, csv) {
        Ok(()) => 0,
        Err(_) => 1,
    }
}
