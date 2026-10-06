# -*- coding: utf-8 -*-
"""r794 bm-a: extract the FULL se_mu chain line + the KLC/SIG/MU/P95 prose
lines from the frozen W164 prereg, plus the same lines from the W163 prereg,
to pin the exact chain-window convention."""
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

for sha, label in (("18231a529", "W163 prereg"),
                   ("f7d34e5a7", "W164 prereg")):
    raw = subprocess.run(
        ["git", "show", f"{sha}:research/PERPETUAL_N1_W163_PREREG.md"
         if label == "W163 prereg" else
         f"{sha}:research/PERPETUAL_N1_W164_PREREG.md"],
        capture_output=True).stdout
    txt = raw.decode("utf-8")
    print(f"=== {label} ({len(raw)} bytes) ===")
    for ln in txt.split("\n"):
        if "0.00041" in ln or "0.00042" in ln:
            print("CHAIN-LINE:", ln.strip()[:400])
    for ln in txt.split("\n"):
        if "se_mu" in ln and "0.0004" not in ln:
            print("SEC-CONTEXT:", ln.strip()[:200])
    print()
