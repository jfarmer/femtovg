#!/bin/zsh
# build.sh TAG [WORKTREE]  - the demo-assets harness built against a femtovg tree with every cfg master has,
# into bin/_logos_full_TAG. Shared release target; sources touched first so a stale library is never linked.
B=/Users/matt/src/femtovg-wt/bin; H=/Users/matt/src/femtovg-wt/da/harness/_logos_full.rs; R=/Users/matt/src/femtovg-wt/runs/pmemo
export CARGO_TARGET_DIR=/Users/matt/src/femtovg-wt/target-prs
tag=$1; wt=${2:-/Users/matt/src/femtovg/.claude/worktrees/exciting-lalande-be708f}
cd $wt || exit 1
cp $H examples/_logos_full.rs; find src -name '*.rs' -exec touch {} +
if cargo rustc --release --example _logos_full --features wgpu -- --cfg harness_clip --cfg harness_turbulence --cfg harness_blend --cfg harness_mix_blend --cfg harness_blur_xy --cfg harness_morph > $R/build_$tag.log 2>&1; then
  cp $CARGO_TARGET_DIR/release/examples/_logos_full $B/_logos_full_$tag && echo "built $tag from $(git rev-parse --short HEAD) $(git status --porcelain -- src | wc -l | tr -d ' ') modified src files $(date +%T)"
else
  echo "BUILD $tag FAILED"; grep -A12 '^error' $R/build_$tag.log | head -40
fi
rm -f examples/_logos_full.rs
