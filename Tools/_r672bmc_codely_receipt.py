# -*- coding: utf-8 -*-
"""r672 bm-c CODELY increment receipt builder (r670 canon copy, single-entry face).

Migrates: nothing further -- verifies the already-moved r672 pit line
(pipeline-snapshot hash false-delta, read-side sibling of r814) from
CODELY.md main -> research/pit-protocol-d19.md, with byte/sha16 accounting:
  (1) block bytes present verbatim in target;
  (2) block bytes ABSENT from main (moved not copied);
  (3) main file <= 30,720B; all research/pit-*.md <= 30,720B;
  (4) receipt = this json.
"""
import glob
import hashlib
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN = os.path.join(ROOT, "CODELY.md")
TARGET = os.path.join(ROOT, "research", "pit-protocol-d19.md")
RECEIPT = os.path.join(ROOT, "results", "_r672bmc_codely_increment.json")

BLOCK = "- [2026-10-07 11:4x r672 bm-c] **集团水位 hash 比对禁管道快照件（r537 算法钉/r583 facts-driven 族·r814 写面坑的读面姊妹）**：git show 输出经 Out-File 落临时件再 hash=PS 管道再编码改写字节流→与 raw blob SHA 恒不等=假 delta（本窗实弹：decisions 临时件 SHA-256 1AC5C497…≠raw 635C3024·s05 脚本 canonical 复核 delta=false·零污染零错账）。How to apply：水位比对一律跑 Tools\\_rNNNbmc_s05.py raw-blob bytes 直 hash（r537 算法钉+r583 facts-driven），管道快照 hash 禁入任何比对面（前置粗比对也不许）。"


def main():
    with open(MAIN, "rb") as fh:
        main_bytes = fh.read()
    with open(TARGET, "rb") as fh:
        tgt_bytes = fh.read()
    block_b = BLOCK.encode("utf-8")
    sha16 = hashlib.sha256(block_b).hexdigest()[:16]

    in_target = block_b in tgt_bytes
    in_main = block_b in main_bytes
    main_len = len(main_bytes)
    pit_files = sorted(glob.glob(os.path.join(ROOT, "research", "pit-*.md")))
    pit_sizes = {os.path.basename(p): os.path.getsize(p) for p in pit_files}
    all_pit_ok = all(v <= 30720 for v in pit_sizes.values())
    main_ok = main_len <= 30720

    facts = {
        "round": 672,
        "machine": "bm-c",
        "block_sha16": sha16,
        "block_bytes": len(block_b),
        "block_in_target_verbatim": bool(in_target),
        "block_absent_from_main": not in_main,
        "main_bytes": main_len,
        "main_le_30720": bool(main_ok),
        "target": "research/pit-protocol-d19.md",
        "target_bytes": len(tgt_bytes),
        "pit_file_count": len(pit_files),
        "pit_all_le_30720": bool(all_pit_ok),
        "pit_max": max(pit_sizes.items(), key=lambda kv: kv[1])[0] if pit_sizes else None,
        "pit_max_bytes": max(pit_sizes.values()) if pit_sizes else 0,
        "zero_loss_assert": bool(in_target and (not in_main) and main_ok and all_pit_ok),
    }
    assert facts["zero_loss_assert"], "zero-loss assertion failed: %s" % facts
    with open(RECEIPT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(facts, fh, ensure_ascii=False, indent=1)
    print("receipt:", RECEIPT)
    print("zero_loss_assert=True main=%dB margin=%dB pit_max=%s %dB" % (
        main_len, 30720 - main_len, facts["pit_max"], facts["pit_max_bytes"]))
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
