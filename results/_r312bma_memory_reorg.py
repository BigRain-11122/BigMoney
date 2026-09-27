# -*- coding: utf-8 -*-
"""R312 bm-a heat/cold reorg: CODELY.md <=10KB hard line (O-20260927-0230).

Migrate ALL existing pitfall entries in CODELY.md Reference section (10 entries,
all from 2026-09-27 morning windows) verbatim to
research/memory-archive/202609.md under batch-8 section header; keep in CODELY.md:
- User meta-law (never archived)
- Reference pointer lines (updated with batch-8 index)
- NEW hot entry from this round (r312 bm-a in-window duplicate-shard-burn law)
Zero-loss check: every migrated line must appear verbatim (exact bytes) in the
archive file afterwards; CODELY.md size must be < 10240 bytes.
"""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODELY = os.path.join(ROOT, "CODELY.md")
ARCHIVE = os.path.join(ROOT, "research", "memory-archive", "202609.md")

with io.open(CODELY, "r", encoding="utf-8") as f:
    lines = f.read().splitlines()

pointer_prefixes = ("- 冷层指针：", "- 坑律正典全量归档")
migrate, keep = [], []
for ln in lines:
    s = ln.strip()
    if s.startswith("- [2026-09-27") and "坑律" in s:
        migrate.append(ln)
    else:
        keep.append(ln)

assert len(migrate) == 10, f"expected 10 pitfall entries, got {len(migrate)}"

NEW_ENTRY = (
    "- [2026-09-27 10:4x r312 bm-a] 坑律：**轮内烧分片前必 fetch 洞察对岸翻面（同窗多机重复烧片发生器）**"
    "——r312 实弹：10:19 读本地池 13 分片 owner=None 即烧（X2-deep 4 片+PROS 9 片），10:37 push 被拒 pull 后见 "
    "bm-b 已同窗独立烧完全部 14 片并翻 done（对岸在制窗盲区=本地池文件落后 origin 结构性必在）；"
    "双烧由 checkpoint keep-last 收敛零数据损，但 13 片纯重复 CPU+runnable_pool UU 需 union 解。"
    "正典=①轮内烧片前 `git fetch` + `git show origin/main:results/runnable_pool.json` 读对岸翻面（本地工作树=滞后面）"
    "②冲突分类器已补 runnable_pool=pool-entry-done-union 配方（done 吸收律·done 侧分片字段权威·selftest 19/19 绿）。"
    "指针=results/_r312bma_resolve.py+_r312bma_resolve_state.py+commit b1e48136。"
)

BATCH_HEADER = (
    "## 坑律归档 2026-09-27 · 归档八批（r312 bm-a 热冷整编·行级 verbatim 零丢失）\n"
    "（O-20260927-0230 ≤10KB 硬线：新坑律入件后超线当窗整编·外迁 10 条·检索按条目内『指针=』字段定位）"
)

with io.open(ARCHIVE, "a", encoding="utf-8", newline="") as f:
    f.write("\n\n" + BATCH_HEADER + "\n\n")
    for ln in migrate:
        f.write(ln.strip() + "\n")

# rewrite CODELY.md: update pointer line + append new hot entry at Reference tail
out = []
for ln in keep:
    if ln.strip().startswith("- 坑律正典全量归档"):
        ln = ln.rstrip() + (
            " 八批外迁索引（R312 bm-a）：r306 rebase-continue/r310 撞认领/r312 bm-b seed·regime·"
            "orders_ack 三条/r309 S6 子命令/r313 第三写手/r72·r73 bm-c 两条/r314 flip-first=归档八批节。"
        )
    out.append(ln)
out.append(NEW_ENTRY)

with io.open(CODELY, "w", encoding="utf-8", newline="") as f:
    f.write("\n".join(out) + "\n")

# zero-loss verification
with io.open(ARCHIVE, "r", encoding="utf-8") as f:
    arch_txt = f.read()
missing = [ln.strip()[:60] for ln in migrate if ln.strip() not in arch_txt]
assert not missing, f"zero-loss violated: {missing}"
size = os.path.getsize(CODELY)
print(f"migrated={len(migrate)} archive_OK zero_loss=PASS codely_size={size}B "
      f"{'UNDER-10KB' if size < 10240 else 'STILL-OVER-RED'}")
