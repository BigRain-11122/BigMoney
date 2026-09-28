# r403 bm-b hot-cold reconsolidation (<=10KB hard line, D-20260924-01 paradigm)
# Moves 4 closed-window pit-law batches verbatim from repo CODELY.md hot layer
# to research/memory-archive/202609.md; replaces with one cold pointer; appends
# new batch 74 (dead-session product attribution = CPU-delta probe law).
# Zero-loss guard: every moved non-blank line must appear verbatim in the
# archive after write; all 4 batch markers must be inside the cut region.
import io, sys

C = "CODELY.md"
A = "research/memory-archive/202609.md"

codely = io.open(C, encoding="utf-8", newline="").read()
assert "\r\n" not in codely, "CODELY.md uses CRLF? abort for manual look"

marker = "- [2026-09-29 01:4x] r402 bm-b \u5751\u5f8b\u4e03\u5341\u4e8c\u6279"
idx = codely.find(marker)
assert idx > 0, "batch-72 marker not found"
cut = codely[idx:]
moved = [ln for ln in cut.split("\n") if ln.strip()]
assert len(moved) == 4, f"expected 4 moved lines, got {len(moved)}"
for m in ["\u4e03\u5341\u4e8c\u6279", "\u4e03\u5341\u4e00\u6279\u8865",
          "\u5751\u5f8b\u4e03\u5341\u4e00\u6279\uff08\u6b7b\u7a97\u53cc\u6740",
          "\u5751\u5f8b\u4e03\u5341\u4e09\u6279"]:
    assert any(m in ln for ln in moved), f"marker missing in cut region: {m}"
assert not any("\u51b7\u5c42\u6307\u9488" in ln for ln in moved), "pointer leaked into cut region"

header = (
    "## \u5751\u5f8b\u5f52\u6863 2026-09-29 r403 bm-b \u7a97\u6279\n"
    "\uff08r403 bm-b \u7a97\u6c34\u4f4d\u5f8b\u5f53\u7a97\u6574\u7f16\uff1aCODELY.md hot \u5c42 9,987B+\u4e03\u5341\u56db\u6279"
    "\u5165\u518c\u5373\u8d85 \u226410KB \u786c\u7ebf\uff1b\u672c\u7a97\u6574\u7f16\u56db\u6761\u5df2\u95ed\u7a97\u6279"
    "\uff08r402 \u4e03\u5341\u4e8c\u6279/r406 \u4e03\u5341\u4e00\u6279+\u8865/r407 \u4e03\u5341\u4e09\u6279\uff09"
    "verbatim \u5916\u8fc1\u672c\u8282\uff0c\u884c\u7ea7\u96f6\u4e22\u5931\u6821\u9a8c\u3002\uff09\n"
)

new_batch = (
    "- [2026-09-29 02:2x] r403 bm-b \u5751\u5f8b\u4e03\u5341\u56db\u6279\uff08\u6b7b\u4f1a\u8bdd\u4ea7\u7269\u5f52\u56e0"
    "=CPU-delta \u63a2\u9488\u5f8b\u00b7\u6302\u6b7b\u7ba1\u9053\u96f6\u8fdb\u5c55\u50f5\u5c38\uff09\uff1ar401 \u6b8b\u7559"
    "\u94fe runner\uff08_r401bmb_s6_chain.py pid19188 \u81ea 00:56:22\uff0976 \u5206\u949f"
    " TotalProcessorTime=78ms\u300112s \u590d\u91c7 delta=0=stdout \u6302\u6b7b\u7ba1\u9053\uff08\u7236\u4f1a\u8bdd"
    "\u4ea1=\u7ba1\u9053\u65e0\u8bfb\u8005\uff09\u9759\u9ed8\u6302\u6b7b\u96f6\u817f\u96f6\u4ea7\u7269\uff0c\u800c\u5de5\u4f5c"
    "\u6811 01:59-02:00 S6 \u9762\u5199\u5165\u5148\u88ab\u8bef\u5f52\u56e0\u4e8e\u5b83\uff1b\u4e00\u6d4b\u5373\u5206\uff1a"
    "\u96f6 delta=\u6302\u6b7b\u50f5\u5c38\u4ea7\u7269\u5f52 01:42 25min-\u9884\u7b97\u51fb\u6740\u6b7b\u4f1a\u8bdd"
    "\uff08run_*.out \u5c3e=\u52a8\u4f5c\u8f68\u8ff9\u6743\u5a01\u53d6\u8bc1\u9762\uff0c\u672c\u6b21\u51ed\u5b83\u91cd"
    "\u5efa\u8ba9\u8def+\u4e8c\u673a\u9a8c\u8bc1+Batch A \u5168\u7a0b\uff1bstate \u505c\u65e7\u8f6e+\u65e0\u8f6e\u62a5"
    "+\u65e0 commit=\u9884\u7b97\u6740\u624b\u4e09\u7279\u5f81\uff09\u3002How to apply\uff1a\u6b7b\u4f1a\u8bdd"
    "\u810f\u6c34\u6536\u53e3\u65f6\u5bf9\u5b58\u6d3b\u540e\u53f0\u8fdb\u7a0b\u4e00\u5f8b\u5148 CPU-delta \u53cc\u91c7"
    "\u6837\u518d\u5f52\u56e0\u4efb\u4f55\u78c1\u76d8\u5199\u5165\uff1b\u94fe runner \u53d1\u5c04\u5fc5\u987b\u771f\u5206"
    "\u79bb\u8fdb\u7a0b\u6811\u5e26\u81ea\u8eab\u65e5\u5fd7\u6587\u4ef6\uff08\u6b7b\u7ba1\u9053=\u96f6\u8fdb\u5c55\u6302"
    "\u6b7b\u6bd4\u540c\u6b7b\u66f4\u9690\u853d\uff09\uff0c\u63a2\u6d4b\u540e\u6b8b\u7559\u96f6\u8fdb\u5c55\u50f5\u5c38"
    "=\u6740\u4e4b\u65e0\u635f\u3002"
)

