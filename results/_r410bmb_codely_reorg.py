# -*- coding: utf-8 -*-
"""r410 bm-b CODELY.md water-line reorg (append batch84 -> move 81/82/83
verbatim to archive -> pointer line -> zero-loss verify)."""
import io
import os

batch84 = (
    "- [2026-09-29 05:3x r410 bm-b] 坑律八十四批（门面自测夹腿连续 run 承重律·W6 runner 构建实录）："
    "组合面止损咬合腿在交替型许可序列（隔日 1/0）下构造性假阴——止损每 0→1 bar 重挂、"
    "穿透 bar 恒为挂入 bar 本身（t==arm 面不检查）→永不咬合；W5 阳线腿的连续 yang run"
    "（bars 4-20）是承重结构非装饰；W6 vconf 腿复刻时交替 volume 面首跑即假阴，"
    "正解=连续严格上升 volume run（滚动 med20 滞后于上升序列→全 run 恒读 surge）"
    "+穿透点置于 run 内部非首 bar（常数 run 会被滚动中位追平 catch-up 勿用）。"
    "How to apply：凡新波次门层自测夹腿 fixture，许可序列必须含≥2 连续许可 bar 且穿透点在其内部；"
    "上升序列持续越中位=可持续 surge run 的唯一构造。"
)

p_hot = "CODELY.md"
hot = io.open(p_hot, encoding="utf-8").read()
lines = hot.splitlines(keepends=True)

b81 = [l for l in lines if "坑律八十一批" in l]
b82 = [l for l in lines if "坑律八十二批" in l]
b83 = [l for l in lines if "坑律八十三批" in l]
assert len(b81) == 1 and len(b82) == 1 and len(b83) == 1, (len(b81), len(b82), len(b83))
moved = b81 + b82 + b83
print("batch84 bytes:", len(batch84.encode("utf-8")))
print("pre-append size:", os.path.getsize(p_hot),
      "-> post-append would be:",
      os.path.getsize(p_hot) + len(batch84.encode("utf-8")) + 1)

# 1) append batch84 (append-first per the water-line law)
lines.append(batch84 + "\n")
# 2) remove the three moved lines
keep = [l for l in lines if l not in moved]
# 3) pointer line inserted before batch84
pointer = (
    "冷层指针：坑律正典 2026-09-29 八十一/八十二/八十三批（r412 bm-a advisory 候选注记陈旧陷阱/"
    "r198 bm-c replace 长 CJK 串失配坑/r413 bm-a jsonl 多重集 union·取侧深探·卡死 rebase 复活）"
    "全文 verbatim=archive 202609.md『坑律归档 2026-09-29 r410 bm-b 窗批』节"
    "（r410 bm-b 窗水位律当窗整编·行级零丢失校验）。"
)
b84_idx = next(i for i, l in enumerate(keep) if "坑律八十四批" in l)
keep.insert(b84_idx, pointer + "\n")
io.open(p_hot, "w", encoding="utf-8", newline="").write("".join(keep))

# 4) archive the three lines verbatim with a section header
p_arc = "research/memory-archive/202609.md"
arc = io.open(p_arc, encoding="utf-8").read()
if not arc.endswith("\n"):
    arc += "\n"
section = ("\n## 坑律归档 2026-09-29 r410 bm-b 窗批（水位律当窗整编·行级零丢失校验）\n\n"
           + "".join(moved))
io.open(p_arc, "w", encoding="utf-8", newline="").write(arc + section)

# 5) zero-loss verification
arc_new = io.open(p_arc, encoding="utf-8").read()
ok = all(m.rstrip("\n") in arc_new for m in moved)
hot_size = os.path.getsize(p_hot)
arc_size = os.path.getsize(p_arc)
print("verbatim-in-archive:", ok)
print("hot size now:", hot_size, "(<10KB:", hot_size < 10240, ")")
print("archive size now:", arc_size)
assert ok and hot_size < 10240
print("REORG OK")
