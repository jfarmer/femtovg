D = '/Users/matt/src/femtovg-wt/runs/busey/triage/mistral-large-4/svg/'
head = '<svg width="1024" height="1024" viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg">'
teeth = '<path d="M430 742 C470 758 554 758 594 742 C575 782 540 800 512 802 C484 800 449 782 430 742 Z" fill="#e8dcc0" opacity="0.92"/>'
tongue = '<path d="M455 770 C485 792 539 792 569 770 C552 812 472 812 455 770 Z" fill="#a34a4a" opacity="0.85"/>'
open(D + 'r_teeth.svg', 'w').write(head + '<rect width="1024" height="1024" fill="#3a1216"/>' + teeth + '</svg>')
open(D + 'r_tongue.svg', 'w').write(head + '<rect width="1024" height="1024" fill="#e8dcc0"/>' + tongue + '</svg>')
