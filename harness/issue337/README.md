# Issue #337's inventory (2026-10-18)

What is left of femtovg/femtovg#337 once #403 and #408 merge, measured with `s48` = master ad762cd5 + #408 (ed93d4a5)
+ #403 (59fbefb9), built by `../build.sh s48:<checkout>`.

- `busey_score.py`: BuseyBench (27 files, `accuracy.py s48 group=buseybench framings=z1,hd png=busey_png` with
  `CORPUS_RUN_OUT=runs/thin`) against Chromium 131, Firefox 159, WebKit (macOS 27.2) and the 8x area reference: mean
  px > 20/255 and structural share, with the browsers' envelopes (`busey_score.json`).
- `fail_score.py`: the 23 reftest pairs (groups 01-22, `../corpus_run/wpt22_report.py`-style self-reftests) that s48
  draws more than 0.15 % off Chromium, against each browser and each browser against the suite's reference
  (`fail_score.json`; Firefox and WebKit references made for those pairs with `refs.py firefox` / `refs_webkit.py`
  `keys=`).
- `sheet337.py`: `../../issue337-remaining.png`, s48 | Chromium | Firefox | WebKit | s48 vs Chromium.
