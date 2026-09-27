# -*- coding: utf-8 -*-
"""r327 bm-a CODELY.md 15th-batch hot-cold archival (water-line triggered:
append pushed 10338B > 10240B hard line -> same-window archival per
O-20260927-0230 / D-20260924-01 pattern, line-level zero loss).

Moves: batch-index block 四批~十四批 (flow-type records) from the Reference
section to research/memory-archive/202609.md 十五批 section, verbatim.
Keeps: 冷层指针 + 坑律正典归档 head + one new 十五批 index line + all
pitlaw entries (hot law: 新坑律仍先入本件).
"""
import io
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

P = "CODELY.md"
A = "research/memory-archive/202609.md"

b = io.open(P, "rb").read()
start_marker = "四批外迁索引（R303）".encode("utf-8")
end_marker = "=归档十四批节·行级零丢失。".encode("utf-8")
i = b.find(start_marker)
assert i >= 0, "start marker not found"
j = b.find(end_marker, i)
assert j >= 0, "end marker not found"
j += len(end_marker)
moved = b[i:j]
assert len(moved) > 300, "moved chunk suspiciously small"

replacement = ("十五批外迁（r327 bm-a·超线当窗整编）：四批~十四批外迁索引面 11 段"
               "（R303/R310/r312/r313/r316/R312/r317/r78/r319/r322/r82/r325/r327bmb）"
               "=归档十五批节·行级零丢失。").encode("utf-8")
newb = b[:i] + replacement + b[j:]
newb.decode("utf-8")  # strict gate
assert len(newb) <= 10240, "still over hard line: %d" % len(newb)

# archive append: byte-faithful, detect archive ending convention
ab = io.open(A, "rb").read()
crlf = b"\r\n" in ab
nls = "\r\n" if crlf else "\n"
section = (nls + "## 十五批外迁（2026-09-27 r327 bm-a·CODELY 超线当窗整编·行级零丢失）" + nls + nls).encode("utf-8")
nl = nls.encode("utf-8")
moved_lf = moved  # moved text is LF (CODELY is LF); archive LF too (crlf False expected)
if crlf:
    moved_lf = moved.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
new_ab = ab + section + moved_lf + nl
new_ab.decode("utf-8")  # strict gate
# anchor verification: first + last batch lines present verbatim in archive
assert "四批外迁索引（R303）".encode("utf-8") in new_ab
assert "=归档十四批节·行级零丢失。".encode("utf-8") in new_ab

io.open(P, "wb").write(newb)
io.open(A, "wb").write(new_ab)

# post-write re-verify from disk
chk = io.open(P, "rb").read()
chk.decode("utf-8")
assert len(chk) == len(newb)
chk2 = io.open(A, "rb").read()
assert len(chk2) == len(new_ab)
print("CODELY.md: %dB -> %dB (limit 10240B) moved=%dB replacement=%dB" % (len(b), len(newb), len(moved), len(replacement)))
print("archive %s: %dB -> %dB (CRLF=%s)" % (A, len(ab), len(new_ab), crlf))
print("byte math CODELY: %d - %d + %d = %d OK" % (len(b), len(moved), len(replacement), len(newb)))
assert len(b) - len(moved) + len(replacement) == len(newb)
print("15TH-BATCH ARCHIVAL OK")
