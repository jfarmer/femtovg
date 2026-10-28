#!/usr/bin/env python3
"""Writes the new reftest SVGs for direction / unicode-bidi into t/<dir>/<name>.svg (dir = direction|unicode-bidi)."""
import os
HEAD = '''<svg id="svg1" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg"
     font-family="{ff}" font-size="{fs}">
    <title>{title}</title>
'''
CROSS = '''
    <path id="crosshair" d="M 20 100 L 180 100 M 100 20 L 100 180"
          stroke="gray" stroke-width="0.5"/>
'''
LINE = '''
    <path id="line" d="M 100 20 L 100 180" stroke="gray" stroke-width="0.5"/>
'''
FOOT = '''
    <!-- image frame -->
    <rect id="frame" x="1" y="1" width="198" height="198" fill="none" stroke="black"/>
</svg>
'''
T = {}
def test(d, name, title, body, ff='Noto Sans', fs=14, cross=CROSS, defs='', root=''):
    import re
    counter = [0]
    def add_id(m):
        counter[0] += 1
        return f'<{m.group(1)} id="{m.group(1)}{counter[0]}"{m.group(2)}'
    body = re.sub(r'<(g|use|stop)(?![^>]*\bid=)(\s|/|>)', add_id, body)
    T[(d, name)] = HEAD.format(ff=ff, fs=fs, title=title).replace('font-size="%s">' % fs, 'font-size="%s"%s>' % (fs, (' ' + root) if root else ''), 1) + (('    <defs>\n' + defs + '    </defs>\n') if defs else '') + cross + body + FOOT

AR = 'ابجد هوز'          # Arabic letters, in Amiri
MIX = 'ابجد ABC 123 هوز'

# ---- direction
test('direction', 'rtl-with-text-anchor', '`rtl` with `text-anchor`', f'''
    <g direction="rtl" font-family="Amiri">
        <text id="text1" x="100" y="40" text-anchor="start" fill="red">Start {AR}</text>
        <text id="text2" x="100" y="60" text-anchor="middle" fill="green">Middle {AR}</text>
        <text id="text3" x="100" y="80" text-anchor="end" fill="blue">End {AR}</text>
    </g>
    <g direction="ltr" font-family="Amiri">
        <text id="text4" x="100" y="120" text-anchor="start" fill="red">Start {AR}</text>
        <text id="text5" x="100" y="140" text-anchor="middle" fill="green">Middle {AR}</text>
        <text id="text6" x="100" y="160" text-anchor="end" fill="blue">End {AR}</text>
    </g>
''', cross=LINE)

test('direction', 'rtl-with-latin-text', '`rtl` with Latin text', '''
    <g direction="rtl">
        <text id="text1" x="170" y="50">Hello, World!</text>
        <text id="text2" x="170" y="75">a b c 1 2 3 !</text>
        <text id="text3" x="170" y="100">(Hello) [World]</text>
    </g>
    <g direction="ltr">
        <text id="text4" x="30" y="140">Hello, World!</text>
    </g>
''')

test('direction', 'rtl-with-mixed-scripts', '`rtl` with mixed scripts', f'''
    <g direction="rtl" font-family="Amiri">
        <text id="text1" x="170" y="50">{MIX}</text>
        <text id="text2" x="170" y="75">{AR} Latin {AR}</text>
    </g>
    <g direction="ltr" font-family="Amiri">
        <text id="text3" x="30" y="120">{MIX}</text>
        <text id="text4" x="30" y="145">{AR} Latin {AR}</text>
    </g>
''')

test('direction', 'on-svg-element', '`direction` on the `svg` element (#475)', '''
    <text id="text1" x="100" y="70" text-anchor="middle"> כתובת MAC:&#x200F;
        <tspan id="tspan1" direction="ltr" unicode-bidi="embed">00-24-AF-2A-55-FC</tspan> </text>
    <text id="text2" x="100" y="130" text-anchor="start"> כתובת MAC:&#x200F;
        <tspan id="tspan2" direction="ltr" unicode-bidi="embed">00-24-AF-2A-55-FC</tspan> </text>
''', fs=11, root='direction="rtl" xml:lang="he"')

test('direction', 'inherited', '`direction` is inherited', '''
    <g direction="rtl">
        <text id="text1" x="170" y="40">Inherited from a group</text>
        <g>
            <text id="text2" x="170" y="65" direction="ltr">Reset on text</text>
        </g>
        <text id="text3" x="170" y="90"><tspan>Inherited by a tspan</tspan></text>
    </g>
''')

