# PAPER_GUARD_DUAL_RAIL 预注册 · T-2026-09-24-20 deliverable-1（跑前冻结）

> 批类=**执行保真验收批（tool-validation·工程 lane）**——零 α 主张、零试验格、`ledger_trials_added=0`（cost_v2_gates / CASH_LEG T-09 / T-14 §1 同源先例）。本件冻结于实现之前；跑后只许回填 §7 占位，禁改判据。
> 权威链：GM 裁决 O-20260924-1310 §二.2（paper 前向守卫双轨=批准）→ T-20 票面 deliverable-(1)→ 本件。实现轮（R72+）按本件逐字执行。
> 认领：F-04 MSG-20260924-1320 先行 + 票据 claimed @ commit db94b0e（R70）。

## §0 批件身份

- 批名/批号：PAPER_GUARD_DUAL_RAIL / 0 试验格（验收门 G0-G6 为判定门非统计门；不产生 N_eff——注册面零触碰）。
- 部门归属：dept:工程（前向记账面=交易部消费，报告制）。
- 算力预算：build_guard 一次 ~秒级（48 符号向量化）+ 验收门 ~10 次引擎跑（冻结面）+ 合成 fixture 跑 ≈ **<2min，轮内可完成，无需后台化**。批报告带 audit 段（compute_audit CLEAN）。
- 截止纪律（票面绑定约束）：**实现完成于 2026-10-01 前**（首个完整纸盘月自第一天即跑守卫语义）；滑期=升级 GM 做月界选择，节点自决权不含改月界。

## §1 α 机制段【N/A 声明——执行保真面非信号面】

四选一均不适用：本批不产生任何新信号/策略函数/因子，只把**既有 ETF 域执行保真守卫**（T-14 冻结构造）接入前向纸盘记账，属执行层语义保真（T-14 §1 同源：「任何执行保真性批都不产生新 α 主张」）。

**D6 同族相关性准入：N/A**——零新策略函数，无 corr 可算；在册 6 员评估语义仅记账面变化，注册证据零触碰（G4 硬门）。

## §2 双轨契约【核心冻结——A/B 轨划分逐字】

**A 轨（legacy·逐字节不动）**：`anchor_gate`（注册证据复现路径）**永不接收 fill_guard**；注册件 evidence 块、`hr.py`、`firm/traders/*` 注册字段——零触碰。逐位性证明=T-14 A-gate 6/6 复跑先例 + smoke 锚定门（G1）。

**B 轨（guarded·前向记账面）**：以下两处生产路径接收守卫，其余一律不动：
1. `paper_run(...)`——前向窗口权益/交易/月度聚合（months_tracked/monthly_returns/current_dd 供给面）；
2. `cost_x2_check(...)` 的滚动重算腿——窗口 Sharpe 与真实成交一致性要求同轨（x2 看护的注册期种子 `backtest.cost_x2` 恒为 legacy 种子，零触碰；滚动腿自接线起为 guarded）。

**守卫数据面=复用禁重建**：`scripts/t14_rules_fidelity.build_guard(prices_full)` 逐字复用（票面 mandatory）；每次 paper 运行**现场构建**（秒级，禁缓存防陈旧面）；引擎消费语义=`run_backtest(fill_guard=...)` P4-B2 逐字（买拒单=pending 丢弃不重试；卖顺延=存原 ExitAction（reason/close_fraction 原样）次一可卖收盘强制执行；守卫面外的日期=可成交 True 默认）。**159985 维持 T+1**（O-1310 do_not_land；引擎 is_t0 面零触碰）。

**一次性切换语义（防语义混杂，票面「月内切换禁止」的实现面）**：接线完成时对 paper_start→当日的**整个前向窗口**按 guarded 全量重算一次——9 月为残月本就不计 months_tracked（整月规则），全窗重算=纸盘台账自第一根 bar 起即守卫语义，零 legacy/guarded 混杂；月度判定阈值（hr.py）零改动。

## §3 数据与成本口径

