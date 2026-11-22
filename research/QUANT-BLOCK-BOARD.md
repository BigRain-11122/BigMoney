# 量化线块面看板

generated 2026-11-22T23:21:07+08:00 | 块面 22 · 绿 22 · 红 0 | 队列待跑 0 | 线态 **LEGIT_IDLE**

线态读法：BUSY=队列有活；LEGIT_IDLE=全绿且无 pending（合法的空转）；STARVING=有红块却没活可干（等于断供）。

- 数据：7/7 绿
- 研究：5/5 绿
- 构造：3/3 绿
- 风控：2/2 绿
- 治理：5/5 绿

| 块面 | 粒度 | 席位 | 技能 | 状态 | 证据 | 红了怎么办 |
|---|---|---|---|---|---|---|
| 期货日线落地（10 品种）（D1_fut_daily） | 品种级：每个 csv 必须连续且最新 bar 等于最近交易日 | 数据管道席 | data-quality-checker | 🟢 GREEN | modal bar 2026-11-20 (100% of 1 sampled dates) | — |
| 指数日线（沪深300/500/50/1000）（D2_index_daily） | 指数级 | 数据管道席 | data-quality-checker | 🟢 GREEN | modal bar 2026-11-20 (100% of 1 sampled dates) | — |
| ETF 日线（1500+）（D3_etf_daily） | 标级 | 数据管道席 | data-quality-checker | 🟢 GREEN | modal bar 2026-11-20 (100% of 1 sampled dates) | — |
| A股日线面板（5000+）（D4_astock_daily） | 标级 + 面板缓存 | 数据管道席 | data-quality-checker | 🟢 GREEN | modal bar 2026-11-20 (98% of 5 sampled dates) | — |
| 转债面板（含退市，无生存者偏差）（D5_cb_panel） | 券级 | 数据管道席 | data-quality-checker | 🟢 GREEN | 192.0h old | — |
| 回购/现金利率（GC001 等）（D6_cash_rate） | 品种级 | 数据管道席 | data-quality-checker | 🟢 GREEN | modal bar 2026-11-20 (100% of 1 sampled dates) | — |
| 数据车道新鲜度看板（D7_lane_board） | 车道级 | 数据管道席 | data-quality-checker | 🟢 GREEN | 3.8h old | — |
| 候选假设队列（唯一入口）（R1_hypothesis_queue） | 假设级：每条必须有 decision/判据/车道/时限 | 研究席 | trade-hypothesis-ideator, gate-rigor | 🟢 GREEN | keys ok, 0.0h old | — |
| 试验场执行器（20 分钟 tick）（R2_bench_executor） | 格级 | 研究席 | quant-backtest-gate | 🟢 GREEN | 0.2h old | — |
| 判据冻结 + 功效闸（R3_gate_power） | 臂级：每臂要有 MDE 与目标边际比较 | 判据席 | quant-backtest-gate, gate-rigor | 🟢 GREEN | keys ok, 0.2h old | — |
| 新 bar 复验（判决翻转警报）（R4_revalidate） | 格级 | 复验席 | quant-backtest-gate | 🟢 GREEN | 0.4h old | — |
| 独立复算（另一套实现）（R5_independent_audit） | 结论级：每条被引用的绝对收益数至少一次独立复算 | 审计席 | quant-backtest-gate | 🟢 GREEN | keys ok, 0.3h old | — |
| 生产书持仓与 k 值（C1_book_positions） | 标的级 | 组合席 | position-sizer | 🟢 GREEN | 4.1h old | — |
| 成本模型（每格声明 bp/边与换手版本）（C2_cost_model） | 格级 | 成本席 | cost-ledger, quant-backtest-gate | 🟢 GREEN | every finished strategy cell prints its cost rate | — |
| 容量与冲击（ADV 口径）（C3_capacity） | 线级 | 容量席 | position-sizer | 🟢 GREEN | 4.7h old | — |
| 回撤断路器（C4_drawdown_guard） | 书级 | 风控席 | drawdown-circuit-breaker | 🟢 GREEN | 314.2h old | — |
| 纸盘净值对账（C5_paper_recon） | 账户级 | 对账席 | cost-ledger | 🟢 GREEN | verdict=PASS, 3.1h old | — |
| 试验台账（只追加）（G1_ledger） | run 级 | 记账席 | cost-ledger | 🟢 GREEN | 0.2h old | — |
| 轮报/日报（G2_round_report） | 轮级 | 轮报席 | session-handoff | 🟢 GREEN | 59 files, newest 3.8h | — |
| 教训转化（每条否/警报→一条可查教训）（G3_lesson_loop） | 结论级 | 复盘席 | signal-postmortem | 🟢 GREEN | 0.2h old | — |
| CEO 一页纸（读者面）（G4_ceo_page） | 决策级 | 汇报席 | fleet-ops | 🟢 GREEN | 3.8h old | — |
| 空转/闲置哨兵（G5_idle_sentinel） | 小时级 | 值守席 | fleet-ops | 🟢 GREEN | board 0.0h old | — |
