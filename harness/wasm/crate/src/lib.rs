//! The corpus harness for wasm32: `harness/_logos_full.rs` (see build.rs)
//! with a page-facing entry in `web`.
#![allow(
    unexpected_cfgs,
    dead_code,
    unused_imports,
    unused_variables,
    unused_mut,
    unused_macros,
    unused_assignments
)]

/// The harness reads its switches from the environment; on wasm the page
/// sets them before each frame.
mod env_shim {
    use std::cell::RefCell;
    use std::collections::HashMap;

    thread_local! {
        static ENV: RefCell<HashMap<String, String>> = RefCell::new(HashMap::new());
    }

    pub fn set(key: &str, value: &str) {
        ENV.with(|e| {
            e.borrow_mut().insert(key.to_owned(), value.to_owned());
        });
    }

    pub fn clear() {
        ENV.with(|e| e.borrow_mut().clear());
    }

    pub fn var<K: AsRef<std::ffi::OsStr>>(key: K) -> Result<String, std::env::VarError> {
        let key = key.as_ref().to_str().unwrap_or("");
        ENV.with(|e| e.borrow().get(key).cloned())
            .ok_or(std::env::VarError::NotPresent)
    }

    pub fn var_os<K: AsRef<std::ffi::OsStr>>(key: K) -> Option<std::ffi::OsString> {
        var(key).ok().map(Into::into)
    }
}

include!(concat!(env!("OUT_DIR"), "/logos.rs"));

mod web;
