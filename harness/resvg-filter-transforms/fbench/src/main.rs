//! Filter rendering bench for the E-cores: every SVG in LIST parsed once, then rendered ITERS times at SCALE.
//! Prints one CSV row per file with the render thread's own E/P-core instructions and cycles (thread_selfcounts),
//! wall time and a checksum of the last frame.
//!
//!   fbench LIST SCALE ITERS
use std::ffi::{c_char, c_void, CString};
use std::sync::OnceLock;
use std::time::Instant;

type ThscFn = unsafe extern "C" fn(i32, *mut c_void, usize) -> i32;
unsafe extern "C" {
    fn dlsym(handle: *mut c_void, symbol: *const c_char) -> *mut c_void;
}

#[derive(Clone, Copy, Default)]
struct Counts {
    instr: [u64; 2],
    cycles: [u64; 2],
}

fn counts() -> Counts {
    static F: OnceLock<Option<ThscFn>> = OnceLock::new();
    let f = *F.get_or_init(|| {
        let c = CString::new("thread_selfcounts").unwrap();
        let p = unsafe { dlsym(-2isize as *mut c_void, c.as_ptr()) };
        (!p.is_null()).then(|| unsafe { std::mem::transmute_copy::<*mut c_void, ThscFn>(&p) })
    });
    let Some(f) = f else { return Counts::default() };
    let mut buf = [[0u64; 4]; 4];
    if unsafe { f(4, buf.as_mut_ptr() as *mut c_void, std::mem::size_of_val(&buf)) } != 0 {
        return Counts::default();
    }
    Counts { instr: [buf[0][0], buf[1][0]], cycles: [buf[0][1], buf[1][1]] }
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let list = std::fs::read_to_string(&args[1]).unwrap();
    let scale: f32 = args[2].parse().unwrap();
    let iters: usize = args[3].parse().unwrap();
    let mut fontdb = usvg::fontdb::Database::new();
    if let Ok(dir) = std::env::var("FONTS") {
        fontdb.load_fonts_dir(dir);
    }
    let fontdb = std::sync::Arc::new(fontdb);
    println!("file,instr_p,cycles_p,instr_e,cycles_e,ns,checksum");
    for path in list.lines().filter(|l| !l.is_empty()) {
        let opt = usvg::Options {
            resources_dir: std::path::Path::new(path).parent().map(|p| p.to_owned()),
            fontdb: fontdb.clone(),
            ..usvg::Options::default()
        };
        let Ok(data) = std::fs::read(path) else { continue };
        let Ok(tree) = usvg::Tree::from_data(&data, &opt) else { continue };
        let size = tree.size().to_int_size().scale_by(scale).unwrap();
        let mut pixmap = tiny_skia::Pixmap::new(size.width(), size.height()).unwrap();
        let ts = tiny_skia::Transform::from_scale(scale, scale);
        resvg::render(&tree, ts, &mut pixmap.as_mut());
        let (c0, t0) = (counts(), Instant::now());
        for _ in 0..iters {
            pixmap.fill(tiny_skia::Color::TRANSPARENT);
            resvg::render(&tree, ts, &mut pixmap.as_mut());
        }
        let (c1, ns) = (counts(), t0.elapsed().as_nanos());
        let sum = pixmap.data().iter().fold(0u64, |h, &b| h.wrapping_mul(1_099_511_628_211) ^ b as u64);
        println!(
            "{path},{},{},{},{},{ns},{sum:016x}",
            c1.instr[0] - c0.instr[0],
            c1.cycles[0] - c0.cycles[0],
            c1.instr[1] - c0.instr[1],
            c1.cycles[1] - c0.cycles[1]
        );
    }
}
