import re, sys
src = open('/Users/matt/src/femtovg-wt/da/corpus/buseybench/mistral-large-4.svg').read()
D = '/Users/matt/src/femtovg-wt/runs/busey/triage/mistral-large-4/svg/'
def w(name, s):
    assert s != src or name == 'm_orig', name
    open(D + name + '.svg', 'w').write(s)
w('m_orig', src)
# 1. no drop shadow on the head group
w('m_noshadow', src.replace('<g filter="url(#headShadow)">', '<g>'))
# 2. the faceLightMask group removed
s = re.sub(r'<g mask="url\(#faceLightMask\)">.*?</g>', '', src, flags=re.S)
w('m_nolight', s)
# 3. the faceLightMask group without its mask
w('m_lightnomask', src.replace('<g mask="url(#faceLightMask)">', '<g>'))
# 4. drop shadow merge in sRGB (color-interpolation-filters on the filter)
w('m_shadow_srgb', src.replace('<filter id="headShadow"', '<filter id="headShadow" color-interpolation-filters="sRGB"'))
# 5. the hairMask group without its mask
w('m_hairnomask', src.replace('<g mask="url(#hairMask)">', '<g>'))
