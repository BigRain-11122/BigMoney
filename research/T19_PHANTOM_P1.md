# T19_PHANTOM_P1 — 幻影贡献量化批预注册（T-19 stage-2c · v1.0）

> 票：fleet/tasks/T-2026-09-24-19-P1.json（GM 裁决票·bm-c 自持 r48 起）· F-04 开工声明=MSG-20260927-1025。
> 模板：research/PREREG_TEMPLATE.md v2 · 判据共享库=scripts/science_gates.py。
> 定位：**呈 GM 裁决的测量批**（选项 a vs b 消费裁决的实测证据面，O-1325：stage-2c 出数后裁）——非策略注册批，零新成员零 ledger trials。

## §0 批件身份【跑前】

- 批名：T19_PHANTOM_P1；批内格数（N_eff 口径）：实测反事实格 **3**（受染员 CE-02/CE-01/DROUGHT 各 1）+ placebo 格 **150**（3 员×K50）+ 零暴露员基线复现自证格 3（ENGULF/NEEDLE/VOLATILITY，结构性零 Δ 只做 G-REPRO 过门）+ 行级归因 10 行（描述面不计数）。**零新策略函数入册=零 ledger trials（N_eff 不膨胀声明，stage-1 审计 ledger_trials_added=0 同律）**。
- 认领：T-19 已由 bm-c 持票（r48 起，同仓单执行体）；本批无分片共享态。
- 部门归属：dept:数据+研究。
- 算力预算：~155 次 6 年窗 rail 重放（run_rail 全窗确定性）≈ 8-15min → **池批**（runnable_pool 提交，禁轮内内联；R99 冻结→runner→池节奏）；批报告带 audit 段。

## §1 α 机制段【D6】

- **本批非策略批**：无新信号函数、无新成员、无搜索面——同族相关性准入检查（max|corr|≥0.7 拒收）适用对象=入批新策略函数，本批 **N/A 如实声明**（非绕闸：处置集=stage-1 冻结披露行、非幸存者搜索）。
- 被测量伪影的机制归类（四选一）＝**结构性**：份额折算/合并=基金申赎制度摩擦——折算不改变持有人真实财富（份额×单位净值不变），raw 价格面的单日跳变=纯记账事件非市场信息；其「收益」由评估面承担失真、无人付出代价=**非 α**（这正是「幻影」定义，与 T-14 发现、stage-2b 官方 21/21 双腿证据同源）。
- h 口径律（跑前冻结）：本批一切窗读数主口径＝**h10**（P1_WQ101 严口径/a158 s3 同律：h10 主判、h5/h20 仅报读列、换口径=数据窥探红线）。行级归因主读数=d0（断点日=制度事件唯一真值日）；h10 前向窗=选项 b 保留成分的报读列（§3）。

## §2 数据与面板【跑前探针事实】

- 宇宙/池：注册 6 员记录格复现面（T-14 A-rail：`_load_traders()`；prices=`LP.load_core()` 按 `LP.evidence_cutoff(t,·)` 逐员截断——与 stage-1 审计**逐位同镜**，r48 先例）。
  - **跑前勘误（2026-09-27 r78 bm-c·零判据触碰）**：上条机制指针 `_load_traders()` 读活注册目录——r242（T-78 s4 EXIT-OVERLAY-P1 winner wiring·2026-09-26·合法活面演进）后活目录 C01/C02/ENGULF 已非 T-14 冻结面，11:30 首磨 G-REPRO 正确拒绝（C01 IS 0.4696≠冻结 0.4514）。本条「逐位同镜」冻结意图的正确实现=**rail 输入钉 T-14 冻结 commit 4a5754a3 注册 blob 快照**（消费件：`data/consolidation/t14_anchor_face.json`·来源 sha+逐件 sha256 内嵌·runner `load_traders_t14_face()` 硬门自证）；§4 G-REPRO 硬门判据逐字不动。
- evidence_cutoff（D2 前向锁盒）：顶层 **2026-09-23**（=stage-1 审计件同锚；各员复现窗=注册窗冻结，cutoff 后新 bar 不回流本批）；结果 JSON 顶层必带 `science_gates.cutoff_meta("2026-09-23")`。
- 数据完备门（不过门禁出数）：G-REPRO——基线复现逐位等于 T-14 冻结 A 面（`_seg_clean` 位级、`a_face_matches_frozen` stage-1 同门）。
- 消费件（全只读）：data/consolidation/registry.json（21 事件）＋ results/t19_exposure_audit.json（处置集来源）＋ data/consolidation/adjust_factors.json ＋ results/t19_official_ratio_probe.json（官方比例+残差披露，stage-2b 21/21）。

## §3 方法学【冻结】

