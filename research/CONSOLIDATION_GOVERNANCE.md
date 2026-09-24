# CONSOLIDATION_GOVERNANCE — 份额折算断点治理决策包（T-19 · stage-1 骨架）

- 票：fleet/tasks/T-2026-09-24-19-P1.json（GM 裁决 bm-c r47 T-14 发现开出的 P1 署名票）
- 认领：bm-c OS iteration loop round 48（commit 71f36a9 即锁）
- 定位：**呈 GM 裁决的决策包骨架**——本文件只固化事实面与两个候选方案；方案选择=GM 权，未裁前一切维持披露态。

## 一、事实面（全部机器可复核）

1. **事件登记册**（deliverable 1，已交付）：`data/consolidation/registry.json` — 21 事件/19 员，从 raw bars 用 T-14 冻结探测语义再推导、与冻结批 break_days 逐位对账（21/21 bit-exact）；每事件含 tier/实测 pct/近似折算比/前收盘-收盘证据/前日历日缺口旗/幅度分级（`consolidation_scale` |pct|≥30% vs `beyond_window_marginal`）。官方公告核验=stage-2 数据面探针（single-probe-first），marginal 级事件可能改判为真实极端日。
2. **六员暴露审计**（deliverable 4，已交付）：`results/t19_exposure_audit.json` — 记录格复现（ledger+0，g25/corr-watch 先例）+ 边界面扫描。**修正后的实质暴露**（T-19 修复 `_break_intersections` 类型空转缺陷后，r47 的「break_x 0/6」为空集假绿，已按 r56 披露面修正律改写冻结批交集面）：
   - **COMPOSITE-CE-02 · 7 行幻影暴露**：512100 2022-09-05（+176.27%，入场 08-25，3 分批腿）= **注册 IS 面内嵌 +176% 幻影利得**；513100 2022-01-14（-80.45%）；513500（-49.18%）；510500（-12.74%，marginal 级）；512800 2025-07-07（-49.69%，**OOS 段**）。
   - **COMPOSITE-CE-01 · 2 行幻影暴露**：513500 -49.18%（IS 边界面）；512800 -49.69%（**OOS 段**边界面）。另有 1 行 frozen 命中=断点日开盘入场（后跳价开仓，无幻影）。
   - **DROUGHT-CE-01 · 1 行**：512480 2021-03-29（-48.90%，IS 边界面）。
   - ENGULF / NEEDLE / VOLATILITY：真零暴露。
   - **边界面（boundary）**：frozen s5 的严格小于语义漏掉「断点当日收盘退出」=真实持有跨越暴露（入场<断点=跨越前持仓），审计行自带 `phantom_accrued` 分类。
   - **注册锚点零改写**（D2 锁盒）：以上全为披露行；幻影贡献的量化=stage-2 预注册反事实面（见 §三）。
3. **幻影方向双向**：既有利得（CE-02 512100 +176%）也有损失（513100 -80%/513500 -49%/512800 -50%/512480 -49%），IS 与 OOS 段都被污染——不是单向美化，是**双向失真**，方向与幅度按行可查。

## 二、候选方案（deliverable 3 · 双选项，正式 prereg 后呈 GM 裁决）

- **选项 a · guard 式处理**：评估面在断点跨越持仓行打旗/剔除（评价层守卫，注册面与 raw 面零改写）。优点：D2 锁盒天然合规、实现轻；缺点：剔除行改变有效样本构成（须同批记 null 面对账）。
- **选项 b · 调整面板切换（仅前向评估）**：官方比例核验后构造调整因子序列+调整视图面板，前向评估消费调整面；raw 面维持注册锚权威。优点：机理正确；缺点：依赖 stage-2 官方核验、引入双面板口径治理成本。
- **两选项不互斥**：可 a 先行（paper 前向保护件本就要求）+ b 随官方核验落地。

## 三、阶段计划

| 阶段 | 交付 | 状态 |
|---|---|---|
| stage-1 | 登记册 + 六员暴露审计 + 决策包骨架（本件） | **DONE（r48）** |
| stage-2a | paper 前向保护件（deliverable 5，**live-gate 前置必需**）：live/paper.py 加性默认关 flag 消费登记册做断点日 no-trade/剔除标记 | 未开工（独立验收：锚定门 6/6 零漂移 + smoke） |
| stage-2b | 官方公告证据核验（数据面探针，逐事件来源 URL，marginal 级改判如实记） | 未开工 |
| stage-2c | 幻影贡献量化批（预注册反事实面：暴露行剔除 vs 基线的 ΔSharpe/Δ年化 per trader，两选项 a 的实测证据） | 未开工 |
| stage-3 | 调整因子序列+调整视图面板（选项 b 落地面） | 未开工 |

## 四、纪律与车道

- 注册证据/引擎/raw bars/live.paper 现行语义：零触碰（stage-2a 才动 paper.py，加性默认关）。
- 与 T-08（bm-a 双腿验证在制）同族不同文件零接触；bm-b XSTOCK 在飞零接触。
- 每阶段开工前 MSG 认领声明（F-04）；量化批走 PREREG_TEMPLATE（v2 判据经 science_gates 共享库）。
