# -*- coding: utf-8 -*-
"""r913 bm-c: round-report books union migration (r855 precedent, third recurrence of the
dead-path-constant books bug). Ledger-class files -> LINE-LEVEL UNION ONLY (treasure_guard
rc3 verdict honored: zero deletion, zero rewrite; both sides append-only).
- canonical: logs/iteration-loop/round_reports-bm-c.md  (appends root-only lines, file order)
- root dead-position: round_reports-bm-c.md             (appends tombstone guard row only)
Byte-precise, UTF-8, EOL preserved from canonical file."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CANON = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")
DEAD = os.path.join(ROOT, "round_reports-bm-c.md")

canon_bytes = open(CANON, "rb").read()
dead_bytes = open(DEAD, "rb").read()
# detect canonical EOL to append with the same terminator
crlf = b"\r\n" if b"\r\n" in canon_bytes else b"\n"
canon_set = set(canon_bytes.splitlines())
dead_lines = dead_bytes.splitlines()

missing = []
for ln in dead_lines:
    if ln not in canon_set and ln.strip():
        missing.append(ln)

# skip lines that are already tombstone guards from earlier migrations
TOMB_MARKERS = (b"[healed", b"tombstone", b"TOMBSTONE", b"migrated")
missing = [m for m in missing if not any(t in m for t in TOMB_MARKERS)]

print("root-position lines total:", len(dead_lines))
print("missing-from-canonical (to union):", len(missing))

out_parts = []
if missing:
    # append with a surgery header line? No -- zero header, pure line-level union (r855 law).
    for m in missing:
        out_parts.append(m + crlf)
    with open(CANON, "ab") as f:
        f.write(b"".join(out_parts))
    print("canon appended:", len(missing), "lines")

tomb = ("[healed r913 bm-c] dead-position books file (r645-lineage dead path constant, THIRD recurrence "
        "r893-r911 window): all unique lines union-migrated verbatim to "
        "logs/iteration-loop/round_reports-bm-c.md this window (r855 surgery precedent, line-level "
        "union per treasure_guard rc3 verdict -- zero deletion zero rewrite, this file byte-preserved "
        "above; NEW round report lines must be written to the CANONICAL position only; "
        "missing rounds r890/r898-r906/r908-r910/r912 = dead sessions absorbed per r907/r911 "
        "heal notes, live in commit log + state face)").encode("utf-8") + crlf
with open(DEAD, "ab") as f:
    f.write(tomb)
print("tombstone guard appended to dead-position file")

# verify: every non-tombstone root line now present in canonical
canon_after = set(open(CANON, "rb").read().splitlines())
still_missing = [ln for ln in dead_lines
                 if ln.strip() and ln not in canon_after and not any(t in ln for t in TOMB_MARKERS)]
print("post-verify still-missing:", len(still_missing))
sys.exit(0 if not still_missing else 1)
