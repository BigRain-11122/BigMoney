# -*- coding: utf-8 -*-
"""One-off probe: inventory of band tokens / wave literals in the W309 splice editor."""
import collections
import io
import json
import re

s = io.open("results/_w309bmc_freeze_edits.py", encoding="utf-8").read()
b = collections.Counter(re.findall(r"\b\d{3}_\d{3}\b", s))
keys = ["wave 309", '"wave": 308', '308: {"batch"', '308: {{"a"', "166 parity rows",
        "167 parity rows", "legs (", "SIXTY", "HUNDRED-AND", "THREE HUNDRED",
        "range(303", "(expect 298/130/127)", "1_101_941", "675_520", "692_701"]
out = {"bands": dict(sorted(b.items())), "counts": {k: s.count(k) for k in keys}}
io.open("results/_w310bmc_editor_inv.json", "w", encoding="utf-8").write(
    json.dumps(out, ensure_ascii=False, indent=1))
print("ok")