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
| stage-2a | paper 前向保护件（deliverable 5，**live-gate 前置必需**）：live/paper.py 加性默认关 flag 消费登记册做断点日 no-trade/剔除标记 | **HOLD（O-1325 显式 T-20 接力时序；bm-a MSG-1608 车道在飞 live/paper.py）**——其 G6 生产切换后落地 |
| stage-2b | 官方公告证据核验（数据面探针，逐事件来源 URL，marginal 级改判如实记） | 未开工（ratios 现为 price-implied 披露态） |
| stage-2c | 幻影贡献量化批（预注册反事实面：暴露行剔除 vs 基线的 ΔSharpe/Δ年化 per trader，两选项 a 的实测证据） | 未开工 |
| stage-3 | 调整因子序列+调整视图面板（选项 b 落地面） | **DONE（r59 bm-c·O-1612 今日必交）**：adjust_factors.json + adjusted_view/×19 parquet + 六门全 PASS（scripts/t19_adjust_view.py）；因子=price-implied 回调整（断点日真收益吸收为 0·待 stage-2b 官方比例）；选项 b **消费**裁决仍缓议（O-1325：stage-2c 出数后裁），本件为加性落地资产；GF 硬门（O-1310 s3）据此放行深轴清洁版重跑 |

### stage-3 交付语义（r59 落地·O-1612）

- **资产面**：`data/consolidation/adjust_factors.json`（21 事件因子+逐员断点日清单=选项 a 守卫消费面，含边界面语义）+ `data/consolidation/adjusted_view/<sym>.parquet`×19（回调整 OHLCV(A)，含 adj_factor/cons_break 列；volume 反比缩放=成交额不变律；amount 不动=真成交货币额；raw 面恒权威，D2 零改写）。
- **因子口径披露**：`factor_k = close_k/prev_close_k`（price-implied）——断点日 k 的真实市场收益被吸收（构造上=0）；官方折算比例=stage-2b 证据槽未填，marginal 级事件仍可能改判为真实极端日。
- **消费律（O-1325 维持）**：评估/纸盘默认面=选项 a 守卫（断点日+边界面打旗/剔除）；调整视图服务于深轴清洁版重跑（O-1612 条 1）与选项 b 消费裁决（stage-2c 出数后）。
- **六门**：GA 断点日连续性（=0·写盘后验证）/ GB 未触段值精确等（float64 归一披露）+非断点收益保全 / GC 成交额不变 / GD 登记册对账（6dp 容差如实标）/ GE 覆盖 / GF 确定性（门侧重算与写盘 JSON 逐位同）→ results/t19_adjust_view_gates.json verdict PASS。

## 四、纪律与车道

- 注册证据/引擎/raw bars/live.paper 现行语义：零触碰（stage-2a 才动 paper.py，加性默认关）。
- 与 T-08（bm-a 双腿验证在制）同族不同文件零接触；bm-b XSTOCK 在飞零接触。
- 每阶段开工前 MSG 认领声明（F-04）；量化批走 PREREG_TEMPLATE（v2 判据经 science_gates 共享库）。
