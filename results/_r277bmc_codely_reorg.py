# -*- coding: utf-8 -*-
"""_r277bmc_codely_reorg.py -- CODELY.md <=10KB hard-line hot-cold reorganization
(r444 pointer-merge paradigm, D-20260924-01 archive route, line-level zero-loss):
migrate five full-text pit entries (r466/r276/r462/r468/r469, consumed windows)
verbatim into research/memory-archive/202609.md new section, replace with ONE
cold pointer line in Project section, append the NEW r277 pit entry at file end
(新坑律仍先入本件). r270 (reform-canon division ruling) + r470 (W14 adjudication
law, freeze step next round needs it) stay hot per 坑律/细则律留热层.
Idempotent: re-run detects the section header and no-ops."""
import io
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

CODELY = "CODELY.md"
ARCHIVE = "research/memory-archive/202609.md"
SECTION_HEADER = ("## 热冷整编 2026-09-30 r277 bm-c 窗批（CODELY ≤10KB 硬线·r277 stash-pop "
                  "活写者坑 append 后超线·r466/r276/r462/r468/r469 五条全文本坑 verbatim 迁入·"
                  "行级零丢失·r270 改革分工+r470 W14 甄别判例留热层）")
POINTER = ("- 冷层指针（r277 合并·r444 范式）：r466 无头 rebase 收口双新面+r276 波次种子带与 SLOT "
           "族带同区交错坑+r462 stash-pop UU 变体坑+r468 PS5.1 epoch 采样坑+r469 PS stash drop "
           "裸写坑全文 verbatim=archive 202609.md『热冷整编 2026-09-30 r277 bm-c 窗批』节。")
NEW_PIT = ("- [2026-09-30 r277 bm-c] stash-pop 撞活跃运行件坑（r462 UU 变体第三形态·r469 同窗族）："
           "轮首脏=本机后台进程持续写入的 runtime 件（dispatcher_state·盘中道 ladder ~4min/写）时，"
           "stash→pull FF→pop 三段的 **pop 段撞「local changes would be overwritten」**（活写者已把"
           "工作树刷得比 stash 快照新·非 UU 非 rebase 态·stash 条目自保全）——正解=diff 两版（通常仅 ts 殂）"
           "后 **drop 陈 stash 保活树**（活树新=权威·drop 零副作用），禁 pop 强推禁 checkout 覆盖活写者；"
           "判别键=stash 版 ts < 工作树版 ts=后台写者在飞。How to apply：轮首遇 runtime 件脏先探 ts 新鲜度，"
           "写者在飞=该件不进 stash 流（定向 stash 其余件或分次 pull），已进撞 pop=drop 保活。")
TARGETS = ("- [2026-09-30 r466 bm-b]",
           "- [2026-09-30 r276 bm-c]",
           "- [2026-09-30 r462 bm-b]",
           "- [2026-09-30 r468 bm-b]",
           "- [2026-09-30 r469 bm-b]")

codely = io.open(CODELY, "r", encoding="utf-8", newline="").read()
archive = io.open(ARCHIVE, "r", encoding="utf-8", newline="").read()
if SECTION_HEADER in archive:
    print("reorg: section already in archive -> idempotent no-op")
    sys.exit(0)

lines = codely.split("\n")
moved, kept = [], []
for ln in lines:
    if ln.startswith(TARGETS):
        moved.append(ln)
    else:
        kept.append(ln)
assert len(moved) == 5, f"expected 5 target entries, found {len(moved)}: {[m[:40] for m in moved]}"

# 1) append archive section (verbatim entries, zero-loss)
if not archive.endswith("\n"):
    archive += "\n"
archive += SECTION_HEADER + "\n\n" + "\n".join(moved) + "\n"
for m in moved:
    assert m in archive, "zero-loss violation: entry missing from archive"
io.open(ARCHIVE, "w", encoding="utf-8", newline="").write(archive)

# 2) rewrite CODELY.md: insert pointer at first removal position, drop targets,
#    append new pit at file end
out = []
inserted = False
for ln in kept:
    if not inserted and ln.startswith("### Project"):
        out.append(ln)
        out.append(POINTER)
        inserted = True
    else:
        out.append(ln)
assert inserted, "Project header not found"
while out and out[-1] == "":
    out.pop()
out.append(NEW_PIT)
new_codely = "\n".join(out) + "\n"
for m in moved:
    assert m not in new_codely, "target still present in CODELY.md"
io.open(CODELY, "w", encoding="utf-8", newline="").write(new_codely)

# 3) verify: zero-loss (archive holds all moved lines verbatim) + size gate
archive2 = io.open(ARCHIVE, "r", encoding="utf-8", newline="").read()
for m in moved:
    assert archive2.count(m) >= 1, "post-write zero-loss violation"
size = len(new_codely.encode("utf-8"))
print(f"reorg: 5 entries migrated verbatim; pointer inserted; new pit appended")
print(f"CODELY.md size: {size} bytes ({'UNDER' if size <= 10240 else 'OVER'} 10KB line)")
assert size <= 10240, f"CODELY.md still over 10KB: {size}"
print("OK")
