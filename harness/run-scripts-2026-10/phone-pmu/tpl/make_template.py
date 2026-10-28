#!/usr/bin/env python3
"""Writes an Instruments CPU Counters template in *manual* mode with a chosen
PMU event list, starting from a template saved by Instruments in guided mode
(CPU Bottlenecks). How the template stores the choice (found by decoding
femtovg-pmu-a13.tracetemplate, an NSKeyedArchiver plist):

- the CPU Counters instrument's recordingControlState.state.optionsEncoded is
  a JSON blob (plist data) with keys configurationType ({"guided": {}} or
  {"manual": {}}; Swift Codable enum ConfigurationType), selectedCountingMode,
  sampleByTime, pmiEventAliasOrMnemonic/pmiThreshold, countingLevel ("EL0"),
  and allEventsAndFormulas: a list of base64 NSKeyedArchiver blobs of
  XRCountersSetupEventOrFormula {_mnemonic, _displayName, _aliasOrMnemonic,
  _explanation, _formulaText, _formulaEvaluator, _beingEdited}.
- manual mode records exactly allEventsAndFormulas (FIXED_CYCLES and
  FIXED_INSTRUCTIONS plus the configurable events; the kpep plist for the CPU
  says which counters each event may use).

usage: make_template.py [--high] <in.tracetemplate> <out.tracetemplate> EVENT [EVENT...]
(--high: high-frequency time sampling)
"""
import base64, json, plistlib, sys

def event_blob(mnemonic):
    display = {"FIXED_CYCLES": "Cycles (FIXED_CYCLES)", "FIXED_INSTRUCTIONS": "Instructions (FIXED_INSTRUCTIONS)"}.get(mnemonic, mnemonic)
    alias = {"FIXED_CYCLES": "Cycles", "FIXED_INSTRUCTIONS": "Instructions"}.get(mnemonic, mnemonic)
    U = plistlib.UID
    objs = ["$null",
            {"$class": U(5), "_formulaEvaluator": U(0), "_formulaText": U(0), "_explanation": U(0),
             "_mnemonic": U(2), "_beingEdited": False, "_displayName": U(3), "_aliasOrMnemonic": U(4)},
            mnemonic, display, alias,
            {"$classname": "XRCountersSetupEventOrFormula", "$classes": ["XRCountersSetupEventOrFormula", "NSObject"]}]
    arch = {"$version": 100000, "$archiver": "NSKeyedArchiver", "$top": {"root": U(1)}, "$objects": objs}
    return base64.b64encode(plistlib.dumps(arch, fmt=plistlib.FMT_BINARY)).decode()

def main():
    args = sys.argv[1:]
    high = "--high" in args
    args = [a for a in args if a != "--high"]
    src, dst, events = args[0], args[1], args[2:]
    p = plistlib.load(open(src, "rb"))
    objs = p["$objects"]
    hits = 0
    for i, o in enumerate(objs):
        if isinstance(o, bytes) and o[:1] == b"{":
            try:
                j = json.loads(o)
            except Exception:
                continue
            if "allEventsAndFormulas" not in j:
                continue
            j["configurationType"] = {"manual": {}}
            j["allEventsAndFormulas"] = [event_blob(e) for e in ["FIXED_CYCLES", "FIXED_INSTRUCTIONS"] + events]
            j["sampleByTime"] = True
            j["useHighFrequencyForManualMode"] = high
            objs[i] = json.dumps(j, separators=(",", ":")).encode()
            hits += 1
    assert hits == 1, hits
    # The template's description string, so the listing says what it records.
    for i, o in enumerate(objs):
        if isinstance(o, dict) and o.get("NS.string", "").startswith("Analyze CPU bottlenecks"):
            o["NS.string"] = "femtovg PMU manual: " + " ".join(events)
    plistlib.dump(p, open(dst, "wb"), fmt=plistlib.FMT_BINARY)
    print(f"{dst}: manual, high-frequency {high}, events {events}")

main()
