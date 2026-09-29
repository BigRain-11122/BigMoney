# GATE-TIMING-PRESCREEN-A158 预注册 —— 17 入册门×五员择时用法廉价初筛（r433 模板逐字应用）

> 【状态：FROZEN——跑前 commit 冻结】本件=「门验证 PASS→策略臂」升格链的 r433 同门换用法反向证伪律必经关：任何门候选升格策略臂前必先跑择时用法廉价初筛（scripts/t101_v4_a2_prescreen.py 模板：T+1 开盘代理+0.1% 往返+IS/OOS+同掩码循环位移 null）。跑前冻结于烧批前；跑后只许回填 §7/§8，禁改判据禁重跑（工程修复重跑须双跑留痕）。

## §0 批件身份【必填·跑前】

- 批名 / 批号：**GATE-TIMING-PRESCREEN-A158**·批内格数=**85 cells**（17 门×5 员·每格一判 SURVIVE/KILL+D6 REJECT 面；本批=测量面非注册面，不入 trials_ledger，marks +0·SEED +0——census/verify 先例：TSGATE-P1/GATE-RECHECK-A158 同族）。
- 认领：F-04 先行已落——fleet/inbox/MSG-20260929-1800-bm-c-ALL-gate-timing-prescreen-a158-claim.md（fetch 前置双检：origin/main==07bbfdd6e·inbox 零未读·零对手声明）；任务板=本机 job #1（GATE-RECHECK-A158 让路后改道件）。
- 部门归属：dept:研究（策略研究面·T-101 v4 政体门臂供给链）。
- 算力预算：est 1-3 min（85 cells×K=200 nulls≈17,000 次 daily_returns 直积+5 面板因子计算）·trivial compute in-round 合法（O-2100·bm-a r439 GATE-RECHECK-A158 同窗先例）；worker 数=1（单进程直积，无并行需求）；批报告必带 audit 段。

## §1 α 机制段【必填·D6】

四选一：**[x] 风险溢价**——17 门全族=「因子自身极端态」（超卖/高波动/趋势结构极端）入场连续持有择时：持有人在不适状态（高波动/深回撤/趋势衰竭）承担持有不适风险，补偿由后期状态回归支付，代价付出方=状态极端期被迫减仓的风控盘与恐慌盘（TSGATE 20d 前向正信号=同一溢价的前向持有读数；本面换用连续择时用法重测）。

**同族相关性准入检查【D6】**：
- vs 在册交易员：in-roster 六员纸盘日收益序列在 paper_export 仅指标面无日序列——**defer**（r433 模板先例逐字：in_roster_daily_series=unavailable_in_paper_export_deferred_to_full_judge_per_prereg_sec1）。
- 绑定判面①（kill 面）：策略日收益 vs 五员各自 B&H 日收益逐对 max|corr|（pairwise intersection 口径·pit-115 律禁五员 inner-join）≥0.7 → **REJECT（beta 同源族预声明处理·r433 定谳：510050|RSV30 0.9424=全仓门控择时与标的 B&H 结构性同源）**。
- 披露面②（非 kill）：17 门×17 门批内策略日收益互相关矩阵逐员全量落 JSON+每门批内 max|corr|——喂 v4 臂设计的冗余处置面（本批零臂设计零组合宣称·冗余裁决权归 v4 prereg 起草轮，初筛不越权 kill 批内同族）。

## §2 数据与面板【必填·跑前探针事实】

