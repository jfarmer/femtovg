#!/bin/zsh
# Tries a launch every 2 minutes for an hour; when the TV is awake, runs round 4.
U=00008110-00015D380283801E
for i in $(seq 1 30); do
  r=$(DEVICECTL_CHILD_SOAK_TAG=wake DEVICECTL_CHILD_SOAK_PHASES=none DEVICECTL_CHILD_SOAK_EXIT=1 xcrun devicectl device process launch --terminate-existing --device $U co.rbckr.femtovgpmu.flatpc 2>&1 | grep -cE "Launched application")
  if [ "$r" = "1" ]; then echo "awake at $(date)"; sleep 5; zsh /Users/matt/src/femtovg-wt/runs/raster/tv/round5.sh; exit 0; fi
  echo "asleep at $(date)"; sleep 120
done
echo "gave up at $(date)"
