# -*- coding: utf-8 -*-
"""r1055 heal: rebuild the W254 editor P5b-rcpt-note chunk faces from the
ACTUAL W253-script note line (verbatim src) + the frozen W254 prereg sec.3
mandate shift (dst), and fix the w245_a cascade mis-shift (frozen lineage
name = w244_a, four generations unchanged W250..W253)."""
import io, py_compile

ED = r"results\_w254bmc_derive_editor.py"
SRC_SCRIPT = r"results\_w253bmc_freeze_edits.py"

# 1) actual note line (verbatim, includes 21 leading spaces)
actual = None
for ln in io.open(SRC_SCRIPT, encoding="utf-8"):
    if '"note": "estate W138..W206' in ln:
        actual = ln.rstrip("\r\n")
        break
assert actual is not None and actual.endswith('"},'), "note line wrapper face unexpected"

# 2) build the W254 dst face from the actual, per the frozen W254 prereg sec.3
#    mandate (W253-block own W239..W252 legs (14) EXCLUDED + fresh W239..W253
#    legs (15) -> W254 block = 112 rows) + lineage faces
dst = actual
subs = [
    ("frozen W253 prereg sec.3 mandate", "frozen W254 prereg sec.3 mandate"),
    ("the W252 block's own W239..W251 legs (13) EXCLUDED",
     "the W253 block's own W239..W252 legs (14) EXCLUDED"),
    ("fresh W239..W252 legs (14) machine-derived",
     "fresh W239..W253 legs (15) machine-derived"),
    ("-> W253 block = 111 rows (W138..W206 + W211..W252)",
     "-> W254 block = 112 rows (W138..W206 + W211..W253)"),
    ("(w244_a holds wave-253 bands)", "(w244_a holds wave-254 bands)"),
    ("E63 5th-gen prevention this window: the W253 derive editor kept",
     "E63 6th-gen prevention this window: the W254 derive editor kept"),
    ("(list(range(211,252))/list(range(211,239))/list(range(239,252))",
     "(list(range(211,253))/list(range(211,239))/list(range(239,253))"),
]
for old, new in subs:
    n = dst.count(old)
    assert n == 1, "dst sub %r count %d != 1" % (old[:60], n)
    dst = dst.replace(old, new)

# 3) editor chunk region rebuild
t = io.open(ED, encoding="utf-8").read()
i0 = t.find("chunk('''                     \"note\": \"estate W138..W206")
i1 = t.find('"P5b-rcpt-note")', i0) + len('"P5b-rcpt-note")')
assert i0 > 0 and i1 > i0
region = t[i0:i1]
parts = region.split("'''")
assert len(parts) == 5, "unexpected chunk wrapper shape: %d parts" % len(parts)
new_src = "\n" + actual + "\n"
new_dst = "\n" + dst + "\n"
parts[1] = new_src
parts[3] = new_dst
new_region = "'''".join(parts)
t = t[:i0] + new_region + t[i1:]

# 4) frozen-name gate fix (w244_a is the lineage frozen name; clone cascade
#    mis-shifted 244->245)
old_gate = '("w245_a", 12),'
assert t.count(old_gate) == 1, "w245_a gate count != 1"
t = t.replace(old_gate, '("w244_a", 12),')
assert "w245_a" not in t, "residual w245_a face in editor"

io.open(ED, "w", encoding="utf-8", newline="").write(t)
py_compile.compile(ED, doraise=True)
print("HEAL OK: src verbatim %dB, dst %dB, gate w244_a fixed" % (len(actual), len(dst)))