test('direction', 'on-tspan', '`direction` on `tspan`', '''
    <text id="text1" x="100" y="40" fill="red"><tspan x="100" direction="rtl">tspan rtl, start</tspan></text>
    <text id="text2" x="100" y="65" fill="blue" text-anchor="end"><tspan x="100" direction="rtl">tspan rtl, end on text</tspan></text>
    <text id="text3" x="100" y="90" fill="green" direction="rtl"><tspan x="100" direction="ltr">text rtl, tspan ltr</tspan></text>
    <text id="text4" x="100" y="120" fill="black" direction="rtl">1 2 3 <tspan direction="ltr">ABC DEF</tspan> 4 5 6</text>
''', cross=LINE)

test('direction', 'rtl-with-text-decoration', '`rtl` with `text-decoration`', f'''
    <g direction="rtl" font-family="Amiri">
        <text id="text1" x="170" y="50" text-decoration="underline">Under {AR}</text>
        <text id="text2" x="170" y="80" text-decoration="line-through">{AR} Line</text>
        <text id="text3" x="170" y="110">Over <tspan text-decoration="overline" fill="red">{AR}</tspan> lined</text>
    </g>
''')

test('direction', 'rtl-with-word-spacing', '`rtl` with `word-spacing`', f'''
    <g id="group1" direction="rtl" font-family="Amiri">
        <text id="text1" x="170" y="50" word-spacing="10">{AR} Word spacing</text>
        <text id="text2" x="170" y="80" word-spacing="10">Word spacing {AR}</text>
    </g>
''')

test('direction', 'rtl-with-filter', '`rtl` with a drop shadow', f'''
    <g direction="rtl" font-family="Amiri" font-size="18">
        <text id="text1" x="170" y="50" filter="url(#dropShadow)">{AR} ABC</text>
        <text id="text2" x="100" y="90" text-anchor="middle" filter="url(#dropShadow)">ABC {AR}</text>
        <text id="text3" x="170" y="130" filter="url(#fill)" fill="red">{AR} ABC</text>
    </g>
    <g direction="ltr" font-family="Amiri" font-size="18">
        <text id="text4" x="30" y="170" filter="url(#dropShadow)">{AR} ABC</text>
    </g>
''', defs='''
        <filter id="dropShadow">
            <feDropShadow dx="3" dy="3" stdDeviation="1.5" flood-color="green"/>
        </filter>
        <filter id="fill" x="0" y="0" width="1" height="1">
            <feFlood flood-color="gold"/>
            <feComposite in2="SourceGraphic" operator="in"/>
        </filter>
''')

test('direction', 'rtl-with-clip-path', '`rtl` with `clip-path`', f'''
    <g direction="rtl" font-family="Amiri" font-size="24">
        <text id="text1" x="170" y="50" clip-path="url(#half)" fill="blue">{AR} ABC</text>
        <text id="text2" x="170" y="90" clip-path="url(#userSpace)" fill="green">{AR} ABC</text>
    </g>
    <rect id="rect1" x="10" y="110" width="180" height="60" fill="orange" clip-path="url(#text)"/>
''', defs=f'''
        <clipPath id="half" clipPathUnits="objectBoundingBox">
            <rect x="0" y="0" width="0.5" height="1"/>
        </clipPath>
        <clipPath id="userSpace">
            <rect x="60" y="60" width="60" height="40"/>
        </clipPath>
        <clipPath id="text">
            <text x="190" y="160" direction="rtl" font-family="Amiri" font-size="36">{AR} ABC</text>
        </clipPath>
''')

test('direction', 'rtl-with-mask', '`rtl` with `mask`', f'''
    <rect id="rect1" x="10" y="30" width="180" height="60" fill="purple" mask="url(#text)"/>
    <g direction="rtl" font-family="Amiri" font-size="24">
        <text id="text1" x="170" y="140" mask="url(#gradient)" fill="blue">{AR} ABC</text>
    </g>
''', defs=f'''
        <mask id="text">
            <rect width="200" height="200" fill="#555"/>
            <text x="190" y="75" direction="rtl" font-family="Amiri" font-size="36" fill="white">{AR} ABC</text>
        </mask>
        <linearGradient id="lg">
            <stop offset="0" stop-color="white"/>
            <stop offset="1" stop-color="black"/>
        </linearGradient>
        <mask id="gradient" maskContentUnits="objectBoundingBox">
            <rect width="1" height="1" fill="url(#lg)"/>
        </mask>
''')

