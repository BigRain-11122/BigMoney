# -*- coding: utf-8 -*-
"""r893 bm-a W191 buildgen fact probe: machine-derive all W191-chain shas
and counts (r587 law: zero hand-copied facts in the buildgen)."""
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def g(args):
    return subprocess.run(args, capture_output=True, text=True,
                          encoding="utf-8", errors="replace").stdout.strip()


subprocess.run(["git", "fetch", "origin"], capture_output=True)
r = g(["git", "log", "origin/main", "--format=%h", "-n", "1", "-S",
       '190: {"a": (432_804', "--", "scripts/perpetual_faces.py"])
print("W190_REG_SHA:", r)
print("W191_FREEZE_grep:", g(["git", "log", "origin/main", "--format=%h",
                             "--grep=W191 five-face freeze", "-1"]) or "(empty)")
print("W191_FREEZE2:", g(["git", "log", "origin/main", "--format=%h",
                          "--grep=W191 FREEZE", "-1"]) or "(empty)")
print("W191_PREREG_GREP:", g(["git", "log", "origin/main", "--format=%h",
                              "--grep=per-wave prereg freeze", "-1"]) or "(empty)")
for p in ("fleet/inbox/MSG-2026-10-08-2130-bma-w191-seat.md",
          "fleet/inbox/processed/MSG-2026-10-08-2130-bma-w191-seat.md"):
    r1 = g(["git", "log", "origin/main", "--format=%h %ci", "-n", "1",
            "--diff-filter=A", "--", p])
    print("SEAT_ADD:", p, "->", r1)
print("BLOB_8394:", g(["git", "rev-parse",
                       "8394b75ea:research/PERPETUAL_N1_W190_PREREG.md"]))
print("BLOB_0cce:", g(["git", "rev-parse",
                        "0cce3c47e:research/PERPETUAL_N1_W190_PREREG.md"]))
sys.path.insert(0, "scripts")
sys.path.insert(0, ".")
import science_gates as sg  # noqa: E402
print("REG_N:", len(sg.SEED_REGISTRY))
for p in ("fleet/inbox/MSG-2026-10-08-2130-bma-w191-seat.md",
          "fleet/inbox/processed/MSG-2026-10-08-2130-bma-w191-seat.md"):
    rc = subprocess.run(["git", "show", "origin/main:" + p],
                        capture_output=True).returncode
    print("ORIGIN_HAS:", p, rc == 0)
# W190 backfill citation live-check (r893 first-leg landed this window)
import io  # noqa: E402
w = io.open(r"research\PERPETUAL_N1_W190_PREREG.md", encoding="utf-8",
            newline="").read()
for n in ("825,328", "K=415,920", "r893 \u56de\u586b\u7a97"):
    print("BACKFILL_NEEDLE:", n, n in w)
