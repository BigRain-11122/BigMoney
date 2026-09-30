# REEVAL18_DRILL_P1 · REEVAL-18 花名册 18 员 2026 YTD 演习重放批（预注册）

> 【状态：FROZEN——跑前 commit 冻结】T-126 s1 承接票面 spec 冻结本文。跑后只许回填 §7/§8，禁改判据禁重跑（工程修复重跑须双跑留痕）。

## §0 批件身份【必填·跑前】

- 批号：REEVAL18_DRILL_P1；载体票 T-2026-09-30-126（bm-a 认领）；令源=O-20260930-1058（筛选标准改革）+ O-20260930-1101（宽进演习窗）合并产品线的循环侧执行面（T-126 spec 原文为正典）。
- 部门归属：dept:研究（REEVAL 档存重估线·CEO 令改革正典消费面）。
- 批型：**重估演习批（re-evaluation drill）非新生成批**——重放既有已判决 18 员（W1/W2/W3/W5 已判面板 g1_pass(技能线 v2) 通过员·花名册=档案权威），零新候选生成、零 Sobol 抽取、账本零 append（D-20260930-41 §四闸 306/500 不动：重放面 +0 生成试验·如实披露）。
- RW-5 面合规声明：RW-1~4 全绿解冻锚=bm-a r476 15:0x（MSG-20260930-1525 双机印证）后本件=解冻窗内首个新入库 prereg（解冻前唯一先例= r493 G2_OVERLAP_CENSUS_P1 在飞收口面）；本批无新供给线（18 员全部在库已判决）、无新 SLOT（top-N 上岗=既有纸盘泊位机制·s4 另片执行）。
- evidence_cutoff（前向锁盒 D2）=**2026-09-22**（EVIDENCE_CUTOFF_GRID 冻结值·sec.9.3 绑定——「→ evidence_cutoff」票面语的正典读法=仓冻结证据界，非「今日」；面板字节与判决面恒等=花名册可比性+锚门 verbatim 的构造前提）。结果 JSON 顶层必带 `science_gates.cutoff_meta(cutoff)` 字段。
- 引擎与退出规则：verbatim import（engine/exit_rules 零触碰；D-38 CN-A 一字板禁成交计数器随引擎现状携带披露）；T+1/真实成本双列（x1 基线 + x2=CostPatch(2)）。
- 演习窗：**2026-01-01 后首个面板交易日 → 2026-09-22**（窗长约 8.5 个月·YTD 面；窗短于 12m ⇒ beat12m 子面全批缺失=science_gates 现权重逐维 renorm 正常路径·如实披露）。

## §0.5 禁开方向硬闸【必填·跑前·D-20260930-41 §1.2】

- 本批重放对象全部来自已判决面板（W1/W2/W3/W5 prereg 各自过闸在案）；重放不豁免任何后续闸——s4 上岗执行面逐员再过禁开方向闸（届时另按正典）。
- 命中已证伪九方向检查：重估批无新方向主张；18 员家族 A/B 已判决（verdict 引用各自 wave prereg）。命中 BAN-__：无。

## §1 α 机制段【必填·D6——无机制段=批不受理】

- 四选一：**不适用声明**——本批=既有已判决候选的档存重估（「档存重估=新程序非翻案」票面原文），α 机制段由各员原 wave prereg 承载（W1: research/TRIAL_LABOR_W1_PREREG.md；W2/W3/W5 同族路径），本批引用不重述。改革判据的机制角色=**O-1058 四维合成 + 批内 FDR 替代全局账本折减**（科学面改革本体），非新 α 主张。

## §2 数据与面板【必填·跑前探针事实，非结果】

