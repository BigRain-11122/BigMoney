# -*- coding: utf-8 -*-
"""Probe the W308 freeze editor for one-wave-bump literal candidates (r1196).

Prints a count table only; touches nothing.
"""
import io
import re

s = io.open("results/_w308bmc_freeze_edits.py", encoding="utf-8").read()
cands = [
    "NEW_W = 308", "PREV_W = 307", "PRIOR_W = 306",
    "SIXTY-SECOND", "SIXTY-FIRST", "SIXTIETH",
    "HUNDRED-AND-TWENTY-FIFTH", "HUNDRED-AND-TWENTY-FOURTH",
    "THREE HUNDRED AND SIXTH", "THREE HUNDRED AND FIFTH",
    "w<308>", "w<307>", "w<306>",
    "297", "298", "296", "130", "126", "125", "127",
    '"wave": 308', '"wave": 307',
    "308: {\"a\"", "308: {{\"a\"", "308: {\"batch\"", "{CFG_I}308: {{\"batch\"",
    "wave 308: ", "wave 307: ",
    "range(303, 295, -1)", "range(304, 296, -1)",
    "1,101,941", "1_101_941", "1,099,741", "1_099_741",
    "675,520", "675_520", "673,320", "673_320",
    "166 parity rows", "167 parity rows",
    "legs (60)", "legs (61)", "legs (59)",
    "r1193", "r1194", "r1195", "r1196",
    "r309;", "r310;",
    "13:1x", "13:2x", "13:4x",
    "3e1ecb3110", "55eb0897ac",
    "2da27a4a3a", "b109a52460",
    "054ba69f34", "897b31fc83",
]
for c in cands:
    print("%-46s %d" % (c, s.count(c)))
print("--- band tokens ---")
print(sorted(set(re.findall(r"\b\d{3}_\d{3}\b", s))))
print("--- ordinals in caps containing SIXT|HUNDRED ---")
print(sorted(set(re.findall(r"[A-Z][A-Z-]*(?:SIXT|HUNDRED)[A-Z-]*", s))))
print("--- lowercase wave ids ---")
print(sorted(set(re.findall(r"\bw(\d{3})\b", s))))
print("--- wave keys in dict-ish context ---")
for m in re.finditer(r"(?m)^.{0,24}\b(\d{3}): \{", s):
    print(repr(m.group(0)))
print("bytes=%d" % len(s.encode("utf-8")))