PATHS = '''
        <path id="path1" d="M 20 30 C 73.3333 30 126.6667 30 180 30"/>
        <path id="path2" d="M 20 55 C 73.3333 55 126.6667 55 180 55"/>
        <path id="path3" d="M 20 80 C 73.3333 80 126.6667 80 180 80"/>
        <path id="path4" d="M 20 105 C 73.3333 105 126.6667 105 180 105"/>
'''
GUIDES = '''
    <g stroke="lightgray" stroke-width="0.5" fill="none">
        <use xlink:href="#path1"/><use xlink:href="#path2"/><use xlink:href="#path3"/>
        <use xlink:href="#path4"/>
    </g>
'''
test('direction', 'rtl-on-text-path', '`rtl` on a text path', f'''{GUIDES}
    <g direction="rtl" font-family="Amiri">
        <text id="text1" fill="red"><textPath xlink:href="#path1" startOffset="80">Start {AR}</textPath></text>
        <text id="text2" fill="green" text-anchor="middle"><textPath xlink:href="#path2" startOffset="50%">Middle {AR}</textPath></text>
        <text id="text3" fill="blue" text-anchor="end"><textPath xlink:href="#path3" startOffset="80">End {AR}</textPath></text>
    </g>
    <g direction="ltr" font-family="Amiri">
        <text id="text4" fill="black"><textPath xlink:href="#path4" startOffset="30">{MIX}</textPath></text>
    </g>
''', defs=PATHS, cross='')

test('direction', 'rtl-on-text-path-with-start-offset', '`rtl` on a text path with `startOffset`', f'''{GUIDES}
    <g direction="rtl" font-family="Amiri" font-size="12">
        <text id="text1" fill="red"><textPath xlink:href="#path1" startOffset="60">Cut at the path start {AR}</textPath></text>
        <text id="text2" fill="green" text-anchor="end"><textPath xlink:href="#path2" startOffset="100">Cut at the path end {AR}</textPath></text>
        <text id="text3" fill="blue"><textPath xlink:href="#path3" startOffset="160">Ends at the path end {AR}</textPath></text>
        <text id="text4" fill="black" text-anchor="middle"><textPath xlink:href="#path4" startOffset="20">Centered on the start {AR}</textPath></text>
    </g>
''', defs=PATHS, cross='')

test('direction', 'rtl-with-punctuation', '`rtl` with end-of-sentence punctuation', f'''
    <g id="group1" direction="rtl" font-family="Amiri" font-size="12">
        <text id="text1" x="190" y="34">قرأت عن SVG.</text>
        <text id="text2" x="190" y="56">هل تعرف HTML؟</text>
        <text id="text3" x="190" y="78">ما أجمل SVG!</text>
        <text id="text4" x="190" y="100">أولاً، ثانياً؛ ثم SVG.</text>
        <text id="text5" x="190" y="122">نهاية الجملة: abc.</text>
        <text id="text6" x="190" y="144">جملة بالإنجليزية at the end.</text>
    </g>
''', cross=LINE)

test('direction', 'rtl-with-numbers', '`rtl` with numbers and date ranges', f'''
    <g id="group1" direction="rtl" font-family="Amiri" font-size="12">
        <text id="text1" x="190" y="34">من 1990–2000 كان</text>
        <text id="text2" x="190" y="56">التاريخ 12/05/2026 م</text>
        <text id="text3" x="190" y="78">الوقت 10:30–11:45</text>
        <text id="text4" x="190" y="100">الرقم 1,000.5 و 3.14</text>
        <text id="text5" x="190" y="122">من ١٩٩٠–٢٠٠٠ كان</text>
        <text id="text6" x="190" y="144">التاريخ ١٢/٠٥/٢٠٢٦ م</text>
        <text id="text7" x="190" y="166">الرقم ٣٫١٤ و ١٬٠٠٠</text>
    </g>
''', cross=LINE)

test('direction', 'rtl-with-brackets', '`rtl` with nested parentheses and brackets', f'''
    <g id="group1" direction="rtl" font-family="Amiri" font-size="12">
        <text id="text1" x="190" y="34">نص (كلمة [مثال {{تجربة}}]) نص</text>
        <text id="text2" x="190" y="56">(SVG (HTML [CSS])) ثم نص</text>
        <text id="text3" x="190" y="78">نص (ابجد (هوز) 12) نص</text>
        <text id="text4" x="190" y="100">[abc (def) ghi] ونص {{1}} ثم</text>
        <text id="text5" x="190" y="122">(1) أولاً و (2) ثانياً</text>
        <text id="text6" x="190" y="144">SVG (v1.1) و [HTML5] ثم</text>
    </g>
''', cross=LINE)

