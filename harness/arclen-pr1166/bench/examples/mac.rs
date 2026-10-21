use std::ffi::CString;
fn main() {
    let a: Vec<String> = std::env::args().collect();
    let out = CString::new(a[1].clone()).unwrap();
    let kinds = CString::new(a[2].clone()).unwrap();
    let vars = CString::new(a.get(3).cloned().unwrap_or_default()).unwrap();
    let rounds: u32 = a.get(4).map(|s| s.parse().unwrap()).unwrap_or(20);
    let inner: u32 = a.get(5).map(|s| s.parse().unwrap()).unwrap_or(20);
    std::process::exit(arclen_bench::arclen_bench_run(out.as_ptr(), kinds.as_ptr(), vars.as_ptr(), rounds, inner, 0));
}
