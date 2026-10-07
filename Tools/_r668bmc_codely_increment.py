# -*- coding: utf-8 -*-
"""r668 bm-c CODELY increment batch (D-20261002-06 main <=30,720B rule leg).

Migration ceremony r783/r789/r651/r654/r667 lineage:
- Migrate r814 bm-a watermark-write-side pit (1 entry, 758B incl CR, sha16
  3598f944144aaa01) verbatim OUT of main -> research/pit-protocol-d19.md
  (D-19 watermark family, 14.6KB headroom) + in-file accounting line.
- Append new r668 pit line (future-calendar-facts verification law,
  reopen-date 10-09 -> 10-08 erratum) to main.
- Byte equations + verbatim-in-target + marker-absence + CRLF three-count
  (r402) + reparse gates; receipt results/_r668bmc_codely_increment.json.
- prescan rc3 recorded (registry hits, r651/r654 operative precedent:
  verbatim zero-loss relocation, not deletion, registry rows untouched).
All writes CRLF-preserving (main + target both CRLF files)."""
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN = os.path.join(ROOT, "CODELY.md")
TARGET = os.path.join(ROOT, "research", "pit-protocol-d19.md")
RECEIPT = os.path.join(ROOT, "results", "_r668bmc_codely_increment.json")
CAP = 30720

R814_NEEDLE = b"[2026-10-07 08:4x r814 bm-a]"
NEW_LINE = (
    "- [2026-10-07 10:2x r668 bm-c] **\u672a\u6765\u65e5\u5386\u4e8b\u5b9e\u672a\u6838\u9a8c\u5199 CEO \u9762\u5751\uff08\u590d\u5e02\u65e5\u9519\u62a5\u52d8\u8bef\u00b710-09\u219210-08\uff09**\uff1a"
    "r666/r667 \u5fc3\u8df3+state \u5199\u300c10-09 \u590d\u5e02\u300d=\u9519\u2014\u2014\u56fd\u52a1\u9662\u529e\u516c\u5385 2026 \u8282\u5047\u65e5\u901a\u77e5\uff08\u5916\u6e90\u4e09\u6e90\u4ea4\u53c9\uff09="
    "\u56fd\u5e86 10-01\uff08\u5468\u56db\uff09~10-07\uff08\u5468\u4e09\uff09\u4f11\u30019-20/10-10 \u8c03\u4f11\u4e0a\u73ed\uff1bA \u80a1\u590d\u5e02\u9996\u4ea4\u6613\u65e5=10-08\uff08\u5468\u56db\uff09\u00b7"
    "10-10 \u8c03\u4f11\u4e0a\u73ed\u65e5\u80a1\u5e02\u7167\u5e38\u4f11\u5e02\uff1bbm-a r714 readiness \u4ef6+bm-b \u5fc3\u8df3\u672c\u6301 10-08=\u4ec5 bm-c \u9762\u5355\u65b9\u9519\uff08r666 close \u6a21\u677f\u5f15\u5165\uff09\u3002"
    "\u6b63\u6cd5=\u672a\u6765\u5e02\u573a\u65e5\u5386\u4e8b\u5b9e\uff08\u590d\u5e02\u65e5/\u5047\u671f\u754c/\u6708\u754c\uff09\u5199\u5165\u5fc3\u8df3/\u91cc\u7a0b\u7891\u524d\u5fc5\u4e24\u6e90\u6838\u9a8c\uff08\u6743\u5a01\u5916\u6e90+\u4ed6\u673a\u6b63\u5178\u4ef6\uff09"
    "\u00b7\u9762\u95f4\u51b2\u7a81\u5373\u5f53\u8f6e\u5916\u6e90\u5b9a\u8c23+\u52d8\u8bef\u7559\u75d5\u3002\u589e\u91cf\u6279\u540c\u7a97\uff1ar814 \u6c34\u4f4d\u5751 verbatim \u8fc1 pit-protocol-d19.md"
    "\uff08sha16 3598f944144aaa01\u00b7\u6536\u636e _r668bmc_codely_increment.json\uff09\u3002"
    "How to apply\uff1a\u5199\u590d\u5e02/\u5047\u671f\u7c7b\u91cc\u7a0b\u7891\u5148\u4e24\u6e90\u4ea4\u53c9\u518d\u843d\u9762\uff1b\u672c\u673a\u9762 10-09 \u5df2 r668 S7 \u52d8\u8bef 10-08\u3002")
