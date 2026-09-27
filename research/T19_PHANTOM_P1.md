# T19_PHANTOM_P1 — 幻影贡献量化批预注册（T-19 stage-2c · v1.1：§4 G-SET v2 零跑修正 2026-09-27 r79）

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
  - **v1.1 零跑修正（2026-09-27 12:0x bm-c r79·崩#4 实弹证伪）**：上行「清单恒等」隐含假设=重模拟下 (symbol, exit_date, hold_days) 恒等面不变——12:00:12 首磨实跑证伪：equity_fraction 路径依赖下抑制处置族→权益/持仓槽位路径变→**下游全部交易的入场日期/持有天数/数量联动漂移**（崩栈 missing/extra 各 40+ 行、2022-04→2025-07 跨全账户 9+ 符号、全部位于最早处置族之后=整路径漂移形态、零族窗内行=mask 无罪）。恒等面 multiset 恒等在重模拟语义下结构性不可满足，与 §3 自认「后续入场 sizing 依赖在途权益」同源但更广（含日期/持有面）。**G-SET v2（保留原门意图=mask 构造缺陷必被捕获）**：①硬门 A=族窗抑制精确性（反事实零笔派生入场落于任一处置/抽样族窗 [entry, exit)——欠抑制/守卫失效捕获）；②硬门 B=mask 面纯度（buy=False 面恒==族窗并集面——错键/漏日/野日捕获）；③**下游 identity 漂移=披露面非门输入**（per trader gone/extra 计数+样本≤5+size_drift_rows，输出 JSON `downstream_drift` 字段，placebo 同律）；④v1 清单恒等检验废除（其失败面与 mask 缺陷不可分=废门）。零跑纪律：本修正先于任何完整跑上链（崩#4 零产物、results 文件不在盘）；G-REPRO/判据其余面零触碰；selftest 双例律=今日生产失败模式入永久腿（下游漂移过门+泄漏/野面必炸，17/17）。
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

## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】（r80 bm-c 回填·首个完整跑 12:10:02→12:18:49 落地）

- G-REPRO（6 员）：**PASS 6/6**——逐位==T-14 冻结 A 面（钉面 `t14_anchor_face.json` 源 commit 4a5754a3；r78 钉面后漂移归零：C01 IS 0.4514/OOS 1.6085、C02 0.4585/1.4853、ENGULF 0.6239/0.2944 全对）。
- G-SET（处置 8 族/placebo 抽样）：**G-SET v2 PASS**——硬门 A 族窗抑制精确（反事实零笔派生入场落于任一处置/抽样族窗）＋硬门 B mask 面纯度（buy=False 面==族窗并集）；闭包面=actual 3（CE-01/CE-02/DROUGHT 各一）＋placebo 150（K=50×3 受染员）全部精确；下游 identity 漂移=披露面（CE-01 gone38/extra46、CE-02 gone96/extra103、DROUGHT gone2/extra2、size_drift_rows 逐员在件）非门输入——v1.1 修正生效、崩#4 形态未复现=门改对了。
- ΔSharpe/Δ年化 per trader（IS/OOS）：**CE-01 +0.3050/+0.6243**（Δ年化 +1.23pp/+1.81pp）；**CE-02 +0.3115/+0.1628**（+2.41pp/−0.33pp）；**DROUGHT +0.5767/−0.0001**（+0.98pp/−0.18pp）；零暴露三员（ENGULF/NEEDLE/VOLATILITY）=结构性零 delta（families_disposed=0）。
- null 带与分位：CE-01 IS p100 带外/OOS p100 带外；CE-02 IS p100 带外/OOS p100 带外；DROUGHT IS p100 带外/**OOS p18 带内**（μ=+0.0024 σ=0.0342——单族员 OOS 段零处置行=近零暴露效应）；placebo |Δ| 数量级（σ 0.0137-0.0545）≪实测 |Δ|（0.16-0.62）与 (c) 先验吻合。
- 行级归因（10 行）：d0 跳空成分绝对主导——CE-02 512100 三分批腿 d0_gap +44,373/+88,746/+66,560 元（raw_d0 +176.27%）vs 官方真收益成分 −27/−54/−41 元；损失腿 d0_gap：513100 −97,027／513500 −93,642（CE-01）·−58,502（CE-02）／512480 −45,641／512800 −66,575（CE-01）·−29,024（CE-02）／510500 −14,739（marginal 级）；reconciliation_ratio_space 全行 ≤0.027（残差=真收益+比例舍入，stage-2b 律）。
- 预测对账 (a)-(e)：**(a) 部分证伪**——CE-02 IS 年化预测「显著下移」、实测 **+2.41pp 上移**（−80%/−49% IS 幻影损失在复合路径上的拖累＞+176% 横财贡献：路径依赖重模拟非行删，方向由复合路径净效应决定）；OOS sharpe 方向对、OOS 年化异向（−0.33pp·(e) 覆盖）；**(b) 全对**——CE-01 IS/OOS 上移、DROUGHT IS 上移（幅度超「小幅」预期）；**(c) 全对**；(d) CE-02 带外对、DROUGHT 边际对（IS 带外/OOS 带内）、**CE-01 证伪**（预测带内~边际、实测双窗 p100 带外）；**(e) 实证**——CE-02 OOS sharpe↑年化↓异向、DROUGHT OOS 同构。两处方向证伪如实记档，零翻案面。

## §8 批后复盘【r80 bm-c 回填】

- 预测对账：(a) CE-02 IS 年化方向、(d) CE-01 带位两处证伪（见 §7 末行）；(b)(c)(e) 全对。跑前写死律保持——证伪只记档不改判。
- gate_attrition.json 追加一行：T19_PHANTOM_P1 measurement 行（cells_ledger_delta=0·ledger_total_after=286541 不变）r80 落（entries 58→59）。
- 轮报告回执：r80 bm-c（本轮）。
- CODELY.md 行级追加：本批唯一新坑律=r79 G-SET v2 恒等门面（已入册·本轮回填 commit）；收割面=既有律执行（记忆入口四问门过滤·零新增 append）。
- 工程重跑留痕（skill 正典「确定性引擎产物写 bug 的合法重执行≠结果重跑」）：崩 #1-#4 全部先于首个完整跑（12:10:02 发射→12:18:49 落地=唯一完整跑）——零跑纪律全程保持（每次修复先上链再重跑：e21bc4f6 修正先于完整跑）；12:30:13 tick 重复发射（pid 22408·pool flip 前盲窗）按 r312 keep-last 收敛·确定性产物字节恒等·零数据损。
- **GM 裁决（O-1325 选项 a/b·O-1620 P1 自决面·本票 bm-c 循环车道署名）**：①选项 a **维持**=评估/纸盘默认消费面（stage-2c 证据=幻影失真实质且 5/6 窗超族剔除噪声 p100，守卫剔除后风险调整指标 5/6 窗改善）；②选项 b=**清洁重跑资产面维持**（O-1612 深轴消费）·默认评估面不切双面板（双口径治理成本无证据支撑）；③stage-2a paper 前向保护件 HOLD 维持（T-20 接力时序不变）；④裁决面+证据入 research/CONSOLIDATION_GOVERNANCE.md，GM 会话一句话可翻面（保留面）。
