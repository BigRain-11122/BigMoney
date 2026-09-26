# -*- coding: utf-8 -*-
"""r305 bm-b lineage copy (r298 kenglu law): whole-file copy + round-face
replace only + difflib delta verify (expected face) before any run."""
import difflib
import io
import os

R = os.path.dirname(os.path.abspath(__file__))
JOBS = [
    # (src, dst, replace rules, expected unified-delta line count)
    ("_r304bmb_s6_chain.ps1", "_r305bmb_s6_chain.ps1",
     [("r304", "r305")], 2),
    ("_r304bmb_astock_pass_probe.py", "_r305bmb_astock_pass_probe.py",
     [("r304", "r305"), ("probe #17", "probe #18")], 8),
    ("_r304bmb_faces.py", "_r305bmb_faces.py",
     [("r304", "r305")], 2),
]

for old, new, rules, expected in JOBS:
    src, dst = os.path.join(R, old), os.path.join(R, new)
    text = io.open(src, encoding="utf-8", newline="").read()
    new_text = text
    for a, b in rules:
        assert a in new_text, "face missing in %s: %s" % (old, a)
        new_text = new_text.replace(a, b)
    assert "r304" not in new_text, "stray r304 face in %s" % new
    diff = list(difflib.unified_diff(
        text.splitlines(True), new_text.splitlines(True), old, new))
    delta = sum(1 for l in diff
                if (l.startswith("+") and not l.startswith("+++"))
                or (l.startswith("-") and not l.startswith("---")))
    assert delta == expected, "%s delta=%d expected=%d" % (new, delta, expected)
    io.open(dst, "w", encoding="utf-8", newline="").write(new_text)
    print("%s -> %s delta=%d==expected OK" % (old, new, delta))