ACCT_LINE = (
    "\u589e\u91cf\u56de\u626b\u884c\uff08r668 bm-c\u00b7D-20261002-06 \u4e3b\u4ef6 \u226430KB \u5224\u636e\u817f\u00b7\u8fc1\u79fb\u4eea\u5f0f r783/r789 \u540c\u6b3e\uff09\uff1a"
    "\u4e3b\u4ef6\u56de\u5f39\u589e\u91cf\u5751\u5f8b 1 \u6761 verbatim \u8fc1\u5165\u2014\u2014r814 bm-a \u6c34\u4f4d\u952e\u5199\u4fa7\u574f\u6765\u6e90\u54c8\u5e0c\u5751"
    "\uff08r812 PS \u7ba1\u9053\u5047 CHANGED \u65cf\u5199\u9762\u53d8\u4f53\u00b7S0.5 \u6c34\u4f4d\u6bd4\u5bf9\u4e0e\u5199\u952e\u9762\uff09\u2014\u2014"
    "\u9010\u6761\u5b57\u8282+sha16 \u5bf9\u8d26=receipt results/_r668bmc_codely_increment.json"
    "\uff08\u96f6\u4e22\u5931\u65ad\u8a00=\u9010\u5757 bytes in target verbatim+\u4e3b\u4ef6\u4fdd\u7559\u9762\u6052\u7b49\u5f0f+\u4e3b\u4ef6 \u226430KB+\u5168\u57df\u4ef6 \u226430KB\u00b7prescan rc3 \u7559\u75d5\uff09\uff1b"
    "\u65b0\u5751\u5f8b\u4ecd\u5148\u5165\u4e3b\u4ef6\u540e\u56de\u626b\u3002")


def sha16(b):
    return hashlib.sha256(b).hexdigest()[:16]