- 面板：core48 `data/daily`（`live.paper.load_core` 现行面，raw per-symbol 含停牌缺口——build_guard 的输入面契约天然匹配）；`510300` 在池=日历源可用。
- **evidence_cutoff=2026-09-23**（前向锁盒 D2；results JSON 顶层 `science_gates.cutoff_meta` 键）：**验收对照一律在截断冻结面上做**（G2 等价门 vs 改动前基线——R27 数据漂移坑律：活数据增长必然假红，验收面必须截断到冻结时点）；生产前向 accrual 面=活数据照常增长（paper 域本性，非证据面）。
- 成本口径：**V1 legacy 默认 FeeSchedule（13bp）**——双轨只改成交可行性，零触成本模型（铁律）；守卫与 CostPatch 正交（x2 滚动腿维持 ×2 压测语义不变）。
- 数据完备门：6 员注册面 + 冻结面板在位（smoke 20 项基线即门）；守卫构建门=build_guard diag 非空 + 列覆盖 48/48。

## §4 验收门（G0-G6·跑前写死·全绿=deliverable-2..4 完成）

- **G0** smoke 全绿（实现轮若加双轨 selftest 项则 23→24 项，计数随项声明）。
- **G1 A 轨逐位**：anchor_gate 6/6 PASS（evidence_cutoff 截断语义不变）+ T-14 A-gate 式复跑逐位；锚路径代码 diff=零（A 轨无 fill_guard 参数）。
- **G2 legacy 等价回归**：guard=None（缺省路径）与全 True 守卫在冻结面（cutoff 2026-09-23）上，paper_run/cost_x2_check 输出与改动前基线**逐字节相同**（改前基线=实现 commit 前先行落盘；缺省默认=None=他人调用面行为不变）。
- **G3 合成前向用例**（fixture 面板，离线确定性）：①跌停封板日卖退出→顺延至次一可卖收盘、reason 保留、封锁日权益按 close 盯市可见；②一字涨停日买入→拒单丢弃、无持仓开立；③停牌日双向封锁；④双跑确定性 identical。
- **G4 零触碰审计**：注册件 evidence 块逐字节不变（纸盘 additive 块除外——既有行为）；hr.py 零 diff；注册成本种子零触碰。
- **G5 披露块在场**：`results/paper/<ID>_paper.json` 新增 additive `forward_guard` 块：`{enabled, guard_source="t14_rules_fidelity.build_guard", buy_rejected_n, sell_deferred_events_n, deferred_days_total, first_deferred_date, window_semantics="guarded", as_of}`；**月度简报/记分卡判据零改动**（10-31 首检条款不变——守卫使首月更诚实，非另立门）；简报/记分卡对披露块的显示接线=后续 additive 小步（报告制）。
- **G6 切换收口**：接线 commit 落地后首个 `python -m live.paper` 生产跑=全窗 guarded 重算一次完成；六员 months_tracked 语义不变（9 月残月仍不计月）；x2 看护台账新条目带 `window_semantics` 谱系字段（additive）。

**产物**：`live/paper.py` 加性改动 + `scripts/paper_guard_gates.py`（验收 runner，cost_v2_gates/cash_leg_gates 家族范式）+ `results/paper_guard_dual_rail.json`（顶层 evidence_cutoff + audit 段 + G0-G6 判定 + guard_totals 快照）+ 本件 §7 回填。

## §5 跑前预测（写死于实现前，跑后对账）

1. G1 六锚零漂移=PASS（构造性保证——A 轨不接线），置信 >99%。
2. G2 等价门 PASS（全 True 守卫≡缺省≡改动前），置信 90%（风险=守卫面 reindex 细节差异）。
3. 切换时点 6 员前向窗 guard 事件数≈**0**（窗内仅 1-2 根 bar、09-23 无封板日预期；若有=≤2 事件），对窗口 Sharpe 影响≈不可测。
4. G3 合成四用例首版通过率 3-4/4（P4-B2 gates 8/8 先例但集成面为新——中等置信，失败即修不留账）。
5. 披露块/台账谱系字段对 10-31 首检路径零影响（hr 读数不消费守卫字段）。
6. 实现总时长 ≈1-2 个 OS 轮（R72 实现+G 门、R73 收口+简报显示接线候选）。

