# femtovg plus-lighter + usvg 0.49

Evidence for the femtovg PR that moves to usvg 0.49 and adds `BlendMode::PlusLighter` (femtovg#379).

Builds (harness/build.sh): `b48` upstream master 1bca261c (usvg 0.48), `b49` the same with usvg 0.49 only, `bpl`
the branch `plus-lighter`, `bpl2` the branch with this harness's `feComposite operator="lighter"` mapping (a flood or
noise chain ending in a lighter composite with the source graphic runs as the blend pass's plus-lighter).

- `strip_chr.png`: master | plus-lighter | Chromium 131 | differences, the WPT plus-lighter test and resvg 0.49's two
  new lighter tests (corpus/resvg-lighter) at z1.
- `strip.png`: the same with WebKit, and resvg's `feBlend mode="plus-lighter"` test, which usvg (as Chromium) reads as
  `normal`; WebKit applies plus-lighter there.
- Identity sweeps (corpus_run/identity.py, 2,215 files x 16 framings): see `identity.md`.
- GL: `clip-bench/gl_plus_lighter_check.rs` passes on the branch, and fails with the GLSL mode-16 line removed.