def main():
    main_raw = open(MAIN, "rb").read()
    tgt_raw = open(TARGET, "rb").read()
    main_before, tgt_before = len(main_raw), len(tgt_raw)

    lines = main_raw.split(b"\n")
    idx = [i for i, l in enumerate(lines) if R814_NEEDLE in l]
    assert len(idx) == 1, "r814 needle count==1 gate, got %d" % len(idx)
    i = idx[0]
    r814_line = lines[i]                      # content + trailing \r
    assert r814_line.endswith(b"\r"), "r814 CR-tail gate"
    r814_sha16 = sha16(r814_line)
    assert r814_sha16 == "3598f944144aaa01", "r814 sha16 gate %s" % r814_sha16
    # already-migrated gate: signature must not exist in target yet
    assert R814_NEEDLE not in tgt_raw, "already-migrated gate"
    # needle-avoid-furniture (r420): raw needle count in main == 1
    assert main_raw.count(R814_NEEDLE) == 1, "raw needle count gate"

    new_line_b = NEW_LINE.encode("utf-8") + b"\r"
    acct_b = ACCT_LINE.encode("utf-8") + b"\r"

    # ---- byte equations (pre-check, fail-closed) ----
    main_after = main_before - (len(r814_line) + 1) + (len(new_line_b) + 1)
    tgt_after = tgt_before + (len(r814_line) + 1) + (len(acct_b) + 1)
    assert main_after <= CAP, "main cap gate: %d > %d" % (main_after, CAP)
    assert tgt_after <= CAP, "target cap gate: %d > %d" % (tgt_after, CAP)
    # budget guard for the new line itself (round-note: <=937B incl CR)
    assert len(new_line_b) <= 937, "new line budget gate: %d" % len(new_line_b)

    # ---- main surgery: remove r814 line, append r668 line as new tail ----
    assert main_raw.endswith(b"\n"), "main trailing-newline gate"
    body = lines[:-1]                       # real lines, each CR-terminated
    assert body[i] is r814_line
    body2 = body[:i] + body[i + 1:] + [new_line_b]
    main_new = b"\n".join(body2) + b"\n"
    # sanity: exact byte count matches equation
    assert len(main_new) == main_after, "main byte equation: %d != %d" % (len(main_new), main_after)

    # ---- target surgery: append r814 verbatim + accounting line ----
    assert tgt_raw.endswith(b"\n"), "target trailing-newline gate"
    tgt_new = tgt_raw + r814_line + b"\n" + acct_b + b"\n"
    assert len(tgt_new) == tgt_after, "target byte equation"

    # ---- gates ----
    # verbatim-in-target
    assert r814_line in tgt_new, "verbatim-in-target gate"
    # marker-absence in main (full entry signature gone)
    assert R814_NEEDLE not in main_new, "marker-absence gate"
    # r668 new line present in main exactly once
    assert main_new.count(b"[2026-10-07 10:2x r668 bm-c]") == 1, "new-line presence gate"
    # CRLF three-count (r402): every \n preceded by \r in both files
    for name, blob in (("main", main_new), ("target", tgt_new)):
        lf, crlf = blob.count(b"\n"), blob.count(b"\r\n")
        assert lf == crlf, "CRLF three-count gate %s: lf=%d crlf=%d" % (name, lf, crlf)
        blob.decode("utf-8")                       # strict reparse
    # preserved-face identity (r402 same-table-anchor law):
    # split-view of main_new = surviving real lines + new tail + final empty
    surv_expect = body[:i] + body[i + 1:] + [new_line_b]
    assert main_new.split(b"\n") == surv_expect + [b""], "preserved-face identity gate"
    # target preserved-face = strict prefix identity
    assert tgt_new[:len(tgt_raw)] == tgt_raw, "target prefix identity gate"

    with open(MAIN, "wb") as fh:
        fh.write(main_new)
    with open(TARGET, "wb") as fh:
        fh.write(tgt_new)

    receipt = {
        "batch": "r668 bm-c CODELY increment",
        "prescan_rc": 3,
        "prescan_note": "registry hits CODELY.md + pit-protocol-d19.md; r651/r654 operative precedent: verbatim zero-loss relocation, not deletion; registry rows untouched",
        "migrated": [{
            "entry": "r814 bm-a watermark-write-side bad-source-hash pit",
            "bytes_incl_cr": len(r814_line),
            "sha16": r814_sha16,
            "from": "CODELY.md",
            "to": "research/pit-protocol-d19.md",
        }],
        "new_main_line": {"bytes_incl_cr": len(new_line_b), "sha16": sha16(new_line_b)},
        "target_accounting_line": {"bytes_incl_cr": len(acct_b), "sha16": sha16(acct_b)},
        "main_before": main_before, "main_after": len(main_new),
        "main_equation": "%d - %d + %d = %d" % (main_before, len(r814_line) + 1, len(new_line_b) + 1, len(main_new)),
        "target_before": tgt_before, "target_after": len(tgt_new),
        "target_equation": "%d + %d + %d = %d" % (tgt_before, len(r814_line) + 1, len(acct_b) + 1, len(tgt_new)),
        "cap": CAP,
        "gates": ["needle count==1", "sha16 pin", "already-migrated", "raw-needle==1",
                  "main cap", "target cap", "new-line budget<=937", "byte equations x2",
                  "verbatim-in-target", "marker-absence", "new-line presence==1",
                  "CRLF three-count x2", "strict reparse x2", "preserved-face identity",
                  "tail line"],
        "zero_loss": True,
    }
    with open(RECEIPT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(receipt, fh, ensure_ascii=False, indent=1)
    print("INCREMENT OK main %d->%d target %d->%d" % (main_before, len(main_new), tgt_before, len(tgt_new)))
    print("r814 sha16", r814_sha16, "| new line", len(new_line_b), "B | acct", len(acct_b), "B")
    print("receipt", RECEIPT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
