# -*- coding: utf-8 -*-
"""_r431bmb_w9_berth_repick.py -- W9 draft-window berth amendment (2nd collision:
bm-a r435 t101_v4_a7_scrnull=20309000 landed same-window) -> final pick
20309500/20310000/20310500 (three-step law green vs 108-key registry)."""
p = "research/TRIAL_LABOR_W9_PREREG.md"
t = open(p, encoding="utf-8").read()

# A. L3 banner berth numbers
old_a = "泊位 **20309000/20309500/20310000**·冻结时点三步律复验·撞带重取+横幅注记"
assert t.count(old_a) == 1, "A"
t = t.replace(old_a, "泊位 **20309500/20310000/20310500**·冻结时点三步律复验·撞带重取+横幅注记")

# B. L4 collision-disclosure line rewrite (locate by unique prefix)
i = t.find("> **种子泊位撞带重取披露")
assert i > 0, "B-locate"
j = t.find("\n", i)
old_line = t[i:j]
new_line = ("> **种子泊位撞带重取披露（起草窗内两连撞·三次推位·横幅注记）**：+500 步进律自然推位=20308000/20308500/20309000"
            "→ **一撞**：`t101_v4_a2_scrnull`=20308000+`t101_v4_a2_corrnull`=20308500（bm-a r433/r434 注册占用·起草时点 registry 107 键实读）"
            "→ 首取 20309000/20309500/20310000（三步全绿）；"
            "→ **二撞（rebase 收口窗实弹·bm-a r435 同窗冻结 T-101-V4-A7-PRESCREEN 注册 `t101_v4_a7_scrnull`=20309000·108 键入树实读）**"
            "→ **终取 20309500/20310000/20310500**（重验三步全绿：步1 registry 108 键 int 值全集盘点=三值零精确撞带+带内零其他键；"
            "步2 新基首元素与全部既有基互异且新基间互异；步3 rg 全仓扫描命中=data\\daily 与 Money0923 CSV volume 列数值巧合"
            "〔sh510980/sh516130/sh588860=20309500·sh562550=20310000·601211/sz159937/159516=20310500·69 批先例排除面〕"
            "+本起草轮泊位声明文档〔prereg/MSG/轮报告·泊位声明面≠种子面·W6/W7 同族判例〕"
            "——**三步全绿·W5 撞带重取先例新态=一窗两连撞**）。**冻结步依法复验**（撞带重取先例在册·冻结时点若再撞=三步律再重取+横幅注记）。")
t = t.replace(old_line, new_line)

# C. sec.3 seed base line (exact literal)
old_c = ("seed 基起草泊位 `trial_labor_w9_gen`=20309000 / `trial_labor_w9_scrnull`=20309500 / `trial_labor_w9_unc`=20310000**"
         "（**起草时点三步律已过 2026-09-29 15:4x·撞带重取已兑现**：+500 自然推位 20308000/20308500/20309000 撞 t101_v4_a2 批〔bm-a r433/r434〕"
         "→重取 20309000/20309500/20310000 三步全绿〔registry 107 键零精确撞带+首元素互异+rg 全仓零种子面命中·命中面=CSV volume 列巧合与起草轮临时件〕；"
         "**冻结步依法复验**——撞带重取先例在册）")
assert old_c in t, "C"
new_c = ("seed 基起草泊位 `trial_labor_w9_gen`=20309500 / `trial_labor_w9_scrnull`=20310000 / `trial_labor_w9_unc`=20310500**"
         "（**起草窗内两连撞重取兑现·三步律终态全绿 2026-09-29 15:5x**：+500 自然推位 20308000/20308500/20309000 一撞 t101_v4_a2 批〔bm-a r433/r434〕"
         "→首取 20309000/20309500/20310000→二撞 t101_v4_a7_scrnull=20309000〔bm-a r435 同窗冻结·rebase 收口窗实读 108 键〕"
         "→终取 20309500/20310000/20310500〔registry 108 键零精确撞带+首元素互异+rg 全仓零种子面命中·命中面=CSV volume 列巧合与泊位声明文档〕；"
         "**冻结步依法复验**——撞带重取先例在册）")
t = t.replace(old_c, new_c)

# D. null-family seed
old_d = "seed=`trial_labor_w9_scrnull`=20309500（派生 [20309500, i]）"
assert t.count(old_d) == 1, "D"
t = t.replace(old_d, "seed=`trial_labor_w9_scrnull`=20310000（派生 [20310000, i]）")

# E. judge seed
old_e = "seed=`trial_labor_w9_unc`=20310000（派生 [20310000, cell_idx]）"
assert t.count(old_e) == 1, "E"
t = t.replace(old_e, "seed=`trial_labor_w9_unc`=20310500（派生 [20310500, cell_idx]）")

# F. sec.9 freeze-step line
old_f = "（泊位 20309000/20309500/20310000·冻结时点三步律复验·撞带重取+横幅注记）"
assert t.count(old_f) == 1, "F"
t = t.replace(old_f, "（泊位 20309500/20310000/20310500·冻结时点三步律复验·撞带重取+横幅注记）")

open(p, "w", encoding="utf-8").write(t)

# verify: no stale standalone berth triplet outside the historical narrative
import re
stale = t.count("泊位 **20309000/20309500/20310000**") + t.count("泊位 20309000/20309500/20310000·")
print("amended OK; stale berth anchors remaining:", stale)
print("new-band mentions:", t.count("20309500/20310000/20310500"))
