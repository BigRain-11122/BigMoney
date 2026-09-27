# results/_r384bma_codely_hotcold.py -- r384 in-window hot/cold archival
# (water law: CODELY.md union 10,537B > 10KB hard line -> consolidate NOW).
# Migrate three settled pit-law entries (r356/r358/r359, all 2026-09-28 bm-b)
# verbatim to research/memory-archive/202609.md batch-28 section, replace
# with a single cold-pointer line, verify line-level zero loss + size.
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CP = os.path.join(ROOT, "CODELY.md")
AP = os.path.join(ROOT, "research", "memory-archive", "202609.md")

codely = open(CP, encoding="utf-8", newline="").read()
lines = codely.splitlines()

# locate the three entry lines by their verbatim head tokens
HEADS = ["- [2026-09-28 03:4x r356 bm-b]",
         "- [2026-09-28 05:0x r358 bm-b]",
         "- [2026-09-28 04:4x r359 bm-b]"]
idx = {}
for i, l in enumerate(lines):
    for h in HEADS:
        if l.startswith(h):
            idx[h] = i
assert len(idx) == 3, f"entry locate failed: {sorted(idx)}"
migrated = [lines[idx[h]] for h in HEADS]
assert all(len(m) > 200 for m in migrated), "suspiciously short entry"

POINTER = ("冷层指针：坑律正典 2026-09-28 二十八批（r384 bm-a 窗·水位律当窗整编："
           "CODELY union 10,537B 超 ≤10KB 硬线）：r356 PS 无 env 前缀语法 / "
           "r358 win-git rebase-continue 拒发 r355-addendum 直连收口 / "
           "r359 pandas to_numpy 只读视图 三条全文 verbatim=archive 202609.md"
           "『坑律归档 2026-09-28 二十八批』节（行级零丢失校验）。")

# splice: entries sit on consecutive lines L15-L17 (r356/r358/r359)
first = min(idx.values())
last = max(idx.values())
assert last - first == 2, f"entries not consecutive: {first}..{last}"
new_lines = lines[:first] + [POINTER] + lines[last + 1:]
new_codely = "\n".join(new_lines) + "\n"

ARCHIVE_SECTION = ("\n## 坑律归档 2026-09-28 二十八批（r384 bm-a 窗·当窗整编）\n\n"
                   "自 repo 根 CODELY.md Reference 节迁入，行级零丢失：\n\n"
                   + "\n".join(migrated) + "\n")
with open(AP, "a", encoding="utf-8", newline="") as fh:
    fh.write(ARCHIVE_SECTION)

# line-level zero-loss verification: every migrated line byte-present in archive
arch = open(AP, encoding="utf-8", newline="").read()
for m in migrated:
    assert m in arch, f"zero-loss FAIL: {m[:60]}"
assert len(new_codely.encode("utf-8")) <= 10240, "still over hard line"
open(CP, "w", encoding="utf-8", newline="").write(new_codely)

chk = open(CP, encoding="utf-8", newline="").read()
print("migrated:", len(migrated), "entries")
print("pointer line in place:", POINTER[:40] in chk)
print("CODELY.md bytes:", len(chk.encode("utf-8")), "(<= 10240)")
print("archive bytes now:", os.path.getsize(AP))
