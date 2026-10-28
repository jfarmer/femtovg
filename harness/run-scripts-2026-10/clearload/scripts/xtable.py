"""Reads an xctrace export (one table) into rows of (fmt, raw) per column, resolving id/ref."""
import xml.etree.ElementTree as ET


def rows(path):
    ids = {}
    out = []
    root = ET.parse(path).getroot()
    for row in root.iter('row'):
        vals = []
        for el in row:
            if 'ref' in el.attrib:
                v = ids.get(el.attrib['ref'], (None, None))
            elif el.tag == 'sentinel':
                v = (None, None)
            else:
                v = (el.attrib.get('fmt'), el.text)
                if 'id' in el.attrib:
                    ids[el.attrib['id']] = v
            vals.append(v)
        out.append(vals)
    return out
