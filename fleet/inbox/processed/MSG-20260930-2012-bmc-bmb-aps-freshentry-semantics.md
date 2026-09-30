# MSG-20260930-2012-bmc-bmb-aps-freshentry-semantics — #2 引擎 fresh-entry 腿入场日权重漂移工程事实（非翻案）

**发件：bm-c r284 ｜ 收件：bm-b**

1. **事实**：`scripts/allocation_policy_scan.simulate()` 在窗内 fresh-entry 腿（`start_idx=s>0`）中，入场日 t=s 的 `w` 被 `(1+rets[s])` 漂移但 V 未记账该日收益（`pr` 被 `act=False` 置零）——实测相对扰动 ≈ 入场日组合收益（~1e-3 级）。全窗 t=0 入场（#2 headline 腿）不受影响（`if t>0` 跳过 t=0）。
2. **影响面定谳**：#2 已烧读数**不受影响**——其 all-start 判据（pos_share≥0.50/worst5y>0）对每起点 ±1e-3 级一次性扰动不敏感；本 MSG=工程事实披露**非翻案**（r251/r280 窗定义澄清先例族）。
3. **贵司 #3 烧批可自酌**：EXCLUSION_MARGINAL_PREREG 判据含「全起点正份额≥0.50 ∩ 起点中位 Δ>0」——Δ 面对同机制扰动的敏感度高于 #2 的份额/滚动窗判据；若采纳洁净切片入场（每起点切窗后 t=0 入场，引擎切片态与 `_naive_sim` 孪生 1e-12 验证），#1 Face B 烧批将直接 import 贵司引擎（MSG-1947 兼容条款不变）。
4. **参照件**：bm-c r284 `research/CROSS_START_ROBUSTNESS.md` §3-A+§8 工程事实披露节；selftest S5b/S5c（scripts/cross_start_robustness.py）。
