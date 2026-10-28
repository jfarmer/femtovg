#!/usr/bin/env python3
"""Decode an NSKeyedArchiver plist (Instruments .tracetemplate) into nested Python
objects and print it as JSON-ish text. Nested 'optionsEncoded' / NSData blobs that are
themselves bplists are decoded recursively. Usage: unarchive.py <file> [maxdepth]"""
import plistlib, sys, json
def load(data):
    p = plistlib.loads(data)
    if not isinstance(p, dict) or p.get("$archiver") != "NSKeyedArchiver":
        return p
    objs = p["$objects"]
    seen = {}
    def res(x, depth=0):
        if isinstance(x, plistlib.UID):
            i = x.data
            if i in seen: return seen[i]
            o = objs[i]
            if o == "$null": return None
            seen[i] = f"<cycle {i}>"
            v = res(o, depth+1)
            seen[i] = v
            return v
        if isinstance(x, dict):
            cls = x.get("$class")
            cname = None
            if isinstance(cls, plistlib.UID):
                cname = objs[cls.data].get("$classname")
            if "NS.keys" in x:
                return {str(res(k)): res(v) for k, v in zip(x["NS.keys"], x["NS.objects"])}
            if "NS.objects" in x:
                return [res(v) for v in x["NS.objects"]]
            if "NS.string" in x: return x["NS.string"]
            if "NS.data" in x: return sub(x["NS.data"])
            d = {k: res(v) for k, v in x.items() if k != "$class"}
            if cname: d["__class"] = cname
            return d
        if isinstance(x, list): return [res(v) for v in x]
        if isinstance(x, bytes): return sub(x)
        return x
    return res(p["$top"])
def sub(b):
    if b[:6] == b"bplist":
        try: return {"__bplist": load(b)}
        except Exception as e: return f"<bplist err {e}>"
    return f"<{len(b)} bytes>"
def conv(o):
    if isinstance(o, dict): return {k: conv(v) for k, v in o.items()}
    if isinstance(o, list): return [conv(v) for v in o]
    if isinstance(o, (bytes, bytearray)): return f"<{len(o)} bytes>"
    if isinstance(o, plistlib.UID): return f"UID{o.data}"
    return o if isinstance(o, (str, int, float, bool, type(None))) else str(o)
print(json.dumps(conv(load(open(sys.argv[1], "rb").read())), indent=1, ensure_ascii=False))