- 宇宙：五员冻结宇宙 O-1555 = {510300, 510050, 510500, 512100, 588000}（错期上市如实：510050 2005-02-23 起 / 510300 2012-05-28 起 / 510500 2013-03-15 起 / 512100 2016-11-04 起 / 588000 2020-11-16 起——pit-115 律：本批逐员独立计算零跨员矩阵，OOS 2017-01-01 起各员可判天数不同为冻结宇宙实况，逐 cell 披露 oos_n/is_n）。
- **数据锚面定义四元组（G-ANCHOR-FACE 律·每个锚）**：五员面板锚=`data/daily/sh<code>.csv` + `pd.read_csv` raw 直读截断（非引擎池面）+ 全史起算（各行首日期如上）+ 门预热窗 rolling(252, min_periods=120)→首可判 bar=第 120 行（0 基）。探针-锚同面断言：runner 实载路径与锚声明路径逐位比对，一面不符=面错配 VOID（fail-closed 拒烧报「面错配」非「数据腐坏」）。
- **冻结行数锚（截断 @2026-09-28 实测·r231 bm-c 探针）**：510300 rows=**3486**（2012-05-28→2026-09-28）/ 510050 rows=**5251** / 510500 rows=**3289** / 512100 rows=**2405** / 588000 rows=**1425**；五员截断尾行一律=**2026-09-28**（runner G-ANCHOR 逐位断言）。
- **evidence_cutoff（前向锁盒 D2）=2026-09-28**：面板截断到 2026-09-28（五员 ETF 面最新完整 bar 日·r433 模板 latest-bar 惯例同面；A158 族 P-5C=2026-09-22 绑定面止于 TSGATE-P1/GATE-RECHECK-A158 因子普查/复核两批已收口面，本批=新择时用法面随模板惯例取最新完整 bar·+3 交易日如实披露）；cutoff 后新 bar 不回流本批；结果 JSON 顶层必带 `science_gates.cutoff_meta(cutoff)`。
- **G-P1 门（fail-closed）**：results/gate_recheck_a158.json 实读 library_entries==本件 §3 冻结 17 门表逐位一致·且 17 门全部 ⊆ results/a158_tsgate_p1.json PASS 48 集——任一不符=exit 2 拒烧。
- **G-FACTORS 门（fail-closed）**：`a158_tsgate_probe.alpha158_factors` import 单源复用（禁重实现），断言 N_FACTORS=157 且 17 门名全在 `gate_universe(F)` 产出集中。

## §3 方法学【必填】

- 因子/信号定义（冻结参数）：Alpha158 157 因子 qlib-verbatim pandas port（`scripts/a158_tsgate_probe.py::alpha158_factors` import 单源）；门构造逐字=`f < f.rolling(252, min_periods=120).quantile(0.1)`（_q10 侧）/ `f > f.rolling(252, min_periods=120).quantile(0.9)`（_q90 侧）——TSGATE-P1 冻结门构造零改动。
- **冻结 17 门表**（源=results/gate_recheck_a158.json::library_entries·bm-a r439 07bbfdd6e RECHECK-CONFIRM 17 门）：`CNTD5_q90, CNTN20_q10, MAX30_q10, RANK30_q90, RESI60_q90, RSQR10_q90, RSQR20_q90, RSQR5_q90, STD10_q90, STD20_q90, SUMD30_q90, SUMD5_q90, SUMN10_q10, SUMN20_q10, VSUMD10_q90, VSUMD20_q90, VSUMD30_q90`（runner 逐位重derive并对账冻结表）。
- 择时用法（r433 模板逐字）：gate open→持仓/gate closed→现金腿 0%；执行=T+1 开盘代理（O-1132 保守口径·position=mask.shift(1)）；成本=0.05%/腿（开/平各计·往返 0.1%·gate_verify cost_rt 同面）；IS≤2016-12-31/OOS≥2017-01-01 分界（模板 SPLIT 逐字）。
- null 对照：**K=200/ cell 同掩码循环位移 null**（shift k∈[1,n-1] 均匀抽·掩码循环位移重摆·同成本同执行重算 Sharpe）；seed 基=`science_gates.SEED_REGISTRY["gate_timing_prescreen_a158_scrnull"]`=**20312500**（本批新登记·20311000-20312000=W10 目录预留块未动·rng 基每 cell 重init=模板逐字语义）；被动基线=B&H 五员（oos_excess_vs_bh 主判列）。
- 分段面（描述性）：bear/bull/chop 三段（510300 MA200+slope60 判据·模板 regime_segment 逐字）OOS 逐段年化披露（≥30 日段才计）。
- 账本：**非试验账本批零 append**（census/verify 先例·E[FP] 披露面见 §4）；判据节禁手抄判线——本批无注册面，v4 锦标赛注册面归 `science_gates.g1_prime_v2/g2_registration_v2` 共享库（§4 指针）。

## §4 判据【必填·跑前写死，禁看结果调线】

