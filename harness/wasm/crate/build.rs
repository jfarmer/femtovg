//! The corpus harness (`harness/_logos_full.rs`) as this crate's body: its
//! crate attributes dropped (lib.rs sets its own) and its environment reads
//! routed through `env_shim`, which the page fills per frame. Nothing else in
//! the harness changes, so a frame here is drawn by the same code as natively.
use std::{env, fs, path::Path};

fn main() {
    let src = env::var("LOGOS_SRC").expect("LOGOS_SRC: the path of harness/_logos_full.rs");
    println!("cargo:rerun-if-changed={src}");
    println!("cargo:rerun-if-env-changed=LOGOS_SRC");
    let text = fs::read_to_string(&src).unwrap();
    let mut out = String::with_capacity(text.len());
    for line in text.lines() {
        let trimmed = line.trim_start();
        if trimmed.starts_with("#![") {
            continue;
        }
        // The file's own doc comment is an inner one, which an included file cannot have.
        if let Some(rest) = trimmed.strip_prefix("//!") {
            out.push_str("//");
            out.push_str(rest);
        } else {
            out.push_str(line);
        }
        out.push('\n');
    }
    let out = out
        .replace("std::env::var_os(", "crate::env_shim::var_os(")
        .replace("std::env::var(", "crate::env_shim::var(");
    fs::write(Path::new(&env::var("OUT_DIR").unwrap()).join("logos.rs"), out).unwrap();
}
