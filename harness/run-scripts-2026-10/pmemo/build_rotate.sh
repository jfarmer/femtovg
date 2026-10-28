#!/bin/zsh
# build_rotate.sh TAG  - pm_rotate.rs built against the worktree as it stands, into bin/pm_rotate_TAG.
B=/Users/matt/src/femtovg-wt/bin; R=/Users/matt/src/femtovg-wt/runs/pmemo
export CARGO_TARGET_DIR=/Users/matt/src/femtovg-wt/target-prs
cd /Users/matt/src/femtovg/.claude/worktrees/exciting-lalande-be708f || exit 1
cp $R/pm_rotate.rs examples/_pm_rotate.rs; find src -name '*.rs' -exec touch {} +
if cargo build --release --example _pm_rotate --features wgpu > $R/build_rotate_$1.log 2>&1; then
  cp $CARGO_TARGET_DIR/release/examples/_pm_rotate $B/pm_rotate_$1 && echo "built pm_rotate_$1 $(git status --porcelain -- src | wc -l | tr -d ' ') modified src files"
else
  echo "BUILD FAILED"; grep -A12 '^error' $R/build_rotate_$1.log | head -40
fi
rm -f examples/_pm_rotate.rs
