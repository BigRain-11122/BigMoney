# -*- coding: utf-8 -*-
# r1050 bm-c: fix P5b-hdr-parity chunk needle/dst leading-space defect in the
# dead-window derive editor (source lines carry one leading space inside the
# list literal; the authored needle dropped it -> xf(needle) not found).
import io

p = "results/_w252bmc_derive_editor.py"
t = io.open(p, encoding="utf-8").read()

old_needle_lines = [
    '"    #     PARITY STRUCTURAL CHOICE (frozen W251 prereg sec.3 mandate):",',
    '"    #     estate 92 rows (W138..W206 full-span 69 + W211..W233 legs) +",',
    '"    #     W234..W238 legs (5) extracted verbatim from the OWN W250 block",',
    "\"    #     physical bytes; the W250 block's own W239..W249 legs (11) are\",",
    '"    #     EXCLUDED from the estate path per the prereg mandate; fresh",',
    '"    #     W239..W250 legs (12) added, machine-derived from the live pf",',
    '"    #     registry at freeze time -> 109 parity rows (W138..W206+W211..W250).",',
]
old_needle = "chunk('''" + "\n".join(old_needle_lines) + "''',"
new_needle = "chunk(''' " + "\n ".join(old_needle_lines) + "''',"
n = t.count(old_needle)
assert n == 1, f"needle-call count {n}"
t = t.replace(old_needle, new_needle)

old_dst_lines = [
    '"    #     PARITY STRUCTURAL CHOICE (frozen W252 prereg sec.3 mandate):",',
    '"    #     estate 69 rows (W138..W206 full-span, r858 absorb generation) +",',
    '"    #     W211..W238 legs (28) extracted verbatim from the OWN W251 block",',
    "\"    #     physical bytes; the W251 block's own W239..W250 legs (12) are\",",
    '"    #     EXCLUDED from the estate path per the prereg mandate; fresh",',
    '"    #     W239..W251 legs (13) added, machine-derived from the live pf",',
    '"    #     registry at freeze time -> 110 parity rows (W138..W206+W211..W251).",',
]
old_dst = "\n".join(old_dst_lines) + "''', \"P5b-hdr-parity\")"
new_dst = "\n ".join(old_dst_lines) + "''', \"P5b-hdr-parity\")"
m = t.count(old_dst)
assert m == 1, f"dst-call count {m}"
t = t.replace(old_dst, new_dst)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("patched OK: needle + dst leading spaces restored")
