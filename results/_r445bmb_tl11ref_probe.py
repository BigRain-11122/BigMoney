# -*- coding: utf-8 -*-
"""_r445bmb_tl11ref_probe.py -- scan the W12 draft for every tl11.<attr>
reference and verify it against the FROZEN tl11 module's real exports.
Read-only (imports tl11 which loads data faces, same as selftest)."""
import re
import sys

sys.path.insert(0, "scripts")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import trial_labor_w11 as tl11  # noqa: E402

src = open("results/_r445bmb_w12_runner_draft.py", encoding="utf-8").read()
refs = sorted(set(re.findall(r"tl11\.([A-Za-z_][A-Za-z0-9_]*)", src)))
bad = []
for r in refs:
    ok = hasattr(tl11, r)
    print(("OK  " if ok else "BAD "), "tl11." + r)
    if not ok:
        bad.append(r)
print("=== %d refs, %d BAD ===" % (len(refs), len(bad)))