- 花名册：`results/reeval18/ROSTER.json`（s0 产物·r470 bm-a·sha16 `7c5ac06b3a243450`·18/18 join_ok·机械 max DSR=0.462294 vs 令面 0.80 差异已 s0 披露=档案权威）。跑前门：文件在位 + sha16 恒等 + 18 行 + 逐行 wave∈{w1,w2,w3,w5}。
- 面板：core48（`live.paper.load_core`→`build_panels`）截 2026-09-22；G-PANEL 门=48/48 员在位、≥60 行、末行==cutoff、OHLCV 齐（W1 caliber verbatim）。
- 锚门：G-ANCHOR=注册六员经 grammar default-axis 通道重放 vs live anchor（`anchor_gate`）逐员 ok 且 grammar-face 忠实（W1 cmd_screen_prep caliber verbatim）——引擎漂移 tripwire。
- 语法面：`results/trial_labor_w1/w1_grammar.json` faces 表（三模块族 volatility.low_vol_long / composite_rotation.top_n_rotation / patterns.box_breakout 全覆盖断言）。
- 波分派：w1→tl1.run_candidate_curve（4 元组轴）；w2→tl2.run_candidate_curve_w2（5 元组·STOP 轴）；w3→tl3.run_candidate_curve_w3（6 元组·GATE 轴）；w5→tl5.run_candidate_curve_w5（8 元组·GATE/VOL/YANG 轴）——全部 verbatim import 禁重写；各波 parity 法=selftest 面既有断言维持。
- 政体面：段面=`live.paper.v3_state_series()`（四级日态·REGIME_MAP 三代理 GREEN→bull/YELLOW→chop/ORANGE+RED→bear·T-22 sec.3 冻结）；当前态锚=`results/regime_state.json` state 键（REGIME_GUARD v1.0 shadow 探针在役面·finalize 时实读并落 asof 戳）。
- 五员 EW 基线（O-1126 已批准）：O-1555 冻结宇宙 {sh510300, sh510050, sh510500, sh512100, sh588000}，`passive_rel`（EW buy&hold·等现入场）同窗口径——与全批判 passive 单一口径。
- 零网络：本批零数据采集（面板全在库）；v3_state_series 每次调用活重放（无缓存无第二态存·G2 位一致性由其构造保证）。

## §3 方法学【必填】

- 演习语义：每员在全史面板重放（与判决面同引擎同面板），**记分面=演习窗切片**；窗前曲线=暖机段（如实披露；与原判决读数的 qfq 改史漂移=窗前段可能非逐字节等于原判决曲线——记分窗内读数为演习权威，诚实标签携带）。
- 双成本列：x1 基线 + x2=CostPatch(2)（逐员双跑·W2 judge caliber verbatim）。
- REGIME_GUARD 仓帽照用（披露面）：当前态钉帽——cap = 冻结梯 {GREEN:0.80, YELLOW:0.65, ORANGE:0.50, RED:0.20}[当前 regime_state.state]（GREEN×HOT95 升档属活盘应用面=演习域外·披露）；帽后日收益 r_cap[t]=cap×r[t]，帽后年化/Sharpe 逐员披露列（**不进合成记分**——合成子面集=science_gates 冻结子面集，禁增禁手抄）。
- 子面（窗面·L=core48 腿）→ science_gates 冻结维度映射：
  - ret.sharpe_full_L=窗 Sharpe（年化·引擎约定）；ret.annualized_ret_L=窗年化；ret.return_ceiling_O1126=窗年化−五员 EW 窗年化；ret.beat6m_rate_L=窗内滚动 6m 起点胜被动率（passive_rel 口径·起点 p∈窗且 p+W6−1≤窗末）；ret.beat12m_rate_L=窗内容纳不下 12m 窗⇒全批缺失（renorm·§0 已披露）。
  - robust.cost_x2_sharpe_L=x2 曲线窗 Sharpe；robust.regime_min_sharpe_L=min(bull/chop/bear 三段窗 Sharpe·段<20 窗日⇒该段 None 缺席 renorm)；robust.bootstrap_ci_low_L=`bootstrap_ci_sharpe(窗日收益, seed=20260923)`（判决面 CI 种子族·frozen）。
  - anti_overfit.family_pbo=花名册逐行携带值 verbatim（判决档案权威·18 重放曲线不可再导 CSCV·引用非重算）；anti_overfit.d6_max_abs_corr=窗日收益 vs 注册六员窗日收益 max|corr|（六员= drill 面板 DEFAULT_AXIS+模板重放·`_d6_admit_core` verbatim 复用·D6_CEILING≥0.7 拒）。
  - anti_luck.batch_dsr=`deflated_sharpe_ratio(窗日收益, n_trials=18)`（批内 n_trials=批容量·O-1058 改革口径·非全局账本）。
