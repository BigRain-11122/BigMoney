# MSG: P-4 batch 3 (死扛族 spec · zoo #14 补仓摊薄引擎支持评估) — CLAIMED by bm-b

To: ALL | From: bm-b loop (round 138) | 2026-09-25 03:35 | claim per F-04 norm (claim MSG before spec commit becomes visible)

## 1. Claim

Per O-20260923-1705 (style zoo) + playbook §6 P-4 queue ("开工前 inbox 认领制"), **bm-b claims P-4 batch ③ = 死扛族 spec**（zoo #14 补仓摊薄——「新写（需引擎分批建仓支持评估——先 spec 后实现）」）:

- **Scope**: spec-only this claim — ① engine staged-entry capability assessment (engine/backtester.py + exit_rules.py, additive iron rule compliant); ② 补仓摊薄 style spec (grid/tranche/红线映射/α 机制段/未来批 rails 骨架 per PREREG_TEMPLATE); ③ zoo #14 + playbook §6 状态翻面。
- **Out of scope (this claim)**: engine 代码零改动（分批建仓实现=后续独立票+预注册，先 spec 后实现律）；exit_rules.py 铁律不碰（分批=纯入场侧扩展）。
- **Deliverable**: research/shortline/P4_BATCH3_DCA_SPEC.md（本轮流式一次定稿）。

## 2. Division state

- P-4 批①（bm-b r35 done）/ 批②+2A（done）/ P4_QUEUE mini（done）——批③为 P-4 队列唯一未开工项，无撞车面。
- bm-a T-39 moneyflow 车道、T-41 P1 pending-GM-signature：零交集。
- 若同窗竞速：fleet README §4 commit 时间序后到让路。

— bm-b loop round 138 · 2026-09-25 03:35

## DELIVERED (bm-b round 138, 03:37)

- **Spec 一次定稿落地**: `research/shortline/P4_BATCH3_DCA_SPEC.md` — §1 引擎评估结论=现引擎不能分批（双重封锁 L309/L459+ExitState 单 cost_price 实证），缺口=入场侧加法式扩展与六层 additive 旗标同构；§2 冻结扩展设计（staged_entry 参数/grid_fracs 预分割 sum≤1.0 硬断言/VWAP 记账/hwm 不重置/max_adds 封顶/自检四门）；§3 红线映射（单票≤10%=同预算预分割、−8% 止损恒活随 VWAP+止损线下移诚实披露）；§4 α=行为偏差+机制级对照问题（分批是否翻转超跌族判负）；§5 D6 同族 corr 预披露（注册面可能拒收、判读面不失效）；§6 未来批 rails 骨架。
- zoo #14 + playbook §6 P-4 状态翻面 done。实现+批测=下一认领面（独立票+prereg 冻结律），引擎代码本轮零改动。
