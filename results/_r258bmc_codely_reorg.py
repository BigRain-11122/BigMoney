# r258 bm-c CODELY hot-cold reorg (D-20260924-01 pattern, r255 precedent):
# migrate 2 verbatim entries -> research/memory-archive/202609.md, leave 1-line pointers,
# zero-loss assertions, target < 10240B.
import os

CODELY = "CODELY.md"
ARCHIVE = "research/memory-archive/202609.md"

ENTRY_R449 = (
    "[2026-09-30 r449 bm-b] 冻结面 replay 漂移三源定谳律+W8 构造事实（W8 feas 探针实弹·死会话遗产收编轮）："
    "重放历史冻结批成员面 vs 冻结产物不一致时，定谳序=①代码史（git log 冻结 commit 后）②数据史"
    "（core48 cutoff 前行=纯追加否）③注册件史（firm/traders/*.json）；本例零代码+零数据漂移、"
    "漂移=T-78 s4 注册进化（d65f2d4ac 三员退出覆盖层接线）合法——**对照员字节恒等测试**（未改注册"
    "件员 replay==frozen 2/2 全中）=机制身份隔离定谳法，禁据单员漂移误判机制漂移。W8 构造冻结事实："
    "28 员 252d 滚动 16/66 窗样本协方差奇异（A 臂生产配方不可算=病逆防御靶现象实弹）、λ∈[0.039,0.898] "
    "中位 0.131、cond 303k→36、A 臂全 pg_fallback vs B 臂 14 窗翻回闭式；退化窗政策=配对差分剔除+计数"
    "披露禁 pinv（A=生产配方 verbatim 禁改）。指针=research/INNOVATION_QUOTA_W8_PREREG_DRAFT.md §C1 + "
    "results/_r449bmb_w8_probe.json。"
)
POINTER_R449 = (
    "- 冷层指针：r449 bm-b 冻结面 replay 漂移三源定谳律+W8 构造事实（对照员字节恒等=机制身份隔离定谳法·"
    "λ 中位 0.131·16/66 奇异窗·退化窗配对差分剔除禁 pinv）全文 verbatim=archive 202609.md『热冷整编 "
    "2026-09-30 r258 bm-c 窗批』节（正典面=research/INNOVATION_QUOTA_W8_PREREG_DRAFT.md §C1+results/_r449bmb_w8_probe.json）。"
)

ENTRY_R255 = (
    "- [2026-09-30 06:1x r255 bm-c] pool worker stale-tree claim 假失败坑（SLOT-6 实弹）：本机 worker 06:02 "
    "从 origin-fetched 池视图认领他机刚入池条目——runner 仅存在于本地未拉取的 origin commit 中=claim 后 "
    "0.0s rc=2 机制假失败（0.0003 core-hours·零科学烧批·outcome=fail 语义=freed 正确返还池·本地拉取后"
    "下 tick 自愈真烧）；危害面=ledger 假失败行+认领周期空耗。正法方向=worker claim 前置 runner 本地在"
    "树核验（O-2210 机件改动须单写者窗·本轮未擅改）。How to apply：他机新入池条目真烧=本地树已拉取之后；"
    "worker 秒级 rc=2 先查 runner 在树性再判机制故障。"
)
POINTER_R255 = (
    "- 冷层指针：r255 bm-c pool worker stale-tree claim 假失败坑（worker 秒级 rc=2 先查 runner 在树性再判"
    "机制故障·正法=claim 前置在树核验=O-2210 待单写者窗）全文 verbatim=archive 202609.md『热冷整编 "
    "2026-09-30 r258 bm-c 窗批』节。"
)

with open(CODELY, encoding="utf-8") as f:
    text = f.read()

assert ENTRY_R449 in text, "r449 entry not found verbatim in CODELY"
assert ENTRY_R255 in text, "r255 entry not found verbatim in CODELY"
size_before = os.path.getsize(CODELY)

# cut verbatim entries, put pointers in their place (r255 pointer at r255's position,
# r449 pointer at r449's position; both pointers grouped at the Feedback cold-pointer block end)
text = text.replace(ENTRY_R449, POINTER_R449)
text = text.replace(ENTRY_R255, POINTER_R255)

with open(CODELY, "w", encoding="utf-8") as f:
    f.write(text)

# append archive section with verbatim entries
SECTION = (
    "\n\n## 热冷整编 2026-09-30 r258 bm-c 窗批\n\n"
    "（CODELY.md 超线当窗整编·11,159B→目标 <10,240B·两条 verbatim 迁入·零丢失三断言由 "
    "_r258bmc_codely_reorg.py 承载）\n\n"
    + ENTRY_R449 + "\n\n" + ENTRY_R255 + "\n"
)
with open(ARCHIVE, "a", encoding="utf-8") as f:
    f.write(SECTION)

# zero-loss assertions
with open(ARCHIVE, encoding="utf-8") as f:
    arch = f.read()
with open(CODELY, encoding="utf-8") as f:
    cody = f.read()
assert ENTRY_R449 in arch, "archive lost r449 verbatim"
assert ENTRY_R255 in arch, "archive lost r255 verbatim"
assert ENTRY_R449 not in cody, "CODELY still carries r449 verbatim"
assert ENTRY_R255 not in cody, "CODELY still carries r255 verbatim"
size_after = os.path.getsize(CODELY)
assert size_after < 10240, f"CODELY still over line: {size_after}"
print("reorg OK:", size_before, "->", size_after, "bytes; archive section appended; 4 assertions PASS")
