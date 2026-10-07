# -*- coding: utf-8 -*-
"""r693 bm-c increment fix-up leg: main CODELY.md is 15B over the 30,720B
line after the r693 pointer append. Per r667 precedent, migrate ONE
existing pointer line (bm-a r833, smallest tail line, declared domain =
pit-engine-freeze-editor.md) verbatim into that domain file's tail
(arrow stays true), freeing ~250B in main. Then write the FULL receipt
(heal + pit append + pointer + migration accounting). Idempotent-guarded."""
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN = os.path.join(ROOT, "CODELY.md")
DEST = os.path.join(ROOT, "research", "pit-engine-freeze-editor.md")
RECEIPT = os.path.join(ROOT, "results", "_r693bmc_codely_increment.json")
LIMIT = 30720
NEEDLE = "r833 bm-a".encode("utf-8")


def eol_of(raw):
    return b"\r\n" if raw.count(b"\r\n") >= 10 else b"\n"


def main():
    raw = open(MAIN, "rb").read()
    receipt_path = os.path.join(ROOT, "results", "_r693bmc_codely_increment.json")
    receipt = {"round": 693, "machine": "bm-c",
               "action": "direct-write increment (r429/r666/r673 pattern) "
                         "+ truncation heal (line-level union per guard rc3) "
                         "+ r667-precedent pointer migration"}
    if os.path.exists(receipt_path):
        receipt = json.load(open(receipt_path, encoding="utf-8"))
        if receipt.get("migration_done"):
            print("already done")
            return 0

    lines = raw.splitlines(keepends=True)
    hits = [i for i, l in enumerate(lines) if NEEDLE in l]
    assert len(hits) == 1, "r833 needle must hit exactly 1 line, got %d" % len(hits)
    idx = hits[0]
    moved = lines[idx]
    assert moved.startswith(b"- "), "r833 line bullet form gate"
    new_main = b"".join(lines[:idx] + lines[idx + 1:])
    assert open(MAIN, "rb").read().count(NEEDLE) == 1, "pre-verify"
    with open(MAIN, "wb") as fh:
        fh.write(new_main)
    post_m = open(MAIN, "rb").read()
    assert post_m.count(NEEDLE) == 0, "post-verify removed from main"
    assert len(post_m) <= LIMIT, "MAIN STILL OVER LINE: %d" % len(post_m)

    raw_d = open(DEST, "rb").read()
    eol_d = eol_of(raw_d)
    assert raw_d.count(NEEDLE) == 0, "rerun guard: r833 already in dest"
    block = moved if moved.endswith(b"\n") or moved.endswith(b"\r\n") else moved + eol_d
    with open(DEST, "ab") as fh:
        fh.write(block)
    post_d = open(DEST, "rb").read()
    assert post_d.count(NEEDLE) == 1, "post-verify r833 in dest count==1"
    moved_core = moved.rstrip(b"\r\n")
    assert moved_core in post_d, "zero-loss: migrated line verbatim in dest"

    receipt["migration_r833"] = {
        "line_bytes": len(moved_core), "sha16": hashlib.sha256(moved_core).hexdigest()[:16],
        "from": "CODELY.md", "to": "research/pit-engine-freeze-editor.md",
        "main_bytes_after_remove": len(post_m), "dest_bytes_post": len(post_d),
        "dest_under_line": len(post_d) <= LIMIT, "verbatim_in_dest": True}
    receipt["main_bytes_post"] = len(post_m)
    receipt["main_under_line"] = len(post_m) <= LIMIT
    receipt["migration_done"] = True
    with open(RECEIPT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(receipt, fh, ensure_ascii=False, indent=1)
    print("r833 pointer migrated %dB; main %dB (under line), dest %dB"
          % (len(moved_core), len(post_m), len(post_d)))
    print(json.dumps(receipt.get("migration_r833"), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
