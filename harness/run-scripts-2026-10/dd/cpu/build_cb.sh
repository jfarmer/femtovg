#!/bin/zsh
# build_cb.sh TAG:WORKTREE ... - the lib test binary with cache_bench_test.rs appended to src/path/cache.rs (restored after)
export CARGO_TARGET_DIR=${CARGO_TARGET_DIR:-/Users/matt/src/femtovg-wt/target-dd} CARGO_PROFILE_RELEASE_DEBUG=0
S=/private/tmp/claude-501/-Users-matt-src-femtovg--claude-worktrees-dazzling-margulis-82b624/a9e7c503-7f96-4d2e-a87e-825f0e6c0118/scratchpad
for spec in "$@"; do
  tag=${spec%%:*}; wt=/Users/matt/src/femtovg-wt/${spec##*:}
  cd $wt || exit 1
  cp src/path/cache.rs $S/cache_$tag.rs.orig
  cat /Users/matt/src/femtovg-wt/runs/dd/cpu/cache_bench_test.rs >> src/path/cache.rs; find src -name '*.rs' -exec touch {} +
  out=$(cargo test --release --lib --no-run --message-format=json 2>/Users/matt/src/femtovg-wt/runs/dd/cpu/build_cb_$tag.log | python3 -c "
import sys, json
for l in sys.stdin:
    try: m = json.loads(l)
    except Exception: continue
    if m.get('reason') == 'compiler-artifact' and m.get('executable') and m['target']['name'] == 'femtovg': print(m['executable'])")
  cp $S/cache_$tag.rs.orig src/path/cache.rs
  if [ -n "$out" ]; then cp $out /Users/matt/src/femtovg-wt/bin/_cb_$tag && echo "built _cb_$tag"; else echo "BUILD $tag FAILED"; tail -20 /Users/matt/src/femtovg-wt/runs/dd/cpu/build_cb_$tag.log; fi
done
