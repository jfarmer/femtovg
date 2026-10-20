#!/bin/zsh
# build_gl.sh TAG:WORKTREE ...  - the OpenGL fill bench and clip check built against each worktree, into
# bin/gl_fill_bench_TAG and bin/gl_clip_check_TAG. Sources touched first so a stale library is never linked.
B=/Users/matt/src/femtovg-wt/bin; G=/Users/matt/src/femtovg-wt/da/harness/clip-bench; R=/Users/matt/src/femtovg-wt/runs/pr
export CARGO_TARGET_DIR=/Users/matt/src/femtovg-wt/target-prs
for spec in "$@"; do
  tag=${spec%%:*}; wt=/Users/matt/src/femtovg-wt/${spec##*:}
  cd $wt || exit 1
  find src -name '*.rs' -exec touch {} +
  for ex in gl_fill_bench gl_clip_check ${=EXTRA_EXAMPLES}; do
    cp $G/$ex.rs examples/$ex.rs
    if cargo build --release --example $ex > $R/build_gl_${ex}_$tag.log 2>&1; then
      cp $CARGO_TARGET_DIR/release/examples/$ex $B/${ex}_$tag && echo "built $ex $tag from $(git rev-parse --short HEAD)"
    else
      echo "BUILD $ex $tag FAILED"; grep -A12 '^error' $R/build_gl_${ex}_$tag.log | head -30
    fi
    rm -f examples/$ex.rs
  done
done
echo GL_BUILDS_DONE
