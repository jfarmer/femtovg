import re
S='/Users/matt/src/femtovg-wt/runs/busey/triage/gemini-3-1-pro-preview'
src=open(f'{S}/svg/orig.svg').read()
def w(name, old, new='', count=1):
    assert old in src, name
    t=src.replace(old,new,count) if count else src.replace(old,new)
    open(f'{S}/svg/{name}.svg','w').write(t)
inner1='<path d="M 290 720 C 400 670, 624 670, 734 720 C 700 740, 600 720, 512 720 C 424 720, 324 740, 290 720 Z" fill="#000000" opacity="0.5" filter="url(#blur-sm)"/>'
inner2='<path d="M 290 720 C 344 860, 680 860, 734 720 C 700 820, 600 840, 512 840 C 424 840, 324 820, 290 720 Z" fill="#000000" opacity="0.7" filter="url(#blur-sm)"/>'
w('m_noinner1', inner1)
w('m_noinner2', inner2)
w('m_noinner2blur', inner2, inner2.replace(' filter="url(#blur-sm)"',''))
w('m_noclip', '<g clip-path="url(#mouth-clip)">', '<g>')
lowstroke='<path d="M 280 725 C 344 880, 680 880, 744 725" fill="none" stroke="#5c2411" stroke-width="6" filter="url(#blur-sm)"/>'
w('m_nolowstroke', lowstroke)
w('m_lowstroke_noblur', lowstroke, lowstroke.replace(' filter="url(#blur-sm)"',''))
w('m_nolowfill', '<path d="M 280 725 C 344 880, 680 880, 744 725 C 680 840, 344 840, 280 725 Z" fill="url(#lip-lower)"/>')
w('m_nocreases', '<path d="M 260 700 C 270 730, 290 750, 310 760" fill="none" stroke="#4a1d0d" stroke-width="8" filter="url(#blur-sm)" opacity="0.7"/>')
w('m_noupstroke', '<path d="M 280 725 C 390 665, 634 665, 744 725" fill="none" stroke="#5c2411" stroke-width="4" filter="url(#blur-xs)"/>')
w('m_noupfill', '<path d="M 280 725 C 390 665, 634 665, 744 725 C 634 685, 390 685, 280 725 Z" fill="url(#lip-upper)"/>')
w('m_nodark', '<path d="M 290 720 C 400 670, 624 670, 734 720 C 680 860, 344 860, 290 720 Z" fill="#1a0804"/>')
