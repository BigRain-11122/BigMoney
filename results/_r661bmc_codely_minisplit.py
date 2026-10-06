# -*- coding: utf-8 -*-
"""r661 bm-c CODELY over-gate minisplit (r651/r654 same-window duty): the tail
commit landed CODELY.md at 30816B > 30720B gate (561B pit line, my ~260B size
estimate was wrong for CJK UTF-8; assert fired AFTER the append write).
Cure = verbatim-migrate one complete main-file pit entry (r656 commit
attribution, pit-git domain) out of CODELY.md into research/pit-git.md,
byte-exact move, sha16 accounting receipt, gate assert on the AFTER size.
Pattern credit: Tools/_r654bmc_codely_increment.py lineage."""
import hashlib
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "CODELY.md")
DST = os.path.join(ROOT, "research", "pit-git.md")
MARKER = "- [2026-10-07 05:2x r656 bm-c]".encode("utf-8")
GATE = 30720

raw = open(SRC, "rb").read()
before = len(raw)
idx = raw.find(MARKER)
assert idx >= 0, "r656 marker not found in CODELY.md"
start = raw.rfind(b"\n", 0, idx) + 1
end = raw.find(b"\n", idx)
if end < 0:
    end = len(raw)
    eol_included = b""
else:
    end += 1
    eol_included = b"\r\n" if raw[end - 2:end] == b"\r\n" else b"\n"
block = raw[start:end]
assert block.startswith(MARKER), "block boundary wrong"

new_main = raw[:start] + raw[end:]
open(SRC, "wb").write(new_main)

d_raw = open(DST, "rb").read()
d_before = len(d_raw)
pre = b"" if (not d_raw or d_raw.endswith(b"\n")) else b"\n"
open(DST, "ab").write(pre + block)
d_new = open(DST, "rb").read()

after = len(open(SRC, "rb").read())
assert block in d_new, "verbatim assert: block not byte-present in target"
assert after <= GATE, "CODELY.md still over gate: %d" % after
assert (len(d_new) - len(d_raw)) == len(pre) + len(block)

receipt = {
    "probe": "r661 bm-c CODELY over-gate minisplit (r651/r654 same-window law)",
    "cause": "tail commit landed CODELY.md 30816B > 30720B gate (561B pit line vs ~260B estimate; CJK UTF-8)",
    "migrated": {
        "entry": "r656 commit-attribution pit ([via bm-x rNNN] suffix = sole machine-attribution authority)",
        "src": "CODELY.md", "dst": "research/pit-git.md",
        "bytes": len(block), "sha16": hashlib.sha256(block).hexdigest()[:16],
        "verbatim_assert": True,
    },
    "codely_before": before, "codely_after": after, "gate": GATE,
    "dst_before": d_before, "dst_after": len(d_new),
}
with open(os.path.join(ROOT, "results", "_r661bmc_codely_minisplit.json"),
          "w", encoding="utf-8", newline="\n") as fh:
    json.dump(receipt, fh, ensure_ascii=False, indent=1)
print("minisplit OK: CODELY %d->%d (gate %d, headroom %d); pit-git %d->%d; "
      "block %dB sha16=%s" % (
          before, after, GATE, GATE - after, d_before, len(d_new),
          len(block), receipt["migrated"]["sha16"]))