test('direction', 'rtl-with-scientific-text', '`rtl` with scientific text', f'''
    <g id="group1" direction="rtl" font-family="Amiri" font-size="12">
        <text id="text1" x="190" y="34">درجة 36.6 °C و -5 و +3</text>
        <text id="text2" x="190" y="56">p &lt; 0.05 و x = 2</text>
        <text id="text3" x="190" y="78">5 ± 0.3 µm و 10 mg/L</text>
        <text id="text4" x="190" y="100">Na+ / Cl− و 50%</text>
        <text id="text5" x="190" y="122">α = 0.01 و β &gt; 2</text>
    </g>
''', cross=LINE)

# ---- unicode-bidi
test('unicode-bidi', 'embed', '`embed`', '''
    <text id="text1" x="170" y="40" direction="rtl">1 abc <tspan unicode-bidi="embed" direction="ltr">ltr embed 123</tspan> def 2</text>
    <text id="text2" x="30" y="70" direction="ltr">1 abc <tspan unicode-bidi="embed" direction="rtl">AB CD EF</tspan> def 2</text>
    <text id="text3" x="30" y="100" direction="ltr">1 <tspan unicode-bidi="embed" direction="rtl">AB <tspan fill="red">CD</tspan> EF</tspan> gh</text>
    <text id="text4" x="30" y="130" direction="ltr">1 <tspan direction="rtl">AB CD EF</tspan> gh</text>
    <text id="text5" x="170" y="160" direction="rtl" unicode-bidi="embed" text-anchor="middle" transform="translate(-70 0)">rtl embed middle 3</text>
''')

test('unicode-bidi', 'bidi-override-on-tspan', '`bidi-override` on a `tspan`', '''
    <text id="text1" x="30" y="40" direction="ltr">abc <tspan unicode-bidi="bidi-override" direction="rtl">ABC DEF</tspan> ghi</text>
    <text id="text2" x="170" y="70" direction="rtl">abc <tspan unicode-bidi="bidi-override" direction="ltr">ABC DEF</tspan> ghi</text>
    <text id="text3" x="30" y="100"><tspan unicode-bidi="bidi-override" direction="rtl">ab <tspan fill="red">cd</tspan> ef</tspan> gh</text>
    <text id="text4" x="30" y="130" direction="ltr" unicode-bidi="bidi-override">ltr override on text</text>
    <text id="text5" x="170" y="160" direction="rtl" unicode-bidi="bidi-override">rtl override on text</text>
''')

test('unicode-bidi', 'isolate', '`isolate` and `isolate-override`', '''
    <text id="text1" x="30" y="40" direction="ltr">1 <tspan unicode-bidi="isolate" direction="rtl">AB CD EF</tspan> gh</text>
    <text id="text2" x="30" y="70" direction="ltr">2 <tspan unicode-bidi="isolate-override" direction="rtl">AB CD EF</tspan> gh</text>
    <text id="text3" x="170" y="100" direction="rtl">3 <tspan unicode-bidi="isolate" direction="ltr">AB CD EF</tspan> gh</text>
    <text id="text4" x="170" y="130" direction="rtl">4 <tspan unicode-bidi="isolate-override" direction="ltr">AB CD EF</tspan> gh</text>
''')

test('unicode-bidi', 'plaintext', '`plaintext`', f'''
    <g font-family="Amiri">
        <text id="text1" x="100" y="40" unicode-bidi="plaintext">1 plaintext {AR}</text>
        <text id="text2" x="100" y="70" unicode-bidi="plaintext">{AR} plaintext 2</text>
        <text id="text3" x="100" y="100" direction="rtl"><tspan unicode-bidi="plaintext">3 plain {AR}</tspan> tail</text>
    </g>
''', cross=LINE)

test('unicode-bidi', 'normal-ignores-direction-on-tspan', '`direction` on a `tspan` without `unicode-bidi`', '''
    <text id="text1" x="30" y="40" direction="ltr">abc <tspan direction="rtl">ABC DEF</tspan> ghi</text>
    <text id="text2" x="30" y="70" direction="ltr">abc <tspan direction="rtl" unicode-bidi="normal">ABC DEF</tspan> ghi</text>
''')

if __name__ == '__main__':
    root = os.path.dirname(os.path.abspath(__file__)) + '/t'
    for (d, name), svg in T.items():
        os.makedirs(f'{root}/{d}', exist_ok=True)
        if 'xlink:href' in svg:
            svg = svg.replace('xmlns="http://www.w3.org/2000/svg"', 'xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"', 1)
        open(f'{root}/{d}/{name}.svg', 'w').write(svg)
    print(len(T), 'tests')
