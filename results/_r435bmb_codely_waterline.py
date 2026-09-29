# -*- coding: utf-8 -*-
"""r435 bm-b waterline reorg: CODELY.md 10,421B > 10KB hard line ->
migrate five batch-lesson entries verbatim to research/memory-archive/202609.md,
leave one cold-layer pointer in the hot file. Line-level zero-loss verified.
Idempotent: refuses if pointer already present."""
import io, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOT = os.path.join(ROOT, "CODELY.md")
ARC = os.path.join(ROOT, "research", "memory-archive", "202609.md")

PREFIXES = [
    "- [2026-09-29 15:1x r434 bm-a] 坑律一百一十二批",
    "- [2026-09-29 15:4x r223 bm-c] 坑律一百一十三批",
    "- [2026-09-29 15:5x r435 bm-a] 坑律一一三批",
    "- [2026-09-29 16:2x r225 bm-c] 坑律一百一十四批",
    "- [2026-09-29 16:4x r437 bm-a] 坑律一百一十五批",
]
POINTER = ("- 冷层指针：坑律一百一十二批（r434 bm-a·append_ledger 返回值丢弃簿记盲区律）"
           "+一百一十三批（r223 bm-c·API 猝死遗产先落地律）"
           "+一一三批（r435 bm-a·云盘桌面备份同步风暴杀树律）"
           "+一百一十四批（r225 bm-c·PS 参数字串拆散坑）"
           "+一百一十五批（r437 bm-a·inner-join 静默截史律）"
           "全文 verbatim=archive 202609.md『坑律归档 2026-09-29 r435 bm-b 窗批』节"
           "（水位 10,421B 超 ≤10KB 硬线当窗即办·行级零丢失校验）。")
SECTION_HDR = ("## 坑律归档 2026-09-29 r435 bm-b 窗批（水位整编·行级零丢失迁移："
               "CODELY.md 10,421B 超 ≤10KB 硬线→坑律一百一十二/一百一十三/一一三/"
               "一百一十四/一百一十五批五条 verbatim 迁此·行级零丢失校验）")

hot = io.open(HOT, encoding="utf-8").read()
if POINTER in hot:
    print("IDEMPOTENT-GUARD: pointer already present, refuse re-run")
    sys.exit(2)
arc = io.open(ARC, encoding="utf-8").read()
hot_lines = hot.splitlines()
migrated = []
kept = []
for ln in hot_lines:
    if any(ln.startswith(p) for p in PREFIXES):
        migrated.append(ln)
    else:
        kept.append(ln)
assert len(migrated) == 5, f"expected 5 entries, found {len(migrated)}"
# zero-loss precondition: each entry currently in hot exactly once
for p in PREFIXES:
    assert sum(1 for ln in hot_lines if ln.startswith(p)) == 1, p

block = "\n\n" + SECTION_HDR + "\n\n迁自 CODELY.md 热层（verbatim 零删改·指针回置热层）：\n\n" \
    + "\n\n".join(migrated) + "\n"
with io.open(ARC, "a", encoding="utf-8", newline="") as fh:
    fh.write(block)

# pointer goes into the Reference section (after the last 冷层指针 line)
ref_anchor = "- 冷层指针：坑律一百零九批（r428 bm-b·显示面乱码上下文污染律）"
assert ref_anchor in hot, "reference anchor line missing"
new_hot_lines = []
inserted = False
for ln in kept:
    new_hot_lines.append(ln)
    if ln.startswith(ref_anchor.split("：")[0] + "：坑律一百零九批") and not inserted:
        new_hot_lines.append("")
        new_hot_lines.append(POINTER)
        inserted = True
assert inserted, "pointer insertion point not reached"
new_hot = "\n".join(new_hot_lines) + ("\n" if hot.endswith("\n") else "")
with io.open(HOT, "w", encoding="utf-8", newline="") as fh:
    fh.write(new_hot)

# ---- zero-loss verification ----
arc2 = io.open(ARC, encoding="utf-8").read()
hot2 = io.open(HOT, encoding="utf-8").read()
missing = [p for p, ln in zip(PREFIXES, migrated)
           if ln not in arc2]
assert not missing, f"zero-loss FAILED: {missing}"
for p in PREFIXES:
    assert not any(l2.startswith(p) for l2 in hot2.splitlines()), \
        f"hot still contains {p}"
assert POINTER in hot2 and SECTION_HDR in arc2
print(f"WATERLINE-REORG OK: hot {len(hot.encode('utf-8'))}B -> "
      f"{len(hot2.encode('utf-8'))}B (<={10_000}); archive +"
      f"{len(block.encode('utf-8'))}B; migrated=5 lines verbatim; "
      f"zero-loss verified")
