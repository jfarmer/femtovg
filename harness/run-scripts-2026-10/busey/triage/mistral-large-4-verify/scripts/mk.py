import os
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/svg'
FACE = '<path d="M512 176 C642 176 724 282 724 452 C724 585 690 720 612 812 C575 852 449 852 412 812 C334 720 300 585 300 452 C300 282 382 176 512 176 Z" fill="#d99a6c"/>'
EARS = ('<path d="M250 455 C225 430 220 520 246 585 C270 640 300 650 318 610 C338 565 330 500 250 455 Z" fill="#c98a5f"/>'
        '<path d="M774 455 C799 430 804 520 778 585 C754 640 724 650 706 610 C686 565 694 500 774 455 Z" fill="#c98a5f"/>')
GLOW = '<ellipse cx="512" cy="392" rx="250" ry="150" fill="#ffe0b8" opacity="0.22" filter="url(#soft12)"/>'
MASKDEF = ('<mask id="faceLightMask" maskUnits="userSpaceOnUse"><rect width="1024" height="1024" fill="black"/>'
           '<ellipse cx="512" cy="405" rx="285" ry="205" fill="white" opacity="0.9"/></mask>')
def defs(cif=''):
    c = f' color-interpolation-filters="{cif}"' if cif else ''
    return ('<defs><filter id="soft12" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="12"/></filter>'
            f'<filter id="headShadow" x="-40%" y="-40%" width="180%" height="180%"{c}>'
            '<feDropShadow dx="0" dy="18" stdDeviation="18" flood-color="#000000" flood-opacity="0.55"/></filter>'
            # the shadow alone, as the browser computes it from the same SourceAlpha
            f'<filter id="shadowOnly" x="-40%" y="-40%" width="180%" height="180%"{c}>'
            '<feGaussianBlur in="SourceAlpha" stdDeviation="18"/><feOffset dy="18" result="o"/>'
            '<feFlood flood-color="#000000" flood-opacity="0.55"/><feComposite operator="in" in2="o"/></filter>'
            + MASKDEF + '</defs>')
def svg(bg, body, cif=''):
    return (f'<svg width="1024" height="1024" viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg">{defs(cif)}'
            f'<rect width="1024" height="1024" fill="{bg}"/>{body}</svg>\n')
BG = '#1d2a35'
V = {
    'v_full': svg(BG, f'<g filter="url(#headShadow)">{FACE}{EARS}{GLOW}</g>'),
    'v_full_srgb': svg(BG, f'<g filter="url(#headShadow)">{FACE}{EARS}{GLOW}</g>', 'sRGB'),
    'v_full_mask': svg(BG, f'<g filter="url(#headShadow)">{FACE}{EARS}<g mask="url(#faceLightMask)">{GLOW}</g></g>'),
    'v_nofilter': svg(BG, f'<g>{FACE}{EARS}{GLOW}</g>'),
    'v_glow_black': svg('#000000', f'<g>{GLOW}</g>'),
    'v_glow_white': svg('#ffffff', f'<g>{GLOW}</g>'),
    'v_shadow_white': svg('#ffffff', f'<g filter="url(#shadowOnly)">{FACE}{EARS}{GLOW}</g>'),
    'v_noglow': svg(BG, f'<g filter="url(#headShadow)">{FACE}{EARS}</g>'),
}
for k, s in V.items():
    open(f'{D}/{k}.svg', 'w').write(s)
print(sorted(V))
