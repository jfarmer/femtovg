import re
src = open('/Users/matt/src/femtovg-wt/da/corpus/buseybench/mistral-large-4.svg').read()
D = '/Users/matt/src/femtovg-wt/runs/busey/triage/mistral-large-4/svg/'
fillL = '<path d="M350 404 C382 360 455 348 512 382 C470 372 410 382 366 424 C356 418 352 412 350 404 Z" fill="#3a2418"/>'
fillR = '<path d="M674 404 C642 360 569 348 512 382 C554 372 614 382 658 424 C668 418 672 412 674 404 Z" fill="#3a2418"/>'
strokes = ['<path d="M356 398 C398 366 462 362 506 388" fill="none" stroke="#6b4a2c" stroke-width="13" stroke-linecap="round"/>',
           '<path d="M668 398 C626 366 562 362 518 388" fill="none" stroke="#6b4a2c" stroke-width="13" stroke-linecap="round"/>']
for x in [fillL, fillR] + strokes:
    assert x in src, x
open(D + 'm_nobrowfill.svg', 'w').write(src.replace(fillL, '').replace(fillR, ''))
open(D + 'm_nobrowfillR.svg', 'w').write(src.replace(fillR, ''))
open(D + 'm_nobrowstroke.svg', 'w').write(src.replace(strokes[0], '').replace(strokes[1], ''))
head = '<svg width="1024" height="1024" viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg"><rect width="1024" height="1024" fill="#e8b890"/>'
open(D + 'r_brows.svg', 'w').write(head + fillL + fillR + strokes[0] + strokes[1] + '</svg>')
open(D + 'r_browfills.svg', 'w').write(head + fillL + fillR + '</svg>')
open(D + 'r_browfillL.svg', 'w').write(head + fillL + '</svg>')
