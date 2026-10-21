use std::ffi::{c_char, c_void, CString};
type ThscFn = unsafe extern "C" fn(i32, *mut c_void, usize) -> i32;
unsafe extern "C" { fn dlsym(h: *mut c_void, s: *const c_char) -> *mut c_void; }
fn counts() -> (u64, u64) {
    let c = CString::new("thread_selfcounts").unwrap();
    let p = unsafe { dlsym(-2isize as *mut c_void, c.as_ptr()) };
    let f: ThscFn = unsafe { std::mem::transmute_copy(&p) };
    let mut buf = [[0u64; 4]; 4];
    unsafe { f(4, buf.as_mut_ptr() as *mut c_void, std::mem::size_of_val(&buf)) };
    (buf[1][0], buf[1][1])
}
fn svg(glyphs: usize, kind: &str) -> String {
    let words = "Sphinx of black quartz judge my vow The quick brown fox jumps over the lazy dog ";
    let text: String = words.chars().cycle().take(glyphs).collect();
    let d = match kind {
        "straight" => "M10 300 L 14000 300".to_string(),
        _ => "M10 300 C 4000 -600 8000 1200 14000 300".to_string(),
    };
    format!(r##"<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="14100" height="700"><defs><path id="p" d="{d}"/></defs><text font-family="Noto Sans" font-size="16"><textPath xlink:href="#p">{text}</textPath></text></svg>"##)
}
fn glyphs_of(tree: &usvg::Tree) -> Vec<(f32, f32, f32, f32)> {
    let usvg::Node::Text(t) = &tree.root().children()[0] else { panic!() };
    t.layouted().iter().flat_map(|s| s.positioned_glyphs.iter().map(|g| { let m = g.transform(); (m.tx, m.ty, m.sx, m.kx) })).collect()
}
fn main() {
    let a: Vec<String> = std::env::args().collect();
    let glyphs: usize = a.get(1).map(|s| s.parse().unwrap()).unwrap_or(1000);
    let kind = a.get(2).map(|s| s.as_str()).unwrap_or("straight");
    let reps: usize = a.get(3).map(|s| s.parse().unwrap()).unwrap_or(30);
    let mut opt = usvg::Options::default();
    opt.fontdb_mut().load_fonts_dir(env!("CARGO_MANIFEST_DIR").to_string() + "/../resvg/tests/fonts");
    let text = svg(glyphs, kind);
    {
        let mut all = vec![];
        for &i in &[0u8, 1, 2, 3] { usvg::__set_arc_variant(i); all.push(glyphs_of(&usvg::Tree::from_str(&text, &opt).unwrap())); }
        for (j, label) in [(1usize, "cached"), (2, "resume"), (3, "plain0.5")] {
            let (mut mp, mut mr) = (0f32, 0f32);
            for (a, b) in all[0].iter().zip(&all[j]) { mp = mp.max((a.0 - b.0).hypot(a.1 - b.1)); mr = mr.max((a.2 - b.2).abs().max((a.3 - b.3).abs())); }
            println!("{kind}-{glyphs}: {} glyphs; {label} vs plain0.001: max position diff {mp:.5}, max rotation-matrix diff {mr:.6}", all[0].len());
        }
    }
    let names = ["plain0.001", "cached0.001", "resume0.001", "plain0.5"];
    let ids = [0u8, 1, 2, 3];
    let nv = 4;
    let mut res: Vec<Vec<(u64, u64)>> = vec![vec![]; nv];
    for _ in 0..3 { for &i in &ids { usvg::__set_arc_variant(i); std::hint::black_box(usvg::Tree::from_str(&text, &opt).unwrap()); } }
    for r in 0..reps {
        for k in 0..nv {
            let j = (k + r) % nv;
            usvg::__set_arc_variant(ids[j]);
            let c0 = counts();
            let tree = usvg::Tree::from_str(&text, &opt).unwrap();
            let c1 = counts();
            std::hint::black_box(&tree);
            res[j].push((c1.0 - c0.0, c1.1 - c0.1));
        }
    }
    let med = |v: &Vec<(u64, u64)>, f: fn(&(u64, u64)) -> u64| { let mut x: Vec<u64> = v.iter().map(f).collect(); x.sort(); (x[x.len() / 2], x[0], x[x.len() - 1]) };
    for j in 0..nv {
        let (i, imin, imax) = med(&res[j], |x| x.0);
        let (c, cmin, cmax) = med(&res[j], |x| x.1);
        println!("{kind}-{glyphs} {:12} from_str instr median {:>11} (min {} max {})  cycles median {:>11} (min {} max {})", names[j], i, imin, imax, c, cmin, cmax);
    }
}