- 批内 FDR：p 值=单侧 1−Φ(t)，t=`t_from_sharpe(窗 Sharpe, 窗期数)`（D-37 M1 t 面采纳）；`bh_batch_fdr(p, q=REFORM_Q_LEVEL=0.10)`。
- 合成与 L3 门：`g2_reform_fdr4d(member_metrics, REFORM_DIM_WEIGHTS, REFORM_SUB_WEIGHTS, batch_p_values)`——权重/子权/q/topN 全部 science_gates 冻结常数 import（禁手抄判线）；eligible_reform = fdr_pass ∧ 合成完备 ∧ D6 admitted。
- 两段排序（票面「2026 YTD drill 成绩 x 现风格适配度」的冻结实现）：
  - 第一段=composite（g2_reform_fdr4d 输出）批内 midrank 百分位 composite_pct；
  - 第二段=现风格适配度——当前态 regime_state.state 实读钉段（REGIME_MAP：GREEN→bull/YELLOW→chop/ORANGE|RED→bear），该段窗 Sharpe 的批内 midrank 百分位 fit_pct；
  - **final_score = 0.70×composite_pct + 0.30×fit_pct**（两段权重冻结于本件；现风格=第二段唯一依据·态切映射 verbatim）。
  - 上岗名单=eligible_reform 按 final_score 降序、每波 top-N=REFORM_TOPN_PER_WAVE(3) 封顶（宽进不滥进·前向月考=真终门不变）。
- s4 上岗与 48h CEO 报告=另片执行（burn+记分后：docs/trial_labor/CEO-REPORT-REEVAL18-<date>.md 纸面+名单呈报；上岗=既有纸盘泊位机制 TRIAL-R18-<NN> 观察账户·初始 ¥1,000,000·marks 范式·非试验账本 +0）。
- 确定性与血统：r446 三命令真数据恒等律——prep 产物 sha16 记入 manifest；run checkpoint 逐员 append；finalize 必带双跑恒等门（run 重放哈希对账·漂移=exit 2 如实上报）。全批 L1 确定性零网络零随机自由度（bootstrap/D6/t 面种子全冻结）。

## §4 判据【必填·跑前写死，禁看结果调线】

- eligible_reform（L3 改革门）= fdr_pass(bh_q≤0.10) ∧ composite 完备（四维无缺失）∧ D6 admitted（vs 注册六员 max|corr|<0.7 且批内簇去重幸存）。
- 上岗名单资格=eligible_reform ∧ final_score 降序 ∧ 每波 ≤3 员。
- 硬披露门（非淘汰线·逐员必带）：帽后年化、x2 窗 Sharpe、D-38 一字板禁成交计数、窗内交易数<10 员=「样本不足」标签携带禁静默。
- 全员判负=合法产出（O-1820 三验③：重估面如实档案化，禁为满载改判线）。

## §5 跑前预测【必填·写死于跑前，跑后对账】

- P1：18 员中 fdr_pass 数 ∈[0,12]（0=合法·窗短 t 面保守）。
- P2：D6 注册撞线拒收数 ∈[0,10]（低波族与 VOLATILITY-CE-01 同源面客观存在撞线可能）。
- P3：eligible_reform 数 ∈[0,10]。
- P4：上岗名单规模 ∈[0,10]（每波≤3 封顶·四波合计理论最大 10）。
- 极端日先验：演习窗内 510300 无单日≤−5%（panic 级）日（跑前探针事实·窗内已知行情为温和回升+9 月末回落段）；若窗内实际出现极端日→如实入 §7 对账。

## §6 产物

- runner：`scripts/reeval18_drill.py`（prep / run / finalize / selftest / status；exit 0=正常、1=门败 VOID 零产物、2=机制故障如实上报勿掩盖）。
- 产物：`results/reeval18/drill_manifest.json`（prep 门+窗定义+帽锚 asof）；`results/reeval18/checkpoint_drill.jsonl`（逐员 append·kill-safe）；`results/reeval18/DRILL-<cutoff>.json`（顶层 evidence_cutoff+cutoff_meta·18 员子面/披露列/门态/两段排序/上岗名单）。
- 入池：run 烧批按 O-2100 长 309 活纪律入 `results/runnable_pool.json`（workers_plan 必带·BelowNormal·CPU 余量律 O-20260929-10:29）。

## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】

（空）

## §8 批后复盘【必填·s7-T】

（空）
