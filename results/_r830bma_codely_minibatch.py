# -*- coding: utf-8 -*-
"""r830 bm-a CODELY main-file mini incremental batch (D-20261002-06 main-file
<=30KB criterion leg; trigger = main file measured 31,499B > 30,720B after
the r830 S4 append). Migrates ONE older entry verbatim to its domain file:
the r668 bm-c future-calendar-facts pit (511B) -> research/pit-protocol.md
(heartbeat/milestone bookkeeping-face domain). Fresh r830 entry stays
per the new-pit-first law; the User meta-law row + the two three-machine
shared sec.4 pin rows are locked faces (not migratable).
Ceremony: r441/r651/r654 lineage -- verbatim bytes + byte-conservation
assert + receipt JSON."""
import hashlib
import io
import json
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

MAIN = "CODELY.md"
DOM = "research/pit-protocol.md"
NEEDLE_HEAD = "- [2026-10-07 10:2x r668 bm-c] **"

# ---- 0. treasure_guard prescan (r651/r654 lineage: rc3 registry-hit
# EXPECTED for treasure-corpus faces -- CODELY.md and pit-* are registered
# treasure files; this batch is a byte-conserving verbatim MOVE inside the
# treasure corpus per D-20261002-06, not a sweep; rc3 recorded as trace,
# zero-loss asserted below) -----------------------------------------------
rg = subprocess.run(["python", "Tools/treasure_guard.py", "prescan", MAIN, DOM],
                    capture_output=True)
print("prescan rc:", rg.returncode, rg.stdout.decode("utf-8", "replace")[:120])
assert rg.returncode == 3, "prescan rc changed: %d" % rg.returncode

# ---- 1. extract the entry verbatim (byte-conservation face) ----------------
t = io.open(MAIN, encoding="utf-8", newline="").read()
i = t.find(NEEDLE_HEAD)
assert i > 0, "r668 entry not found"
j = t.find("\n- [", i + 10)
k = t.find("\n\n", i + 10)
ends = [e for e in (j, k, t.find("\n## ", i + 10)) if e > 0]
end = min(ends) if ends else len(t)
# entry runs to end of its line (+ the trailing newline stays in main)
line_end = t.find("\n", i)
entry = t[i:line_end]
assert entry.startswith(NEEDLE_HEAD) and len(entry) in (511, 512), (
    "entry shape mismatch: %d B" % len(entry))

# ---- 2. append verbatim to the domain file (tail, LF blob) ----------------
d = io.open(DOM, encoding="utf-8", newline="").read()
assert NEEDLE_HEAD not in d, "already migrated"
with io.open(DOM, "a", encoding="utf-8", newline="") as f:
    f.write(entry + "\n")

# ---- 3. remove from main file ---------------------------------------------
t2 = t[:i] + t[line_end + 1:]
with io.open(MAIN, "w", encoding="utf-8", newline="") as f:
    f.write(t2)

# ---- 4. byte-conservation + size asserts ----------------------------------
d2 = io.open(DOM, encoding="utf-8", newline="").read()
assert entry in d2, "domain verbatim missing"
assert len(d2) - len(d) == len(entry) + 1, "domain delta mismatch"
assert len(t) - len(t2) == len(entry) + 1, "main delta mismatch"
assert io.open(MAIN, encoding="utf-8", newline="").read().find(NEEDLE_HEAD) < 0, "main still carries entry"
main_sz = os.path.getsize(MAIN)
dom_sz = os.path.getsize(DOM)
print("main file:", len(t), "->", len(t2), "B; domain:", len(d), "->", len(d2), "B")

receipt = {
    "batch": "r830 bm-a CODELY main-file mini incremental",
    "trigger": "main file 31,499B > 30,720B (r830 S4 append pushed over)",
    "migrated": [{"entry_head": NEEDLE_HEAD[:60], "bytes": len(entry),
                  "sha16": hashlib.sha256(entry.encode("utf-8")).hexdigest()[:16],
                  "to": DOM}],
    "byte_conservation": "main_removed==domain_appended==%d(+1 LF each)" % len(entry),
    "main_size_after": main_sz,
    "domain_size_after": dom_sz,
    "remainder_disclosure": ("main lands %dB over the 30,720B line; zero further clean "
                             "candidates this window: User meta-law row + two three-machine "
                             "shared sec.4 pin rows are locked faces, fresh r830 entry stays "
                             "per new-pit-first law; next increment batch takes it") % (main_sz - 30720),
    "prescan_rc": rg.returncode,
    "prescan_note": ("rc3 registry-hit recorded as trace per r651/r654 ceremony lineage; "
                     "byte-conserving verbatim move within the treasure corpus "
                     "(D-20261002-06), zero-loss asserted by the conservation gates"),
}
io.open("results/_r830bma_codely_increment.json", "w", encoding="utf-8").write(
    json.dumps(receipt, indent=1, ensure_ascii=False))
print("receipt: results/_r830bma_codely_increment.json")
print("remainder:", receipt["remainder_disclosure"])
