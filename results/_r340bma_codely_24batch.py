"""r340 bm-a 24th-batch in-window CODELY archival (watermark law: append crossed <=10KB hard line).

Faces:
1. Append 24th-batch section to research/memory-archive/202609.md:
   - new pit entry full text (5x periodic duty silently skipped in collision-storm rapid rounds)
   - CODELY.md line-16 historical batch-index segments (15th x2 + r85 note + 16th) verbatim byte migration
2. CODELY.md: line 16 compacted to law-core + folded pointer; new pit entry stays as pointer row.
3. Line-level zero-loss verification: every migrated byte segment must appear in archive verbatim;
   CODELY size must be <=10240B with CRLF integrity.
"""
import io

CODELY = "CODELY.md"
ARCH = "research/memory-archive/202609.md"

b = open(CODELY, "rb").read()
lines = b.split(b"\r\n")
L16 = lines[16]
assert L16.startswith(b"- " + "\u5751\u5f8b\u6b63\u5178\u5168\u91cf\u5f52\u6863".encode("utf-8")), "line16 drift"
old_len = len(b)

# --- exact byte segments to migrate out of line 16 (verbatim, from the live file) ---
seg_marks = [
    "\u5341\u4e94\u6279\u5916\u8fc1\uff08r327 bm-a".encode("utf-8"),
    "\u5341\u4e94\u6279\u5916\u8fc1\uff08r84 bm-c".encode("utf-8"),
    "\uff08r85 \u52d8\u6ce8\uff1a".encode("utf-8"),
    "\u5341\u516d\u6279\u5916\u8fc1\uff08r328 bm-a".encode("utf-8"),
]
pos = [L16.find(m) for m in seg_marks]
assert all(p > 0 for p in pos), "segment marker missing: %r" % pos
mig_start = L16.find("\u3002\u5341\u4e94\u6279\u5916\u8fc1".encode("utf-8")) + len("\u3002".encode("utf-8"))
law_core = L16[:mig_start]  # up to and including the law sentence period
migrated = L16[mig_start:]  # the four historical batch-index segments, byte-verbatim
assert mig_start > 0 and len(migrated) > 400, "split failed"

new_full = (
    "- [2026-09-27 17:5x r340 bm-a] \u5751\u5f8b\uff1a**round_no \u5468\u671f\u4e49\u52a1\u5728\u649e\u8f66\u98ce\u66b4\u5feb\u8f6e\u7a97\u4f1a\u9759\u9ed8\u6f0f\u505a**"
    "\u2014\u2014R335\uff085 \u500d\u6570\u8f6e\u00b72026-09-27 16:2x\uff09\u6574\u8f6e\u88ab S0 UU canon-resolve \u8fde\u9501\uff0816/27/28-UU \u4e09\u6279\u649e\u8f66\u89e3\uff09+S6 \u7ef4\u62a4\u6324\u5360\uff0c"
    "5x HANDOVER \u5bf9\u8d26\u672a\u505a\u4e14\u8f6e\u62a5\u544a\u65e0\u6807\u6ce8\uff0c\u6b20\u8d26\u9759\u9ed8\u5b58\u7eed\u5230 R340 \u624d\u7531\u8865\u6838\u8986\u76d6\uff08\u5bf9\u8d26\u533a\u95f4=R331-340 \u5168\u7a97\uff1b"
    "\u8de8\u673a\u5197\u4f59\u515c\u5e95=bm-b r335 \u6298\u53e0\u94fe\u4e0a 5x \u884c\u5df2\u4ee3\u8bb0 286,541\u2192286,551 \u589e\u91cf\uff0c\u672c\u7a97\u552f\u4e00\u79d1\u5b66\u6279 SINA-CONSTRUCT-P1 finalize \u96f6\u4e22\u5931\uff09\u3002"
    "Why\uff1a10min \u5feb\u8f6e\u5728\u98ce\u66b4\u7a97\u5bc6\u5ea6\u9ad8\uff08R331-339 \u4e5d\u8f6e\u8de8 2h\uff09\uff0c\u5468\u671f\u68c0\u67e5\u70b9\uff08%5==0\uff09\u843d\u5728\u5176\u4e2d\u4efb\u4e00\u8f6e\u7684\u6982\u7387\u88ab\u649e\u8f66\u89e3\u4f18\u5148\u7ea7\u7a00\u91ca\uff0c"
    "S3 \u77ed\u95ed\u73af\u805a\u7126\u5f53\u8f6e\u7ea2\u9762\u4e0d\u4f1a\u81ea\u52a8\u611f\u77e5\u5468\u671f\u4e49\u52a1\u5230\u671f\u3002"
    "How to apply\uff1a\u51e1\u672c\u673a round_no%5==0 \u7684\u8f6e\uff0c5x HANDOVER \u5bf9\u8d26\u4e0e\u649e\u8f66\u89e3\u5e73\u7ea7\u5fc5\u505a\u4e0d\u53ef\u8ba9\u8def\uff08\u7269\u7406\u4f9d\u8d56\u9664\u5916=\u7968\u5185\u7559\u75d5\uff09\uff1b"
    "\u5df2\u6f0f\u505a=\u6b21\u8f6e\u9996\u5fc5\u8865\u6838\uff08\u5bf9\u8d26\u533a\u95f4\u8986\u76d6\u6b20\u8d26\u7a97\u5168\u8de8\u5ea6\uff09\u5e76\u5728\u8f6e\u62a5\u544a+HANDOVER \u884c\u6ce8\u660e\u6b20\u8d26\u4e0e\u8865\u6838\u7a97\u3002"
)

