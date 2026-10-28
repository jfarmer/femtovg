#!/usr/bin/env python3
"""add_bench.py WORKTREE OLD_REV : adds the scratch rasterizer benchmark to a femtovg worktree (not for commit):
src/clip/coverage_old.rs (OLD_REV's rasterizer), MaskKey::dump/undump and the ignored test zz_raster_bench in
src/clip/mask.rs. RASTER_BENCH=dump RASTER_ITERS=n [RASTER_IMPL=old] [RASTER_OUT=file] [RASTER_HASHES=file]; it
prints the thread's exact instructions and cycles a pass per CPU kind (thread_selfcounts). Undo with
`git checkout -- src/clip.rs src/clip/mask.rs && rm src/clip/coverage_old.rs`."""
import subprocess, sys

wt, old_rev = sys.argv[1], sys.argv[2]
old = subprocess.run(['git', '-C', wt, 'show', f'{old_rev}:src/clip/coverage.rs'], capture_output=True, text=True,
                     check=True).stdout
old = old[:old.index('#[cfg(test)]\nmod tests')]
open(f'{wt}/src/clip/coverage_old.rs', 'w').write(
    '#![allow(dead_code)]\n// Scratch (not for commit): the rasterizer of ' + old_rev + ', for the bench.\n' + old)

p = f'{wt}/src/clip.rs'
s = open(p).read()
s = s.replace('mod coverage;\n', 'mod coverage;\n#[cfg(test)]\nmod coverage_old;\n', 1)
open(p, 'w').write(s)

p = f'{wt}/src/clip/mask.rs'
s = open(p).read()
anchor = '    /// Rasterizes the outline the key was made of'
s = s.replace(anchor, '''    /// The key as bytes: width, height, word count and words, little-endian.
    pub(crate) fn dump(&self) -> Vec<u8> {
        let mut out = Vec::new();
        for v in [self.size[0], self.size[1], self.outline.len() as u32] {
            out.extend(v.to_le_bytes());
        }
        for w in &self.outline {
            out.extend(w.to_le_bytes());
        }
        out
    }

    /// A key read back from `dump`'s bytes, and the bytes after it.
    pub(crate) fn undump(bytes: &[u8]) -> Option<(Self, &[u8])> {
        let word = |i: usize| bytes.get(4 * i..4 * i + 4).map(|b| u32::from_le_bytes(b.try_into().unwrap()));
        let (w, h, n) = (word(0)?, word(1)?, word(2)? as usize);
        let outline = (0..n).map(|i| word(3 + i).map(|v| v as i32)).collect::<Option<Vec<_>>>()?;
        Some((Self { size: [w, h], parent: None, outline }, &bytes[4 * (3 + n)..]))
    }

''' + anchor, 1)
bench = r'''
    /// Scratch benchmark (not for commit), see runs/raster/add_bench.py.
    #[test]
    #[ignore]
    fn zz_raster_bench() {
        let Ok(path) = std::env::var("RASTER_BENCH") else {
            return;
        };
        let bytes = std::fs::read(path).unwrap();
        let mut keys = Vec::new();
        let mut rest = &bytes[..];
        while let Some((key, r)) = MaskKey::undump(rest) {
            keys.push(key);
            rest = r;
        }
        let old_impl = std::env::var("RASTER_IMPL").as_deref() == Ok("old");
        let mut coverage = Coverage::default();
        let mut old_coverage = super::super::coverage_old::Coverage::default();
        let rasterize_old = |key: &MaskKey, coverage: &mut super::super::coverage_old::Coverage, mask: &mut Vec<u8>| {
            let [width, height] = key.size();
            mask.truncate(width * height);
            mask.fill(0);
            mask.resize(width * height, 0);
            coverage.reset(width, height);
            let mut contour = Vec::new();
            let mut words = key.outline.iter().copied();
            while let (Some(rule), Some(contours)) = (words.next(), words.next()) {
                for _ in 0..contours {
                    let points = words.next().unwrap_or(0);
                    contour.clear();
                    for _ in 0..points {
                        if let (Some(x), Some(y)) = (words.next(), words.next()) {
                            contour.push([x as f32 / SUBPIXELS, y as f32 / SUBPIXELS]);
                        }
                    }
                    coverage.contour(&contour);
                }
                let rule = if rule == 0 { FillRule::NonZero } else { FillRule::EvenOdd };
                coverage.resolve(rule, mask);
            }
        };
        let mut run = |key: &MaskKey, out: &mut Vec<u8>| {
            if old_impl {
                rasterize_old(key, &mut old_coverage, out);
            } else {
                key.rasterize_into(&mut coverage, out);
            }
        };
        let mut scratch = Vec::new();
        let mut all = Vec::new();
        for key in &keys {
            run(key, &mut scratch);
            all.extend_from_slice(&scratch);
        }
        if let Ok(out) = std::env::var("RASTER_OUT") {
            std::fs::write(out, &all).unwrap();
        }
        extern "C" {
            fn dlsym(handle: *mut std::ffi::c_void, symbol: *const std::ffi::c_char) -> *mut std::ffi::c_void;
        }
        type Thsc = unsafe extern "C" fn(i32, *mut std::ffi::c_void, usize) -> i32;
        let thsc = unsafe { dlsym(-2isize as *mut _, c"thread_selfcounts".as_ptr()) };
        let counts = || -> [[u64; 4]; 4] {
            let mut buf = [[0u64; 4]; 4];
            if !thsc.is_null() {
                let f: Thsc = unsafe { std::mem::transmute(thsc) };
                unsafe { f(4, buf.as_mut_ptr() as *mut _, std::mem::size_of_val(&buf)) };
            }
            buf
        };
        let iters: usize = std::env::var("RASTER_ITERS").ok().and_then(|v| v.parse().ok()).unwrap_or(100);
        let c0 = counts();
        let started = std::time::Instant::now();
        for _ in 0..iters {
            for key in &keys {
                run(key, &mut scratch);
                std::hint::black_box(&scratch);
            }
        }
        let ns = started.elapsed().as_nanos() as f64 / iters as f64;
        let c1 = counts();
        let per = |kind: usize, i: usize| (c1[kind][i] - c0[kind][i]) as f64 / iters as f64 / 1e6;
        let area: usize = keys.iter().map(|k| k.size()[0] * k.size()[1]).sum();
        eprintln!(
            "RASTER {} masks, {} px: {:.1} us a pass",
            keys.len(),
            area,
            ns / 1e3
        );
        eprintln!(
            "RASTER COUNTS a pass: E {:.3} M instr {:.3} M cycles, P {:.3} M instr {:.3} M cycles",
            per(1, 0),
            per(1, 1),
            per(0, 0),
            per(0, 1)
        );
    }
}
'''
i = s.rindex('}')
s = s[:i].rstrip() + '\n' + bench
open(p, 'w').write(s)
print('bench added to', wt)
