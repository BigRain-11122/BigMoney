# -*- coding: utf-8 -*-
"""r1055 heal probe: extract the actual W253-script freeze-receipt note line
and diff it against the W254 editor's chunk src/dst faces."""
import io, difflib

ED = r"results\_w254bmc_derive_editor.py"
SRC_SCRIPT = r"results\_w253bmc_freeze_edits.py"

# 1) actual note line in the W253 script
actual = None
for ln in io.open(SRC_SCRIPT, encoding="utf-8"):
    if '"note": "estate W138..W206' in ln:
        actual = ln.rstrip("\r\n")
        break
assert actual is not None, "note line not found in W253 script"
print("ACTUAL_LEN", len(actual))
print("ACTUAL:", actual[:400])

# 2) editor chunk src/dst extraction
t = io.open(ED, encoding="utf-8").read()
i0 = t.find("chunk('''                     \"note\": \"estate W138..W206")
i1 = t.find("P5b-rcpt-note")
region = t[i0:i1 + 20]
# src text between first ''' pair; dst between second ''' pair
parts = region.split("'''")
print("N_PARTS", len(parts))
src_face = parts[1]
dst_face = parts[3]
print("SRC_FACE_LEN", len(src_face))
print("DST_FACE_LEN", len(dst_face))

# 3) compare actual line vs src_face (src_face should equal actual pre-banquet text
#    plus trailing quote-comma; the editor src starts with 21 spaces then "note":)
core = src_face.strip()
actual_core = actual.strip()
print("SRC==ACTUAL:", core == actual_core)
if core != actual_core:
    # show first diff position
    for k, (a, b) in enumerate(zip(actual_core, core)):
        if a != b:
            print("FIRST_DIFF @", k)
            print("  actual:", actual_core[max(0, k-60):k+80])
            print("  editor:", core[max(0, k-60):k+80])
            break
    else:
        k = min(len(actual_core), len(core))
        print("LENGTH_DIFF @", k)
        print("  actual tail:", actual_core[k-80:])
        print("  editor tail:", core[k-80:])