## §6 批件纪律

- 零试验入账（`ledger_trials_added=0`）；G 门跑批不写 trials_ledger（tool-validation 先例）；audit 段必带。
- 回滚条款：G1/G2 任一红=实现回滚（live/paper.py 恢复改动前 commit），票面 deadline 风险即报 GM。
- 实现轮开工前再发 MSG（车道续作声明，防他机误认领 T-20 尾段）。

## §7 跑后实证【R80 bm-a 实现轮回填·2026-09-24】

- **G0** PASS：smoke 23/23（未加新 smoke 项——声明：双轨 fixture 用例由验收 runner G3 承载，23 计数不动，T-21 已交付件 G0 断言面保持相容）。
- **G1** PASS：anchor 6/6 且与改前基线逐位同；anchor_gate 源码零 fill_guard/build_guard；结构断言=T-21 两子串保持 + update_trader 新增 fill_guard=fill_guard。
- **G2** PASS：冻结面（09-23）6 员×四腿全逐字节同基线（default_run/alltrue_run/default_x2/alltrue_x2）；缺省路径零加性键发射；全 True 守卫加性键全零。
- **G3** PASS 15/15：买拒 3（S2 封板日 1+S3 停牌双封 2）、卖顺延 2 事件/2 天、first_deferred_date、reason 逐字保留、顺延恰 +1 交易日、封锁日 close 盯市可见、S2 入场位移与顺延抵消（hold 净零）、双跑确定、全 True noop。**首跑红=fixture 作者侧错**（信号 bar→执行 bar off-by-one：bar60 信号→bar61 首执行窗；S2 卖封锁腿漏写）——修 fixture 禁改判据（J18 律），修后 15/15。
- **G4** PASS：六员注册件 evidence 块（level/params/backtest 含 x2 种子/exit_overrides/created/evidence_cutoff）切换前后逐字节同；hr.py+monthly_briefing.py git 面零改动。
- **G5** PASS：6/6 results/paper/*.json forward_guard 块=冻结键集逐字（enabled/guard_source/buy_rejected_n/sell_deferred_events_n/deferred_days_total/first_deferred_date/window_semantics="guarded"/as_of）。
- **G6** PASS：接线 commit b8172ba 后首个生产跑 python -m live.paper=全窗 guarded 重算完成（prod_rc=0，双跑幂等）；months_tracked 0→0（九月残月不计月语义不变）；x2 看护台账尾条目全带 window_semantics 谱系字段；**六员窗口守卫事件全零**（窗口 1-2 bar 无封板日——§5 预测 3 命中，对窗口 Sharpe 影响不可测=零）。
- **runner 自修两处（判据零触碰）**：门循环 dispatch 签名 bug（G2 缺 P 参）；产物 JSON tid 键名 _paper 尾缀。
- **披露交互（已披露不阻断）**：T-21 已交付件 regime_enforce_gates 若未来重跑，其 G1a noop 键排除集需扩 T-20 三新加性键、其 G1b/G4 parity 需容 forward_guard 块（含逐跑 as_of）——无常设链重跑它，已交付判定件不受影响。

## §8 批后复盘【R80 bm-a】

- 预测对账：①G1 零漂移 PASS（构造性保证兑现）；②G2 PASS（reindex+fillna(True) 面未咬合，90% 置信兑现）；③切换事件≈0 兑现（全零）；④G3 首版红=fixture 编写期错非集成面错——实现一次落地全绿（预测「3-4/4 中等置信」按 fixture 质量错归档）；⑤披露块对 10-31 首检路径零影响兑现（G4 判据件零改动+hr 不消费守卫字段）；⑥总时长=1 个 OS 轮兑现（R80 单轮实现+门+切换；R72-79 连续退避为活会话让路，非本批滑期）。
- 教训：合成 fixture 造守卫格前必须先推信号 bar→执行 bar 位移（引擎 T 收盘→T+1 开盘契约是 fixture 作者侧最常见 off-by-one 源）；门 runner 自身 bug=runner 侧修，禁触判据（J18 律第二例证）。