new_pointer = (
    "- [2026-09-27 17:5x r340 bm-a] \u5751\u5f8b\uff08\u4e8c\u5341\u56db\u6279\u5916\u8fc1\u00b7\u6307\u9488\uff09\uff1around_no \u5468\u671f\u4e49\u52a1\uff085x HANDOVER \u5bf9\u8d26\u7b49\uff09\u5728\u649e\u8f66\u98ce\u66b4\u5feb\u8f6e\u7a97\u4f1a\u9759\u9ed8\u6f0f\u505a"
    "\uff08R335 \u5b9e\u8bc1\u00b7R340 \u8865\u6838\u8986\u76d6 R331-340 \u5168\u7a97\uff09\uff1b\u6b63\u5178=%5==0 \u8f6e 5x \u4e0e\u649e\u8f66\u89e3\u5e73\u7ea7\u5fc5\u505a\u3001\u5df2\u6f0f=\u6b21\u8f6e\u9996\u8865\u6838\u6ce8\u660e\u6b20\u8d26"
    "\u2014\u2014\u5168\u6587 verbatim=research/memory-archive/202609.md\u300e\u5751\u5f8b\u5f52\u6863 2026-09-27 \u4e8c\u5341\u56db\u6279\u300f\u8282\u3002"
)

arch_section = (
    "\r\n## \u5751\u5f8b\u5f52\u6863 2026-09-27 \u4e8c\u5341\u56db\u6279\uff08r340 bm-a\u00b7\u6c34\u4f4d\u5f8b\u5f53\u7a97\u6574\u7f16\uff1ar340 \u65b0\u5751\u5f8b append \u540e\u8d85 \u226410KB \u786c\u7ebf\u00b7\u65b0\u5751\u5f8b\u5168\u6587+CODELY \u884c16 \u5341\u4e94/\u5341\u516d\u6279\u7d22\u5f15\u53f2\u6bb5\u884c\u7ea7\u96f6\u4e22\u5931\u5916\u8fc1\uff09\r\n"
    + new_full + "\r\n"
    + "\uff08\u81ea CODELY.md \u884c16 \u6298\u53e0\u5916\u8fc1\u7684\u5386\u53f2\u6279\u7d22\u5f15\u6bb5\u00b7byte-verbatim\uff09\uff1a\r\n"
    + migrated.decode("utf-8") + "\r\n"
)

ab_pre = open(ARCH, "rb").read()
already = "\u4e8c\u5341\u56db\u6279\uff08r340 bm-a".encode("utf-8") in ab_pre
if not already:
    with io.open(ARCH, "ab") as f:
        f.write(arch_section.encode("utf-8"))
print("archive append skipped (already present)" if already else "archive section appended")

compact16 = law_core + (
    "\uff1b\u5341\u4e94\u6279\u53cc\u673a\u6bb5\uff08r327 bma \u7d22\u5f15\u6298\u53e0/r84 bmc \u6761\u76ee\u5916\u8fc1+r85 \u52d8\u6ce8\uff09+\u5341\u516d\u6279\u6bb5\uff08r328 bma\uff09"
    "\u5df2\u518d\u6298\u53e0\u5f52\u6863=archive 202609.md \u4e8c\u5341\u56db\u6279\u8282\uff08\u884c\u7ea7\u96f6\u4e22\u5931\u00b7\u68c0\u7d22\u5148\u67e5\u5404\u6279\u8282\uff09\u3002"
).encode("utf-8")
assert L16.endswith(migrated), "line16 tail mismatch"
lines[16] = compact16
# remove one of the triple blank lines in the Project section (cosmetic slim, zero info loss)
if lines[5] == b"" and lines[6] == b"" and lines[7] == b"":
    del lines[6]
# append new pointer row at end (before final empty)
if lines and lines[-1] == b"":
    lines.insert(len(lines) - 1, new_pointer.encode("utf-8"))
else:
    lines.append(new_pointer.encode("utf-8"))
nb = b"\r\n".join(lines)
with io.open(CODELY, "wb") as f:
    f.write(nb)

# --- verification ---
cb = open(CODELY, "rb").read()
ab = open(ARCH, "rb").read()
assert len(cb) <= 10240, "CODELY still over hard line: %d" % len(cb)
assert cb.count(b"\r\n") == cb.count(b"\n"), "bare LF introduced"
assert migrated in ab, "migrated segment NOT verbatim in archive"
assert new_full.encode("utf-8") in ab, "new full NOT verbatim in archive"
assert new_pointer.encode("utf-8") in cb, "pointer row missing in CODELY"
assert law_core in cb, "law core lost"
assert "\u5341\u4e94\u6279\u5916\u8fc1\uff08r327 bm-a".encode("utf-8") not in cb, "old segment still in CODELY"
print("CODELY: %d -> %d bytes (hard line 10240 OK)" % (old_len, len(cb)))
print("line16: %d -> %d bytes" % (len(L16), len(compact16)))
print("archive: +%d bytes, migrated-segment verbatim OK, new-full verbatim OK" % len(arch_section.encode("utf-8")))
print("CRLF integrity OK; pointer row in place; law core intact")
