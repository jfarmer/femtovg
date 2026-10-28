# Shared settings for the phone PMU scripts (zsh).
typeset -A UDID; UDID=(a12 00008020-001C292A2190003A a14 00008101-000A044A3C28801E a13 00008030-0005694926D3402E)
typeset -A TGT; TGT=(m FlatM a FlatA b FlatB c FlatC pp FlatPP pc FlatPC)
APPS=/Users/matt/src/femtovg-wt/runs/phone-pmu/apps
RUNS=/Users/matt/src/femtovg-wt/runs/phone-pmu
TPL=$RUNS/tpl
bundle() { echo co.rbckr.femtovgpmu.flat$1; }
# Waits (up to 15 min) until / has at least 1.5 GB free.
wait_disk() {
  local i a
  for i in $(seq 1 90); do
    a=$(df -k / | tail -1 | awk '{print $4}')
    [ $a -gt 1572864 ] && return 0
    echo "disk low: $((a/1024)) MiB free, waiting" >&2; sleep 10
  done
  echo "disk still low after 15 min" >&2; return 1
}
# Copies Documents/<name> of a variant's app container on a device into <dir>.
fetch() { # dev variant name dir
  xcrun devicectl device copy from --device ${UDID[$1]} --domain-type appDataContainer --domain-identifier $(bundle $2) \
    --source Documents/$3 --destination $4/$3 >/dev/null 2>&1
}
