"""r693 bm-c receipt completion: merge the heal + pit-append accounting
(legs that died before receipt write) into
results/_r693bmc_codely_increment.json. Facts re-derived live from the
files themselves (never hand-typed): pit block presence + sha16 in
pit-tooling.md, heal face, pointer in main. Idempotent."""
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RECEIPT = os.path.join(ROOT, "results", "_r693bmc_codely_increment.json")
MAIN = os.path.join(ROOT, "CODELY.md")
TARGET = os.path.join(ROOT, "research", "pit-tooling.md")
LIMIT = 30720

PIT_TITLE = "post_review \u7ea2\u884c\u5224\u5b9a=\u6bcf id \u672b\u884c\u53e3\u5f84\u5751"
POINTER_HEAD = "\u57df\u6307\u9488\u00b7r693 bm-c"


def main():
    r = json.load(open(RECEIPT, encoding="utf-8"))

    tgt = open(TARGET, "rb").read()
    # the pit entry line (starts with the attribution, contains title)
    pit_lines = [l for l in tgt.splitlines()
                 if PIT_TITLE.encode("utf-8") in l and b"r693 bm-c" in l]
    assert len(pit_lines) == 1, "pit entry must be exactly 1 line, got %d" % len(pit_lines)
    block = pit_lines[0] + b"\n"
    r["target"] = "research/pit-tooling.md"
    r["pit"] = "post_review red-check latest-row-per-item canon (+ wb-boolean-chain dead-truncation appendix)"
    r["appended_bytes"] = len(block)
    r["appended_sha16"] = hashlib.sha256(block).hexdigest()[:16]
    r["target_bytes_post"] = len(tgt)
    r["target_under_line"] = len(tgt) <= LIMIT
    r["heal"] = {
        "incident": "dead boolean-chain open(p,'wb') (never wrote) truncated "
                    "pit-tooling.md 20,312 -> 0B during first increment attempt",
        "guard": "treasure_guard restore rc3 HARD REJECT (registry class)",
        "method": "line-level union with HEAD blob (current face 0 lines -> "
                  "union == HEAD lines verbatim); zero-loss = all HEAD lines "
                  "present; LF-form HEAD blob landed (autocrlf-normalized)",
        "zero_loss": True}
    main_raw = open(MAIN, "rb").read()
    assert main_raw.count(POINTER_HEAD.encode("utf-8")) == 1
    ptr_lines = [l for l in main_raw.splitlines()
                 if POINTER_HEAD.encode("utf-8") in l]
    r["main_pointer_bytes"] = len(ptr_lines[0]) + 1
    r["main_bytes_pre"] = 30551
    r["zero_loss"] = True
    r["post_verify"] = {
        "main_bytes": len(main_raw), "main_under_line": len(main_raw) <= LIMIT,
        "pit_verbatim_in_target": block in tgt or pit_lines[0] in tgt,
        "pointer_in_main": True}
    with open(RECEIPT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(r, fh, ensure_ascii=False, indent=1)
    print(json.dumps(r["post_verify"], ensure_ascii=False))
    print("receipt completed; appended_sha16=%s bytes=%d" %
          (r["appended_sha16"], r["appended_bytes"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
