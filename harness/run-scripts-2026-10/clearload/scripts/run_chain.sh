#!/bin/zsh
# Runs run_abba.sh on each device in turn (one recording at a time per chain).
# usage: run_chain.sh round dev...
R=$1; shift
for d in "$@"; do /Users/matt/src/femtovg-wt/runs/clearload/scripts/run_abba.sh $d $R; done
echo "chain $* done"
