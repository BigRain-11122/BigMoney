# -*- coding: utf-8 -*-
"""_r250bma_append_memory.py -- append R250 pitfall entry to CODELY.md (UTF-8 safe)."""
ENTRY = (
    " - [2026-09-26 14:3x] 坑律（bm-a R250·T-73 s3 slice-2·CN-DIV-LOWVOL-ROT 探针门设计面·"
    "r221 装载形态族新维·E1 冻结期自捕零外泄）：**多腿 corpus prereg 的日期对齐门禁用全局集合恒等——"
    "510880(4784 根) vs 512890(1862 根) 的 2922 根差全在联合窗前（2019 上市前），全局恒等门=结构性假红**；"
    "正律=①对齐门作用域=联合窗内（joint_first 起）②错位日（实弹：512890 corpus 缺 2021-10-22 而 510880 有="
    "数据缺口非停牌）冻结成清单随探针引用件落盘、runner 断言恒等 else fail-closed exit 2（日期漂移拒跑）"
    "③批时间线口径=intersection（双腿每 batch 日皆可估值可成交）。"
    "连带律=**null seed 基登记前移到 prereg 冻结 commit 内**（CN-REV R245 写基→R246 跑前扫描才撞号让位的"
    "两段式，制度化为一段式：登记与冻结同 commit，撞号窗口消灭）。"
    "指针=results/_r250bma_rot_probe.py+research/CN_DIV_LOWVOL_ROT_PREREG.md §2/§3.4+"
    "scripts/science_gates.py SEED_REGISTRY cn_div_lowvol_rot_p1 行\n"
)
with open("CODELY.md", "a", encoding="utf-8") as fh:
    fh.write(ENTRY)
print("appended", len(ENTRY), "chars")
