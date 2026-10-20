# A clip mask over a self-crossing path (zoom ladder)

Probes, scripts and numbers for the issue: femtovg's coverage mask sums a pixel's winding before the fill rule folds
it, so a pixel of a self-crossing contour that holds windings 0, 1 and 2 comes out over-covered. Master is femtovg
06243b80, a harness built from it with all cfgs; its frames of `multiple-children.svg` are bit-identical to the zoom
ladder's at all eleven zooms.

| file | what |
|---|---|
| `multiple-children.svg` | `resvg-clippath-multiple-children.svg` from the wpt22 SVG reftests: an even-odd pentagram and a circle as one clipPath |
| `multiple-children-uncrossed.svg` | the sheet's after: the same region without crossings (the 10-gon outline and the inner pentagon wound against it, nonzero); equivalent geometry, not a fix |
| `repro.svg`, `repro-nonzero.svg` | the pentagram clip alone, under even-odd and under nonzero |
| `render.sh` | renders SVGs at the ladder's zooms in its framing (a 200 px box centred in 460 x 260) |
| `measure.py` -> `numbers.txt`, `numbers.json` | each pixel against the exact area (supersampled) and against the fold of `a1 + 2 a2`; the corpus file against WebKit, split into inner vertices, frame corners and the rest |
| `model.py` -> `model.txt` | a model of `Coverage::resolve` (reproduces master's frames of both repros to 1/255) and three ways of folding below a pixel |
| `make_sheet.py` | the five-column sheet |

```
./render.sh BIN png multiple-children.svg multiple-children-uncrossed.svg repro.svg repro-nonzero.svg
python3 measure.py png REFS AREA numbers.json > numbers.txt   # REFS: the ladder's browser frames, AREA: the 8x area references
python3 model.py png > model.txt
python3 make_sheet.py png REFS AREA sheet.png
cd harness/corpus_run && python3 zoom_strip.py strip.gif key=wpt22__20-clippath-unions-and-masks__resvg-clippath-multiple-children \
    build=zm panels=femtovg,wk,diff_wk crop=148,50,164,160 scale=2 label=multiple-children
```
