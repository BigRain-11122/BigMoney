# -*- coding: utf-8 -*-
"""r794 bm-a takeover: independent audit of derived W165 tools (era
consistency of band tuples + key anchor values across all four tools)."""
import io
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

EXPECT_ERA = {
    # canonical N1_BANDS rows the W165 tools must reference
    "W165_new":  ("377_804", "379_803"),   # row 165 the freeze ADDS
    "W164_cur":  ("375_604", "377_603"),   # row 164 current canonical
    "W163_old":  ("373_404", "375_403"),   # row 163 historical
    "W166_prev": ("379_804", "381_803"),   # next-wave preview (range form)
}

fails = []
for tool in ("face_probe", "prereg_build", "freeze_edits", "freeze_verify"):
    p = f"results/_r794bma_w165_{tool}.py"
    s = io.open(p, encoding="utf-8", newline="").read()
    # every dotted band pair must be era-pure (both members differ by exactly
    # the canonical band widths; catch mixed-era leftovers)
    pairs = set(re.findall(r"(3\d{2}_\d{4}|3\d{2}_\d{3}), (3\d{2}_\d{3})\)", s))
    pairs = set(re.findall(r"\((3\d{2}_\d{3}), (3\d{2}_\d{3})\)", s))
    for a, b in sorted(pairs):
        va, vb = int(a.replace("_", "")), int(b.replace("_", ""))
        if vb - va not in (1999, 199, 2000, 200):
            fails.append(f"{tool}: suspicious tuple ({a}, {b}) delta={vb-va}")
    print(f"{tool}: {len(pairs)} distinct tuples, {len(s)} bytes")

# era presence checks (canonical faces must be present)
s = io.open("results/_r794bma_w165_freeze_verify.py", encoding="utf-8").read()
for label, (a, b) in EXPECT_ERA.items():
    form = f"{a}..{b}" if label == "W166_prev" else f"({a}, {b})"
    if form not in s:
        fails.append(f"freeze_verify missing {label} {form}")
if "[-1] == 165 and len(pf.N1_BANDS) == 163" not in s:
    fails.append("freeze_verify row-count composite missing")
if '"766,212" in n2' not in s:
    fails.append("freeze_verify positive ledger assert missing")
if '"377_403", "764,012", "356,520"' not in s:
    fails.append("freeze_verify stale-list advanced face missing")

s = io.open("results/_r794bma_w165_freeze_edits.py", encoding="utf-8").read()
for needle in ('("@LEDG@", "766,212")', "('764,012', \"@LEDG@\")",
               "ledger head 766,212", "chain head 766,212"):
    if needle not in s:
        fails.append(f"freeze_edits missing {needle!r}")

s = io.open("results/_r794bma_w165_prereg_build.py", encoding="utf-8").read()
for needle in ("PERPETUAL_N1_W165_PREREG.md", "line_pre 1.1832",
               "K-lift **+0.0001**", "0.000409"):
    if needle not in s:
        fails.append(f"prereg_build missing {needle!r}")

if fails:
    print("AUDIT FAIL:")
    for f in fails:
        print(" -", f)
    raise SystemExit(1)
print("AUDIT PASS: all four derived W165 tools era-consistent + anchors green")
