"""r446 bm-b CODELY hot-cold reorg (over-line prevention law):
move r240 entry verbatim to archive 202609.md, leave one-line pointer,
append r446 surgical-residual pit entry. Line-level zero-loss check."""

import time

CODELY = "CODELY.md"
ARCHIVE = "research/memory-archive/202609.md"

NEW_ENTRY = (
    "- [2026-09-30 04:4x r446 bm-b] 手术过继残漏三连坑（W12 实弹·同一 "
    "r445 手术 tl11→tl12 留三残）：①screen-prep G-ANCHOR 轴长 14→15 "
    "IndexError（死轮已修·hermetic L13 leg 镜像新语法 15 元组但真数据 "
    "identity face 调用点仍 14）②screen-finalize gvvvsktsams_seg 九元组"
    "段字典初始化遗漏 NameError③judge-prep rsqr_meta 每腿 slope_sign_"
    "split 披露键缺 KeyError（打印段引用 A158 verbatim meta 不产出的"
    "键）——48/48 selftest 全数漏检；正解=真数据首跑逐异常点修（皆加性"
    "机械修复零判据触碰，grammar pin 67c86c9cf4ef1ca7 全程恒等）+ "
    "judge-prep 每腿披露面按全量面 sec.2(e) 计算镜像补；How to apply："
    "tlN→tlN+1 过继手术必带「真数据 identity face 三命令实弹首跑」"
    "（prep/finalize/judge-prep）收口步再宣告 runner 落地——W13 过继"
    "者（bm-a berth 已声明）按此律执行。"
)

lines = open(CODELY, encoding="utf-8").read().splitlines(keepends=False)
idx = [i for i, l in enumerate(lines) if "r240 bm-c]" in l]
assert len(idx) == 1, f"r240 entry not unique: {idx}"
i = idx[0]
moved = lines[i]
assert moved.startswith("### [2026-09-29 21:4x r240 bm-c]")

POINTER = (
    "- 冷层指针：r240 tick 15min 时限强杀·完整工件零 commit 接续律"
    "全文 verbatim=archive 202609.md『热冷整编 2026-09-30 r446 bm-b "
    "窗批』节（r443 jsonl 追加写吞换行坑指针随迁在档）。"
)
lines[i] = POINTER
lines.append(NEW_ENTRY)
text = "\n".join(lines) + "\n"
open(CODELY, "w", encoding="utf-8", newline="").write(text)

# archive append: new section + verbatim moved line
arch = open(ARCHIVE, encoding="utf-8").read()
assert moved not in arch, "entry already in archive"
section = (
    "\n\n## 热冷整编 2026-09-30 r446 bm-b 窗批\n\n"
    "> r446 CODELY append 前超 10,240B 硬线预防律当窗即办"
    "（moved 1/lost 0·行级零丢失校验）。\n\n" + moved + "\n"
)
open(ARCHIVE, "a", encoding="utf-8", newline="").write(section)

# zero-loss + size verification
arch2 = open(ARCHIVE, encoding="utf-8").read()
assert moved in arch2, "archive lost the moved line"
assert moved not in open(CODELY, encoding="utf-8").read(), \
    "CODELY still carries full entry"
size = len(text.encode("utf-8"))
print(f"reorg OK: moved 1/lost 0; CODELY {size}B "
      f"({'under' if size <= 10240 else 'OVER'} 10,240 line); "
      f"archive +{len(section.encode('utf-8'))}B")
