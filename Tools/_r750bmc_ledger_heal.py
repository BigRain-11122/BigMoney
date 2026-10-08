# -*- coding: utf-8 -*-
"""r750 bm-c ledger cross-face heal: r749 report row had landed on the FROZEN
ROOT face (round_reports-bm-c.md, r645 epoch-freeze 'ben-jiang ting-xie' note)
because the r749 close clone mechanically applied bm-a's r844/r865 ROOT-path
law. bm-c canonical face = logs/iteration-loop/round_reports-bm-c.md per
fleet/README.md sec.6 + the r645 freeze note inside the ROOT face itself.
This heal mirrors bm-a's r865-heal pattern: append the r749 row VERBATIM
(byte-exact, extracted from the ROOT face) + a dated heal-note row to the
canonical face; ROOT face left untouched (append-only, git history preserved).
Receipt -> results/_r750bmc_ledger_heal_receipt.json."""
import datetime
import hashlib
import json

ROOT_FACE = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\round_reports-bm-c.md"
CANON = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\logs\iteration-loop\round_reports-bm-c.md"
RECEIPT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r750bmc_ledger_heal_receipt.json"
NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")

root_raw = open(ROOT_FACE, "rb").read()
root_sha_before = hashlib.sha256(root_raw).hexdigest()
rows = [ln for ln in root_raw.splitlines() if b"| r749 |" in ln]
assert len(rows) == 1, "expected exactly 1 r749 row on ROOT face, got %d" % len(rows)
r749_row = rows[0]

canon_raw = open(CANON, "rb").read()
assert canon_raw.count(b"| r749 |") == 0, "r749 row already present in canonical face"
eol = b"\r\n" if b"\r\n" in canon_raw[-200:] else b"\n"
canon_size_before = len(canon_raw)

heal_row = (
    "2026-10-08T" + NOW[11:16] + "+08:00 | r750 heal | bm-c | ledger cross-face heal: "
    "r749 report row had landed on the FROZEN ROOT face (round_reports-bm-c.md, r645 "
    "epoch-freeze \u672c\u4ef6\u505c\u5199 note violated by the r749 close clone mechanically "
    "applying bm-a's r844/r865 ROOT-path law) instead of bm-c canonical "
    "(logs/iteration-loop/round_reports-bm-c.md per fleet/README \u00a76 + r645 freeze note); "
    "this heal appends the r749 row verbatim below (extracted from ROOT face bytes); "
    "ROOT face left untouched (append-only git history preserved); "
    "receipt=results/_r750bmc_ledger_heal_receipt.json. [via bm-c r750]"
).encode("utf-8")

if not canon_raw.endswith(eol):
    canon_raw += eol
new_canon = canon_raw + heal_row + eol + r749_row + eol
with open(CANON, "wb") as fh:
    fh.write(new_canon)

# self-verify (write-then-grep, r865 law applied to the CANONICAL face)
back = open(CANON, "rb").read()
assert back.count(b"| r749 |") == 1, "r749 row not exactly-once in canonical after heal"
assert b"r750 heal | bm-c | ledger cross-face heal" in back, "heal note missing"
root_sha_after = hashlib.sha256(open(ROOT_FACE, "rb").read()).hexdigest()
assert root_sha_after == root_sha_before, "ROOT face was modified - must stay untouched"

receipt = {
    "round": 750,
    "heal_kind": "cross-face stray-row verbatim re-migration (r865-heal mirror)",
    "strayed_face": "round_reports-bm-c.md (ROOT, r645 frozen)",
    "canonical_face": "logs/iteration-loop/round_reports-bm-c.md",
    "row_bytes": len(r749_row),
    "row_sha16": hashlib.sha256(r749_row).hexdigest()[:16],
    "heal_note_bytes": len(heal_row),
    "canon_size_before": canon_size_before,
    "canon_size_after": len(new_canon),
    "root_sha256_unchanged": True,
    "eol": repr(eol),
    "ts": NOW,
}
with open(RECEIPT, "w", encoding="utf-8") as fh:
    json.dump(receipt, fh, indent=1)
print("healed: r749 row %dB sha16=%s -> canonical (root face untouched, sha match)" % (
    len(r749_row), receipt["row_sha16"]))
