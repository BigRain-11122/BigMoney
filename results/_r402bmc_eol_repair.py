# -*- coding: utf-8 -*-
"""r402 bm-c EOL repair: remove the two orphaned \\r bytes introduced by
_r402bmc_surgery.py (line_bounds terminator double-count -> insert/remove
span +1 overflow). Lone CR suppresses git's autocrlf clean filter ->
full-file staged diff; after this repair both files carry zero lone CR
and `git add` normalizes to the LF blob convention (surgical diff).

Assert-all-before-write; byte-level; verifiable by re-running (idempotent
guards)."""
import sys

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"


def lone_crs(data):
    return [i for i in range(len(data))
            if data[i:i + 1] == b"\r" and data[i + 1:i + 2] != b"\n"]


def repair(path, next_line_head):
    with open(path, "rb") as fh:
        data = fh.read()
    crs = lone_crs(data)
    if not crs:
        print(f"{path}: no lone CR (already repaired) -- skip")
        return
    if len(crs) != 1:
        print(f"ABORT {path}: unexpected lone-CR count {len(crs)}")
        sys.exit(1)
    pos = crs[0]
    # assert the orphan is exactly: \r\n + \r + next_line_head
    ctx = data[pos:pos + len(next_line_head) + 1]
    if not (data[pos:pos + 1] == b"\r"
            and data[pos + 1:pos + 1 + len(next_line_head)]
            == next_line_head
            and data[pos - 2:pos] == b"\r\n"):
        print(f"ABORT {path}: orphan CR context mismatch at {pos}: "
              f"{data[max(0, pos-10):pos+len(next_line_head)+10]!r}")
        sys.exit(1)
    fixed = data[:pos] + data[pos + 1:]
    assert lone_crs(fixed) == [], "post-fix lone CR remains"
    assert len(fixed) == len(data) - 1
    tmp = path + ".tmp_r402fix"
    with open(tmp, "wb") as fh:
        fh.write(fixed)
    import os
    os.replace(tmp, path)
    print(f"{path}: orphan CR at {pos} removed "
          f"({len(data)}B -> {len(fixed)}B); next-line head verified")


repair(ROOT + r"\CODELY.md",
        "- [2026-10-03 07:25 r402 bm-c]".encode("utf-8"))
repair(ROOT + r"\research\pit-pool.md",
        "> \u589e\u91cf\u56de\u626b\u884c\uff08r402 bm-c".encode("utf-8"))
print("REPAIR OK")