- **r433 模板冻结 4 判据逐字**（SURVIVE 需全部满足，任一不满足=KILL+逐条 fail_reasons）：
  1. `oos_excess_vs_bh > 0`（OOS 年化超额 vs 同员 B&H OOS 年化）；
  2. `oos_entries >= 15`（gate_verify min_ev_per_split 同面·不足=判负非弃权）；
  3. `full_maxdd >= -0.35`（全期 maxdd 地板·BACKTEST_SCIENCE 描述条款模板逐字）；
  4. `oos_sharpe > null_med_sharpe`（同掩码循环位移 null 中位数·K=200）。
- **D6 判（独立于 4 判据的 REJECT 面）**：cell 策略日收益 vs 五员 B&H 逐对 max|corr| ≥ 0.7 → **D6-REJECT（beta 同源族预声明·r433 0.9424 判例）**——SURVIVE∧D6-ACCEPT 才得「择时用法候选资格」入消费面；SURVIVE∧D6-REJECT=如实双标（生存但同源·v4 设计轮自裁）。
- **多重检验披露（诚实面）**：85 cells·null_med 单判据 α≈0.5/cell（中位比较·模板逐字）单判据 E[FP]≈42.5 上探——四判据合取实质压低+D6 独立砍半；**本批=廉价初筛非注册**，多重校正主责归 v4 锦标赛注册面（g1_prime_v2 skill_line_v2 按 N_eff 数据驱动校正+g2_registration_v2 DSR≥0.95+PBO≤0.25——共享库调用禁手抄）；初筛权衡=接受假阳性后遗（后续更严门杀）换取廉价杀伪。
- 判负处置预案（O-1820 三验③）：KILL/D6-REJECT 门=C1 输入特征面注记（不废输入特征资格——GATE-RECHECK-A158 L17 邻接披露·择时判负不借判候选资格面）；全 85 格判负=「17 门择时用法全关线」合法产出（v4 臂设计转纯输入特征组合路线·关线即结论）。

## §5 跑前预测【必填·写死于跑前，跑后对账】

1. **SURVIVE 率 ≤25%**（≤21/85 cells）：r433 RSV 族 1/10 存活+GATE-RECHECK 27 代表 10/27 RECHECK-FAIL（37% 前向面判负）+择时用法=r433 实证的更苛面（9/10 判负）。
2. **SURVIVE 者中 D6-REJECT ≥50%**：全仓门控择时与 B&H 结构性 beta 同源（r433 唯一存活 0.9424 判例）；预期最终「SURVIVE∧D6-ACCEPT」≤10 cells。
3. **批内互相关披露面**：同族对（SUMD5/SUMD30·VSUMD 三窗·STD10/STD20·RSQR 三窗·SUMN 两窗）策略日收益 |corr|>0.7 于多数员成立（簇坍缩择时面复现预期）。
4. **极端日先验（硬界设计三件套 (c)）**：2020-02-03 COVID 跳空（五员单日 −7%~-8%）·512100 2024-02 微盘股灾窗与 2024-09-24+ 爆发反弹窗（单日 ±10% 级）·588000 2021-2024 科技熊段——vol 族门（STD/RSQR/VSUMD）在这些窗成簇 open；512100/588000 深熊段全持有类门 maxdd 击穿 −35% 地板预期复现（r433 接刀亏损判例）；nulls 掩码位移落入极端日=肥尾 null Sharpe 诚实如实。

## §6 产物

- script：`scripts/a158_gate_timing_prescreen.py`（import `scripts/t101_v4_a2_prescreen.py` 执行机器逐字复用零重实现+`scripts/a158_tsgate_probe.py` 因子/门单源；fail-closed G-P1/G-FACTORS/G-ANCHOR；hermetic selftest 子命令）。
- results：`results/gate_timing_prescreen_a158.json`（顶层 evidence_cutoff+science_gates.cutoff_meta+audit 段+cells 85+d6 双面+verdict_counts）+ `results/gate_timing_prescreen_a158.csv`（行级）。
- 本件 §7/§8 回填+`results/gate_attrition.json` 追加一行（§8）。

## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】

（跑后回填：一次定稿；确定性引擎重跑字节恒等合法口径≠结果重跑。）

## §8 批后复盘【必填·s7-T】

（跑后回填：预测对账（对/部分/错）+门禁链损耗账 gate_attrition 行+E[FP] 实证读数+回执入轮报告。）
