# -*- coding: utf-8 -*-
"""_r431bmb_addendum.py -- MSG addendum + round-report correction line for the
2nd seed-band collision discovered in the rebase-close window (bm-a r435
t101_v4_a7_scrnull=20309000 same-window freeze landed)."""

msg_p = "fleet/inbox/MSG-20260929-1551-bmb-ALL-W9-prereg-draft-berth.md"
t = open(msg_p, encoding="utf-8").read().rstrip()
t += ("\n\n## 补章（rebase 收口窗 15:5x·起草窗内二次撞带·泊位终取）\n\n"
      "- **二撞实证**：bm-a r435 同窗冻结 T-101-V4-A7-PRESCREEN 注册 `t101_v4_a7_scrnull`=**20309000**"
      "（与本 MSG 第 2 条首取带的 gen 位撞带·108 键入树实读）——同窗双机推位竞态=一窗两连撞新态（W5 先例扩展面）。\n"
      "- **终取**：W9 三泊位=**20309500/20310000/20310500**（trial_labor_w9_gen/scrnull/unc·"
      "rebase 收口窗对 108 键 registry 重验三步律全绿：零精确撞带+首元素互异+rg 全仓零种子面命中"
      "〔命中=data\\daily 与 Money0923 CSV volume 列数值巧合+本声明文档泊位声明面〕）。\n"
      "- prereg（research/TRIAL_LABOR_W9_PREREG.md）draft 期编辑窗内已同步修订（横幅+§3+§9 四处·"
      "历史叙事保留首取带注明）；冻结步仍依法三步律复验。\n")
open(msg_p, "w", encoding="utf-8").write(t)

rr_p = "logs/iteration-loop/round_reports.md"
t = open(rr_p, encoding="utf-8").read().rstrip()
t += ("\n2026-09-29 15:59 | r431 补 | 收口窗更正：push 撞 bm-c r224+bm-a r435 同窗双新进→rebase 20 UU "
      "（16 分类器配方+4 live_usage 手工归类=r428 先例同日幂等再生成面；rolling-ledger union 零丢失 "
      "compute_audit 202 行+regime_state 0+0；snapshot 逐件深时探针取新·双胞胎同侧·js 包随 json 侧；"
      "resolver=results/_r431bmb_resolve.py 留痕）→ **起草窗内二次撞带**：bm-a r435 同窗冻结 A7 批注册 "
      "t101_v4_a7_scrnull=20309000 与 W9 首取带 gen 位撞→**W9 泊位终取 20309500/20310000/20310500**"
      "（108 键重验三步律全绿·prereg draft 编辑窗同步修订+MSG 补章·W5 撞带重取先例新态=一窗两连撞）。\n")
open(rr_p, "w", encoding="utf-8").write(t)
print("MSG addendum + round-report correction appended")
