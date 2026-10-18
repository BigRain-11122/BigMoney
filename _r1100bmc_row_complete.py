# -*- coding: utf-8 -*-
# r1100 bm-c: round-report row face completion (multi-writer file: fresh-read-modify-write, r1006 law).
# Adds the window-required faces the r1100 row missed: orphan=2 zero-kill + product-three lines.
import io

PATH = "round_reports-bm-c.md"
raw = io.open(PATH, encoding="utf-8", newline="").read()
eol = "\r\n" if raw.count("\r\n") >= raw.count("\n") - raw.count("\r\n") else "\n"
lines = raw.split(eol)

# locate MY r1100 row (unique anchor)
ANCHOR = "| r1100 | W272 FIVE-FACE CHAIN COMPLETE one-window"
idx = [i for i, ln in enumerate(lines) if ANCHOR in ln]
assert len(idx) == 1, "r1100 row anchor not unique: %d" % len(idx)
row = lines[idx[0]]
assert "孤儿面" not in row, "row already carries orphan face (idempotent guard)"

# insert faces: orphan line into the standing column (before watermark cell),
# product-three lines at the row end (before the final pipe).
OLD_TAIL = "| watermark=green | 本地未达 origin commit 数=0 |"
NEW_TAIL = ("| 孤儿面=2 零杀（probe 20:03:31 py_faces=5 只读不杀）| 当前活=W273 席位（r1101 FIRST ACTION）/"
            "最近实物=n1_w272_results.json（ledger 1,022,735/K=596,320）/下个里程碑=W273 seat ≤48h + "
            "周一 10-20 15:30 papers | watermark=green | 本地未达 origin commit 数=0 |")
assert row.count(OLD_TAIL) == 1, "row tail anchor not found exactly once"
lines[idx[0]] = row.replace(OLD_TAIL, NEW_TAIL)
t2 = eol.join(lines)
assert t2.count(ANCHOR) == 1 and "孤儿面=2 零杀" in t2
io.open(PATH, "w", encoding="utf-8", newline="").write(t2)
print("row face-completion OK: orphan=2 zero-kill + product-three lines appended to r1100 row; eol=%r" % eol)