pointer = (
    "\u51b7\u5c42\u6307\u9488\uff1a\u5751\u5f8b\u6b63\u5178 2026-09-29 r403 bm-b \u7a97\u6574\u7f16\u6279\uff08"
    "r402 bm-b \u4e03\u5341\u4e8c\u6279\uff08rebase \u89e3\u9762\u4fa7\u522b\u5047\u8bbe\u5751\u00b7fetch \u57fa\u52a8"
    "\u6001\u63a8\u8fdb\uff09/r406 bm-a \u4e03\u5341\u4e00\u6279\uff08\u6b7b\u7a97\u53cc\u6740\u00b7claims \u9762 origin"
    " \u76f2\u533a+\u94fe\u5b50\u8fdb\u7a0b\u968f\u7236\u6b7b\uff09+r406 bm-a \u4e03\u5341\u4e00\u6279\u8865\uff08rebase"
    " --continue 绕爪钳实弹\uff09/r407 bm-a \u4e03\u5341\u4e09\u6279\uff08\u9884\u6ce8\u518c"
    "\u951a\u4ea4\u53c9\u8868\u5fc5\u987b\u63a2\u9488\u57fa\u9010\u5b57\u590d\u7b97\uff09\u5168\u6587 verbatim=archive"
    " 202609.md\u300e\u5751\u5f8b\u5f52\u6863 2026-09-29 r403 bm-b \u7a97\u6279\u300f\u8282\uff08\u884c\u7ea7\u96f6"
    "\u4e22\u5931\u6821\u9a8c\uff09\u3002"
)

new_codely = codely[:idx].rstrip() + "\n\n" + pointer + "\n\n" + new_batch + "\n"

arch = io.open(A, encoding="utf-8", newline="").read()
assert "\r\n" not in arch, "archive uses CRLF? abort for manual look"
if not arch.endswith("\n"):
    arch += "\n"
arch_new = arch + "\n" + header + "\n".join(moved) + "\n"

# zero-loss verification BEFORE write: every moved line must be in arch_new tail
tail_sec = arch_new[len(arch):]
for ln in moved:
    assert ln in tail_sec, "zero-loss FAIL: moved line not in archive tail section"

io.open(C, "w", encoding="utf-8", newline="\n").write(new_codely)
io.open(A, "w", encoding="utf-8", newline="\n").write(arch_new)

# post-write re-read verification (row-level zero loss, disk truth)
c2 = io.open(C, encoding="utf-8", newline="").read()
a2 = io.open(A, encoding="utf-8", newline="").read()
ok = all(ln in a2 for ln in moved) and all(ln not in c2 for ln in moved)
print("moved_lines:", len(moved))
print("zero-loss verify:", "PASS" if ok else "FAIL")
print("CODELY.md bytes:", len(c2.encode("utf-8")), "(was 9987)")
print("archive bytes:", len(a2.encode("utf-8")), "(was 101582)")
assert ok and len(c2.encode("utf-8")) <= 10240, "reconsolidation gate FAIL"
print("RECONSOLIDATION GATE PASS")