- **处置集（处置单位=tranche family）**：t19_exposure_audit 全部 `phantom_accrued=true` 行＝**10 行/8 族**：CE-02×7 行/5 族（512100@2022-08-25 三分批腿·断点 09-05 +176.27%｜513100@2022-01-10｜513500@2022-03-29｜510500@2022-08-24｜512800@2025-05-29·OOS）；CE-01×2 行/2 族（513500@2022-03-29·IS 边界｜512800@2025-06-19·OOS 边界）；DROUGHT×1 行/1 族（512480@2021-03-12·IS 边界）。同 symbol×entry_date 分批腿=同族共灭（窗并集）。**合法行不剔**：entry-on-break 行（如 CE-01 510500 2022-08-29 后跳价入场，无幻影）不入处置集。
- **反事实语义（option-a 评估层守卫的操作化）**：`run_rail(t, prices, P, guard=buy-guard)`——处置族 buy=False 于 [entry_date, exit_date) 全窗（族窗并集）→ 引擎原生 fill_guard 面（P4-B2 s3.1 加性接口，零 engine 改动）→ 该持仓窗内不存在。**语义披露**：`sizing_mode="equity_fraction"` 复合仓位下「事后从权益曲线抠行」数学上不良定义（后续入场 sizing 依赖在途权益），故 option-a 剔除＝入场抑制重模拟而非账面行删；与 stage-2a 生产件（paper no-trade/exclude flag）同族=fill 级标记。
- 度量：ΔSharpe/Δannualized（+max_dd/trades 披露列）per trader，IS/OOS 分段（`LP.seg_metrics` 同源口径）；**Δ 定义=反事实−基线**（正=剔除幻影后指标改善）。
- **null 对照（null bands）**：每受染员 K=50 placebo——抽样单位=tranche family，从该员复现交易清单的非处置族中均匀抽 n_k 族（CE-02 n=5／CE-01 n=2／DROUGHT n=1），同 [entry,exit) 族窗法构造 buy-guard mask 重模拟 → ΔSharpe null 分布（μ/σ/p5/p95）＋实测 Δ 分位读数。seed 基＝**68_500**（全仓 rg 探针零命中 2026-09-27 10:2x bm-c r74——Money02 legacy 数值巧合域除外；`SEED_REGISTRY["t19_phantom_p1"]` 同 commit 登记）。抽样不对称披露：placebo 族多为单腿、实际处置含 3 腿族（placebo 行数≲实测行数=保守面）。
- 行级归因（描述面）：每处置行=该行全窗 PnL＋d0 跳空成分（仓位×raw d0 收益）＋官方比例口径真收益成分（stage-2b 残差律：`|1/nav_step − price_implied|`=step 日真实市场收益+比例舍入，逐事件披露）＋h10 前向窗报读列（选项 b 保留成分面）。
- 成本口径：**V1 legacy（13bp×2）**——注册锚复现律（历史锚点复现恒用 V1 防漂移）；×2 面不入本批（测量批非生存批）。
- 账本：**零 `append_ledger`**（零新试验=测量面；stage-1 审计同律）。

## §4 判据【跑前写死】

- **无注册主张**：不跑 `g1_prime_v2`/`g2_registration_v2`（无新成员入册；如实声明非绕闸——本批出数为 GM 决策证据，非幸存者过闸）。
- **硬门 G-REPRO**：基线复现逐位==T-14 冻结 A 面（6 员全过；任一员 FAIL=批次中止零出数，禁以反事实面冒充基线）。
- **硬门 G-SET**：反事实交易清单=基线清单−处置族闭包（multiset 差==被抑制族全腿，无多余无缺失；placebo 同律=−抽样族闭包）——mask 构造缺陷必被此门捕获。
- **null 带判读（描述性两态）**：实测 Δ 落 placebo 带外（<p5 或 >p95）→ 标记「幻影贡献超出常规族剔除噪声」；带内→「与族剔除噪声同量级」。两态都如实呈 GM，**无 pass/fail 策略叙事**。
- 硬界设计三件套（D-20260925-01①）：本批无数据腐坏/健康判线→分布界主责=N/A 如实声明（非留空）；max 硬界=N/A（无阈值线）；跑前预测 (c) 已给极端日先验（§5）。
- 输出定位：GM 选项 a/b 裁决证据；**禁自行改注册锚/纸盘/marks（D2 锁盒+O-1325 消费律维持）**。

## §5 跑前预测【写死于跑前】

- (a) 方向：CE-02 IS 年化**显著下移**（512100 +176.27% 三腿横财为 IS 面内嵌，量级预期 10-40pp/年区间）；CE-02 OOS **上移**（512800 −49.69% OOS 损失剔除）。
- (b) CE-01 OOS 上移（512800 −49.69% 剔除）+IS 小幅上移（513500 −49.18% 边界行）；DROUGHT IS 小幅上移（512480 −48.90% 单族）。
- (c) **极端日先验（硬界三件套 (c)）**：本批唯一极端面=10 处置行断点日跳空（−80.45%..+176.27%），全部具官方双腿/公告证据（stage-2b 21/21）=制度事件非腐坏；placebo 族窗不含断点日→placebo |Δ| 数量级预期≪实测 |Δ|。
- (d) null 带：CE-02 实测 Δ 预期带外（含 +176% 尾部横财）；DROUGHT（单族 −48.9%）边际；CE-01（双族）带内~边际。
- (e) 分段小样本下 ΔSharpe 与 Δ年化可能因分母效应异向（如实披露，以两读数并列为准）。

## §6 产物

- scripts/t19_phantom_contribution.py（selftest 先行：mask 构造/G-REPRO/G-SET/placebo 抽样确定性/族窗并集，离线合成检查全过才准真跑）。
- results/t19_phantom_contribution.json（顶层 `cutoff_meta`；per trader：baseline/counterfactual/Δ/per-placebo band/percentile；per row：PnL+d0 成分+官方残差+h10 报读列）。
- results/t19_phantom_contribution.csv（孪生）。
- 本件 §7 回填＋research/CONSOLIDATION_GOVERNANCE.md stage-2c 行刷新＋GM 决策包刷新（O-1325）。

## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】

- G-REPRO（6 员）：
- G-SET（处置 8 族/placebo 抽样）：
- ΔSharpe/Δ年化 per trader（IS/OOS）：
- null 带与分位：
- 行级归因（10 行）：
- 预测对账 (a)-(e)：

## §8 批后复盘【占位】

- 预测对账＋gate_attrition.json 追加一行＋轮报告回执＋CODELY.md 行级追加。
