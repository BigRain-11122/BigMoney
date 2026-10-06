# -*- coding: utf-8 -*-
"""r662 bm-c CODELY over-gate minisplit (r651/r654/r661 same-window duty):
S4 pit append (QA-ignite bare-number clone pit, 879B) landed CODELY.md at
30848B > 30720B gate (main was 29969B with 751B headroom; entry overran).
Cure = verbatim-migrate two complete main-file pit entries out of CODELY.md
into research/pit-protocol-lane.md (state-bookkeeping/race + append-only
ledger mechanics family; r640/r646 lineage home, 6882B has room):
  (a) r644 QA default round-label pit (state+1 vs in-flight round, r758 law)
  (b) r661 close % format crash + RR/state half-way pit (idempotency gate)
Byte-exact move, sha16 accounting receipt, gate assert on AFTER size.
Prescan recorded: rc3 registry hit (CODELY.md + pit-protocol-lane.md,
research/ fail-closed family) per r651/r654/r661 lineage.
Pattern credit: results/_r661bmc_codely_minisplit.py."""
import hashlib
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "CODELY.md")
DST = os.path.join(ROOT, "research", "pit-protocol-lane.md")
GATE = 30720

MARKERS = [
    b"- [2026-10-07 00:3x r644 bm-c]",
    b"- [2026-10-07 07:3x r661 bm-c]",
]


def block_of(raw, marker):
    idx = raw.find(marker)
    assert idx >= 0, "marker not found: %r" % marker
    start = raw.rfind(b"\n", 0, idx) + 1
    end = raw.find(b"\n", idx)
    assert end >= 0, "entry line has no terminator"
    end += 1
    block = raw[start:end]
    assert block.startswith(marker), "block boundary wrong"
    return start, end, block


raw = open(SRC, "rb").read()
before = len(raw)
spans = [block_of(raw, m) for m in MARKERS]
assert spans[0][0] < spans[1][0], "marker order unexpected"
assert spans[0][1] <= spans[1][0], "blocks overlap"

s1, e1, b1 = spans[0]
s2, e2, b2 = spans[1]
new_main = raw[:s1] + raw[e1:s2] + raw[e2:]
open(SRC, "wb").write(new_main)

d_raw = open(DST, "rb").read()
d_before = len(d_raw)
pre = b"" if (not d_raw or d_raw.endswith(b"\n")) else b"\n"
open(DST, "ab").write(pre + b1 + b2)
d_new = open(DST, "rb").read()

after = len(open(SRC, "rb").read())
assert b1 in d_new and b2 in d_new, "verbatim assert: block not byte-present in target"
assert after <= GATE, "CODELY.md still over gate: %d" % after
assert (len(d_new) - len(d_raw)) == len(pre) + len(b1) + len(b2)
assert new_main == open(SRC, "rb").read()

receipt = {
    "probe": "r662 bm-c CODELY over-gate minisplit (r651/r654/r661 same-window law)",
    "cause": "S4 pit append (QA-ignite bare-number clone pit) landed main 30848B > 30720B gate",
    "prescan_rc": 3,
    "prescan_note": "treasure_guard prescan rc3 registry hit recorded per lineage: CODELY.md + research/pit-protocol-lane.md (research/ fail-closed family); verbatim zero-loss migration under D-20261002-06 authority, not a deletion",
    "migrated": [
        {"entry": "r644 QA default round-label pit (state+1 x in-flight round, r758 override law)",
         "src": "CODELY.md", "dst": "research/pit-protocol-lane.md",
         "bytes": len(b1), "sha16": hashlib.sha256(b1).hexdigest()[:16],
         "verbatim_assert": True},
        {"entry": "r661 close % format crash + RR/state half-way pit (idempotency gate law)",
         "src": "CODELY.md", "dst": "research/pit-protocol-lane.md",
         "bytes": len(b2), "sha16": hashlib.sha256(b2).hexdigest()[:16],
         "verbatim_assert": True},
    ],
    "codely_before": before, "codely_after": after, "gate": GATE,
    "dst_before": d_before, "dst_after": len(d_new),
    "retained_face_identity": "new_main == raw minus exactly the two migrated blocks",
}
with open(os.path.join(ROOT, "results", "_r662bmc_codely_minisplit.json"),
          "w", encoding="utf-8", newline="\n") as fh:
    json.dump(receipt, fh, ensure_ascii=False, indent=1)
print("minisplit OK: CODELY %d->%d (gate %d, headroom %d); "
      "pit-protocol-lane %d->%d; blocks %dB+%dB sha16=%s/%s" % (
          before, after, GATE, GATE - after, d_before, len(d_new),
          len(b1), len(b2), receipt["migrated"][0]["sha16"],
          receipt["migrated"][1]["sha16"]))
