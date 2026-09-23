# P-5B 新员入职尽调批（预注册，跑前写死）

> **预注册纪律**：跑前写死（BACKTEST_PLAN 铁律③）。令链：CEO O-20260923-2345（CPU 全面动员）→ OPERATING_PLAN Phase 0 指名项（P-5 扩展 3 新员）→ 认领 MSG-20260923-2347。
> 脚本：`scripts/p5b_new_traders.py`（`p5_random_entry.py` 范式直系+**parallel_runner 并行跑**·O-2345 基建首用）。

## §1 问题

G2_FOLK 今夜注册 3 名新员（ENGULF-CE-01/NEEDLE-DE-01/DROUGHT-CE-01）在 P-5 同口径随机起点实弹下成色如何（新员 were selected on full history → robustness 分布复检，非新样本外——P5 同款诚实条款）。

## §2 口径（逐字继承 P5_RANDOM_ENTRY.md）

- K=50 起点/员（贪心 25td 间隔回退同款），种子 **20260924**（P-5 用 20260923，本批独立新抽样）；窗 3m/6m/12m=63/126/252td；warmup 252td；MIN_LISTED=24。
- 被动=同窗 EW buy&hold（起点在册成员）；**判据逐字**：PASS iff beat_rate_6m≥0.70 AND min_dd_6m≥−0.35。
- 锚定硬门：**全员 6 员锚定逐位复现**（新增 3 员必过——新注册件证据）；任一破=批无效。

## §3 跑数

150 策略跑（3 员×50）+50 被动窗+6 锚定=**206 跑**；**parallel_runner 首用**：worker=floor(核×0.8)≤25，audit 段记 workers 数（预期串行 ~90s → 并行 ~8-15s=CPU 动员实证）。

## §4 预注册预测（跑前写死）

1. 新 3 员 pooled beat_rate_6m ∈[0.45,0.72]（P-5 3 老员 0.6467 邻域；形态确认族低频低换手=政体敏感度低于 composite 高 β 员——**DROUGHT OOS 1.213 高分含政体红利率先折价读**）。
2. 最差起点窗大概率 2021Q4-2022Q2 熊段（P-5 同款）；NEEDLE 低频（73 笔/6.7 年）50 窗内多窗 0 交易→6m 收益≈0 vs 被动=beat 率被低换手拖累=**结构劣势预披露**。
3. dd 条款全过预期（6 员回撤谱 −2%~-20% 均远于 −35% 红线）。
4. 并行跑手与串行逐位一致（确定性引擎+种子固定；workers 只分不乱）。

## §5 判决

per-trader PASS/FAIL 落注册件**注记区**（不改 level/paper 数据）；全员 FAIL=诚实记录（成色定案靠纸盘长期证据不变）；禁调判据/换种子重跑。

## §6 试验账本

prev_total=**2521**（`results/shortline_p4_queue.json` 链头）+ 本批 **206** = **total 2727**。

## §7 跑后对账（跑前为空）

（待回填。）

—— quant 专管 GM 会话 · 研究部 · 2026-09-23 23:52 预注册
