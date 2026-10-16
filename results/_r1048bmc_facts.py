# -*- coding: utf-8 -*-
# r1048 bm-c: gather commit-level facts for the W251 five-face freeze splice editor.
import subprocess, os

def git(*a):
    return subprocess.run(["git"] + list(a), capture_output=True).stdout.decode("utf-8", "replace")

for p in ("fleet/inbox/MSG-20261016-085x-bmc-w251-seat.md",
          "fleet/inbox/processed/MSG-20261016-085x-bmc-w251-seat.md"):
    if os.path.exists(p):
        print("SEAT_PATH:", p)

r = git("log", "--diff-filter=A", "--format=%H", "--",
        "fleet/inbox/MSG-20261016-085x-bmc-w251-seat.md",
        "fleet/inbox/processed/MSG-20261016-085x-bmc-w251-seat.md")
print("seat_add_sha:", (r.strip().splitlines() or ["n/a"])[0])

r = git("log", "--format=%H %s", "-3", "--",
        "fleet/inbox/MSG-20261016-085x-bmc-w251-seat.md",
        "fleet/inbox/processed/MSG-20261016-085x-bmc-w251-seat.md")
print("seat_log:")
for line in r.strip().splitlines():
    print("  ", line[:160])

print("w251_prereg_sha:", git("log", "--diff-filter=A", "--format=%H", "--",
      "research/PERPETUAL_N1_W251_PREREG.md").strip())
print("w251_receipt_sha:", git("log", "--diff-filter=A", "--format=%H", "--",
      "results/_w251bmc_20261016_probe_receipt.json").strip())
print("w250_freeze_sha:", git("log", "--format=%H", "-S", '250: {"a"', "--",
      "scripts/perpetual_faces.py").strip().splitlines()[:2])
print("w250_prereg_sha:", git("log", "--diff-filter=A", "--format=%H", "--",
      "research/PERPETUAL_N1_W250_PREREG.md").strip())

# W250 registered row sanity (live)
import sys
sys.path.insert(0, "scripts")
import perpetual_faces as pf
W250 = pf.N1_BANDS.get(250) or {}
print("W250_row:", W250)
print("W239_a:", pf.N1_BANDS[239]["a"], "W239_b:", pf.N1_BANDS[239]["b_exit"])
# ordinal faces live
owner_rows = [w for w, c in pf.N1_BANDS.items() if (c or {}).get("engine_owner")]
bma_rows = [w for w, c in pf.N1_BANDS.items() if (c or {}).get("engine_owner") == "bm-a"]
bmc_rows = [w for w, c in pf.N1_BANDS.items() if (c or {}).get("engine_owner") == "bm-c"]
print("owner_rows:", len(owner_rows), "bma:", len(bma_rows), "bmc:", len(bmc_rows))
print("max wave:", max(pf.N1_BANDS.keys()))
