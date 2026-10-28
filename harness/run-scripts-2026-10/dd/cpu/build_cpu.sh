#!/bin/zsh
# build_cpu.sh TAG:WORKTREE ... - the Void-canvas path bench against each worktree, into bin/_path_cpu_TAG
export CARGO_TARGET_DIR=${CARGO_TARGET_DIR:-/Users/matt/src/femtovg-wt/target-dd} CARGO_PROFILE_RELEASE_DEBUG=0
for spec in "$@"; do
  tag=${spec%%:*}; wt=/Users/matt/src/femtovg-wt/${spec##*:}
  cd $wt || exit 1
  cp /Users/matt/src/femtovg-wt/runs/dd/cpu/_path_cpu.rs examples/_path_cpu.rs; find src -name '*.rs' -exec touch {} +
  if cargo build --release --example _path_cpu > /Users/matt/src/femtovg-wt/runs/dd/cpu/build_$tag.log 2>&1; then
    cp $CARGO_TARGET_DIR/release/examples/_path_cpu /Users/matt/src/femtovg-wt/bin/_path_cpu_$tag && echo "built $tag from $(git rev-parse --short HEAD)"
  else echo "BUILD $tag FAILED"; grep -A12 '^error' /Users/matt/src/femtovg-wt/runs/dd/cpu/build_$tag.log | head -30; fi
  rm -f examples/_path_cpu.rs
done
