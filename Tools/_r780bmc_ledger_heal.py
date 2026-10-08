"""r780 bm-c ledger heal: r771-r779 rows (10 lines, ROOT orphan face tail
lines 706-715) verbatim row-level union into the canonical face
logs/iteration-loop/round_reports-bm-c.md (r645 epoch-merge law; r749
recurrence x9 healed by r750/r865 mirror recipe). ROOT face untouched
(frozen per r645). Byte-conservation receipt ->
results/_r780bmc_ledger_heal_receipt.json."""
import hashlib
import json
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORPHAN = os.path.join(ROOT_DIR, "round_reports-bm-c.md")
CANON = os.path.join(ROOT_DIR, "logs", "iteration-loop",
                     "round_reports-bm-c.md")
RECEIPT = os.path.join(ROOT_DIR, "results", "_r780bmc_ledger_heal_receipt.json")
ROW_PAT = "| r77"


def main():
    with open(ORPHAN, "rb") as fh:
        orphan_bytes = fh.read()
    orphan_lines = orphan_bytes.split(b"\n")
    # select the r771-r779 block = trailing contiguous rows matching the
    # round-label pattern (scan from tail, stop at first non-match)
    block = []
    for line in reversed(orphan_lines):
        if line.strip() == b"" and not block:
            continue  # skip trailing empty tail element only
        if ROW_PAT.encode() in line and (b" r77" in line):
            block.append(line)
        else:
            break
    block.reverse()
    block_bytes = b"\n".join(block) + b"\n"

    with open(CANON, "rb") as fh:
        canon_before = fh.read()
    canon_before_size = len(canon_before)
    canon_before_sha = hashlib.sha256(canon_before).hexdigest()

    # idempotency guard: rows already on canonical face -> zero append
    already = sum(1 for l in canon_before.split(b"\n") if b"| r779 " in l)
    if already:
        receipt = {"status": "ALREADY_HEALED", "appended_rows": 0,
                   "already_r779_rows_on_canon": already}
        with open(RECEIPT, "w", encoding="utf-8") as fh:
            json.dump(receipt, fh, indent=1)
        print(json.dumps(receipt, indent=1))
        return 0

    joiner = b"" if canon_before.endswith(b"\n") else b"\n"
    canon_after = canon_before + joiner + block_bytes
    with open(CANON, "wb") as fh:
        fh.write(canon_after)

    # verify: re-read, byte-conservation + row parse + orphan untouched
    with open(CANON, "rb") as fh:
        canon_check = fh.read()
    with open(ORPHAN, "rb") as fh:
        orphan_check = fh.read()

    rows_appended = [l for l in block if l.strip()]
    round_labels = [l.decode("utf-8", "replace").split(" | ")[1]
                    for l in rows_appended if b" | " in l]
    receipt = {
        "status": "HEALED",
        "orphan_untouched": orphan_check == orphan_bytes,
        "orphan_size": len(orphan_bytes),
        "orphan_sha256": hashlib.sha256(orphan_bytes).hexdigest(),
        "canon_size_before": canon_before_size,
        "canon_size_after": len(canon_check),
        "canon_sha_before": canon_before_sha,
        "canon_sha_after": hashlib.sha256(canon_check).hexdigest(),
        "appended_row_count": len(rows_appended),
        "appended_bytes": len(joiner) + len(block_bytes),
        "byte_conservation": len(canon_check) == canon_before_size
                             + len(joiner) + len(block_bytes),
        "appended_block_in_canon_verbatim":
            canon_check.endswith(block_bytes),
        "round_labels": round_labels,
        "law_ref": "r645 epoch merge + r749/r750 heal mirror + row-level "
                   "union per S0-restore rc3 carve-out",
    }
    ok = (receipt["orphan_untouched"] and receipt["byte_conservation"]
          and receipt["appended_block_in_canon_verbatim"]
          and receipt["appended_row_count"] == 10)
    receipt["all_asserts_pass"] = bool(ok)
    with open(RECEIPT, "w", encoding="utf-8") as fh:
        json.dump(receipt, fh, indent=1)
    print(json.dumps(receipt, indent=1))
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
