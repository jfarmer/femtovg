#!/usr/bin/env python3
"""ddmin.py SVG ZOOM OUT.svg [A=pm14] [B=stl] : shrink SVG, removing drawable elements (not <defs>) while
builds A and B still render it differently at ZOOM in the default frame; writes the smallest such SVG."""
import copy, hashlib, os, subprocess, sys
import xml.etree.ElementTree as ET

src, zoom, out = sys.argv[1], sys.argv[2], sys.argv[3]
opts = dict(x.split('=', 1) for x in sys.argv[4:])
A, B = opts.get('A', 'pm14'), opts.get('B', 'stl')
BIN = os.path.expanduser('~/src/femtovg-wt/bin')
HERE = os.path.dirname(os.path.abspath(__file__))
ENV = {**os.environ, 'FRAME_W': '460', 'FRAME_H': '260', 'BOX': '200', 'BOX_X': '130', 'BOX_Y': '30',
       'SINGLE_SHADOW_LAYER': '1'}
ET.register_namespace('', 'http://www.w3.org/2000/svg')
ET.register_namespace('xlink', 'http://www.w3.org/1999/xlink')


def render(tree, build):
    path = f'{HERE}/tmp/dd_{build}.svg'
    tree.write(path)
    ppm = f'{HERE}/tmp/dd_{build}.ppm'
    subprocess.run([f'{BIN}/_logos_full_{build}', zoom, ppm, path], env=ENV, capture_output=True, timeout=120)
    return hashlib.sha1(open(ppm, 'rb').read()).hexdigest() if os.path.exists(ppm) else None


def differs(tree):
    a, b = render(tree, A), render(tree, B)
    return a is not None and b is not None and a != b


def leaves(tree):
    """(parent, child) for every element outside <defs>, deepest first."""
    found = []

    def walk(node):
        for child in list(node):
            if child.tag.endswith('defs') or child.tag.endswith('clipPath') or child.tag.endswith('mask'):
                continue
            walk(child)
            found.append((node, child))
    walk(tree.getroot())
    return found


tree = ET.parse(src)
assert differs(tree), 'the builds agree on the original'
changed = True
while changed:
    changed = False
    pairs = leaves(tree)
    chunk = max(1, len(pairs) // 2)
    while chunk >= 1:
        i = 0
        while i < len(pairs):
            trial = copy.deepcopy(tree)
            # map the pairs onto the copy by position in the walk
            tpairs = leaves(trial)
            if len(tpairs) != len(pairs):
                break
            for parent, child in tpairs[i:i + chunk]:
                if child in list(parent):
                    parent.remove(child)
            if differs(trial):
                tree, pairs, changed = trial, leaves(trial), True
                print('kept', len(pairs), 'elements', flush=True)
            else:
                i += chunk
        chunk //= 2
tree.write(out)
print('minimal:', len(leaves(tree)), 'elements ->', out)
