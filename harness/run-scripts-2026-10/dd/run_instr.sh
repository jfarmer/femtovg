#!/bin/zsh
cd /Users/matt/src/femtovg-wt/runs/dd
W=/Users/matt/src/femtovg-wt
REPEATS=5 python3 tool.py instr.py m8 rv -- /Users/matt/src/femtovg-pmu/corpus/Ghostscript_Tiger.svg $W/da/corpus/firefox/puzzle-fox.svg $W/da/harness/clip-bench/cards_none_200.svg $W/da/harness/clip-bench/cards_rounded_200.svg $W/da/harness/clip-bench/cards_circle_200.svg $W/da/mr-settodefault.svg
echo "-- FRAMING=z1 (frames with merges)"
FRAMING=z1 REPEATS=5 python3 tool.py instr.py m8 rv -- $W/da/corpus/firefox/puzzle-fox.svg $W/da/mr-settodefault.svg "$W/da/corpus/firefox-com/btn-app-store.1cfd5dba4a92.svg"
echo INSTR_DONE
