# TRIAL_LABOR_W2_PREREG — T-96 千人试用期大考 wave-2 波级预注册（MASS CANDIDATE TRIAL PROGRAM 第二波·5000 人深化波）

> 模板=research/PREREG_TEMPLATE.md（§0-§8 全节）；跑前 commit 冻结；跑后只回填 §7/§8，禁改判据禁重跑。
> 令源：CEO 直令 O-2026-09-27-2245（「测试的时候，把cpu算力吃满，多用试用期的交易员，哪怕一千个？五千个？只要能扛得住。科学理性的去尝试」）+ O-2026-09-27-2250 常设律（firm/TRIAL_LABOR_LAW.md v1.0「以后不要我提醒」）+ T-20260928-96 波级 prereg 票（bm-b r356 认领，本冻结=r357 开动交付物；sequencing_gates：起草本体无门禁任意轮可开）。
> 统摄律：firm/RANDOM_LARGE_SAMPLE_LAW v1.0（判决面）+ firm/REFINE_BENCH_LAW v1.0（轴系）+ TRIAL_LABOR_LAW §1-§6 + research/BACKTEST_SCIENCE.md v2（判据唯一权威）+ BACKTEST_PLAN.md 三铁律 + COMPUTE_AUDIT.md 批件纪律。
> **本件=波级（wave-level）预注册**：生成语法+漏斗规则+判据全冻结；sub-wave 追加面一律走 §9 append-confirm（每 sub-wave 一冻），禁用本冻结面跑追加波。
> **本波与 W1 语法血统**：新增初始止损轴（§3 扩容面 a）+ Sobol 抽样升级 declare（扩容面 b）→ **新语法新 sha16**（≠W1 a2fa15f4b06b3c40 ≠MASS 96269ebe766c3fc2），同语法禁重跑律（TRIAL_LABOR_LAW §4）经新语法面合法开波。

## §0 批件身份【跑前】

- 批名/批号：**TRIAL_LABOR_W2**（千人试用期大考 wave-2·5000 人深化波）。三层漏斗=批内分批入账（dict schema 唯一）：
  - **TRIAL_LAB_W2_SCREEN**（s2 初筛批）：batch_trials = 去重后候选数 + 200 null（每格 1 trial；raw 5,000 → 去重门后 ≤5,000 distinct——**5000=上限非凑数指标**，语义重复=无效人不计数·造数凑烧禁律）；
  - **TRIAL_LAB_W2_JUDGE**（s3 全量判决批）：batch_trials = 初筛存活者数（judged cells；双 nulls=B/P 重采样=derivation 面 ledger +0·census §9.2 NAV 推导面先例）；
  - 两批 evidence_cutoff 均=**2026-09-22**（P-5C 冻结栅格 binding·双轴同截·W1 §9.3 零跑修正案整体沿用——见 §2）。
- 认领：T-20260928-96 claimed bm-b r356（TRIAL_LABOR_LAW §1 常供律例行供给步，无需 GM 另署名）；F-04 先行=**MSG-20260928-0430-bmb-all-trial-labor-w2-prereg**（fleet/inbox/ 在制窗口声明·本冻结同窗）。
- 部门归属：dept:策略（生成引擎·供给面）+dept:研究（判决漏斗·判据面）joint（票面 note 同 W1）。
- 算力预算：生成+去重=轻（分钟级单机，76 函数值域表枚举+5,000 抽样）；初筛批≈5,200 格（≤5,000 候选+200 null）× 全史引擎回测——实测锚=~28s/候选单核（W1 O-2245 产力账），**估 12-20h @ ≤floor(核×0.8) workers 池批**（>5min 一律入 results/runnable_pool.json·O-2100 执行面分离；每 50 候选一 checkpoint 跨轮续跑·R41；CPU 排队=池优先序自主调度）；判决批=分钟级/格（双 nulls 向量化重采样）。批报告必带 audit 段（无 audit 段结果件不入账本）。
- **供给粒度如实披露**：A=在编六员工模板族 500 抽（常供律维持面）；B=流派战法模板族 4,500 抽 → **76 函数均摊 ≈59.2 抽/函数**（W1 为 ≈7 抽/71 函数·广度薄覆盖；W1 §0 预告「~70 抽/函数」按 B-only 5000 口径预估，本冻结=5000 上限含 A500 常供线后的实分账，如实入账不掩饰）；C=因子普查存活腿族 500 抽（when-ready·§9 禁跑面）。W1 JUDGE 存活变体供给面（TRIAL_LABOR_LAW §5）**declare 不可得**：W1 两判决批（TRIAL_LAB_W1_JUDGE+MASS_TRIAL_W1_JUDGE）于本冻结时点仍在池 waiting（RAM 序列化·r357 实况）→ **(d) 面如实降权为基线网格**（轴族均匀分配零 judged 加权，禁编造；后续波次待 W1 judged 落地后另 declare）。

## §1 α 机制段【四选一+论证·D6 门槛】

- **供给族 A（在编六员工模板精炼）**：[x] 风险溢价（主）+行为偏差（辅）——母员机制继承同 W1 §1（VOLATILITY-CE-01 低波风险溢价/COMPOSITE 低波+低振幅+动量复合溢价/ENGULF·NEEDLE·DROUGHT 确认构造行为反转）。本波主张=**母员 α 在 REFINE_BENCH 轴系+初始止损叠加层下可发现增益变体**；代价支付者与母员注册线同源。
- **供给族 B（流派战法模板大考）**：[x] 逐流派四选一映射同 W1 §1（11 流派·工厂批次血统；负先验标签如实随格携带、漏斗平等处置不预筛）。本波主张=**冻结工厂库在 Sobol 低差异抽样×轴系×初始止损面下存在仅大规模深化抽样可检出的 α 口袋**。
- **初始止损叠加层机制注记（本波新增面 a）**：初始止损=入场武装的价格保护叠加层（非引擎出场规则）——机制归属=**风险溢价面**（波动承担的截断：止损=将左尾波动风险让渡回市场，换取更高 Sharpe 形态的可能；代价=尾部让渡成本+whipsaw 摩擦）。pct 族=固定口径校准面，ATR20 族=波动自适应口径（per-function 适配由 ATR 归一承载）。
- **D6 同族相关性准入（W1 大考面适配声明整体沿用）**：批内候选两两 corr 矩阵全量计算（去重门副产品）；≥0.999 塌缩=生成段绑定门（§3）；0.7 线对在册六员=全候选计算+披露（逐格 max|corr| 列），绑定生效位=s4 intake（≥0.7 拒收·存活者簇内 ≥0.7 塌缩留最优）；批内 0.7-0.999 中带=锦标赛选择面，非准入门。
- 排除律（反 dredging·W1 同律）：**已判精确格（正负皆然）禁重跑**——cell key=(template, params, axis_config, initial_stop)：initial_stop=none 面上与在册判决产物全等（注册六员配置、34 判负函数默认参数原批、W1/MASS_TRIAL_W1 已判格=w1_screen.json 存活清单+w1_judge 产物+MASS judged 产物）→ 生成段排除并逐格留痕；**initial_stop≠none 面=新语法面合法格**（W1 全部已判格隐含 initial_stop=none）。本波=新 prereg+新语法（轴系×止损面×Sobol），符合 RANDOM_LARGE_SAMPLE_LAW §5 唯一合法重试通道。

## §2 数据与面板【跑前探针事实，非结果】

- 宇宙/池：**core48**（ETF 交易线正典域·在册六员注册域；loader=引擎 T-22/T-34 血统 import-face 复用禁重写）+ 判决段深轴=**T-18 增长成员面板**（Money02 t18_deep_panel cache 只读·WILD-S1/KLINE 只读先例禁写）。
- **evidence_cutoff=2026-09-22（P-5C 冻结栅格 binding·双轴同截）**：整体沿用 W1 §9.3 零跑修正案机械——**import `scripts/p5c_virtual_timepoint.py` 冻结栅格禁重实现**：初筛面=leg-L 6m 面 census 门==FROZEN_CENSUS["L"]["6m"]=**1,253**；判决面=双腿窗口 {6m,12m,24m} 全网格逐面==FROZEN_CENSUS 对应腿窗值（L 1253/1127/875·D 3104/2978/2726）；被动=模块 passive_rel/passive-cell 机械；leg-L 宇宙口径=模块 MIN_LISTED=24（census caliber never binds·模块原文注记）。G-ANCHOR 一致性：live.paper 锚定门常数 cutoff=2026-09-22 与本波 binding 同栅=锚门复放语义自洽。cutoff 后新 bar 锁定不得回流本批；结果 JSON 顶层必带 `science_gates.cutoff_meta("2026-09-22")`（缺字段=C2 VIOLATION）。
- 数据完备门（fail-closed，不过即 VOID 中止零产数）：
  - **G-PANEL**：core48 48/48 员·每员≥60 行·截断后末行日期==2026-09-22 逐员唯一·OHLCV 列齐；
  - **G-CENSUS**：P-5C FROZEN_CENSUS 逐面实读断言（L/D×{6m,12m,24m} 六值逐位；import 实读禁手抄）；
  - **G-ANCHOR**：在册六员注册配置经本波 grammar 引擎默认轴路径（template_default+EW+daily+initial_stop=none）重放，IS/OOS Sharpe==live.paper 锚定门常数（import 实读零手抄；不等=管线漂移 VOID）；
  - **G-MANIFEST**：深轴 manifest verdict==PASS（48-member twin cache 口径·W1 §9.3 manifest_note 先例：P-5C 冻结栅格仅在 48 员孪生 cache 上复现，member count 披露；**冻结时实读**——r357 实读=judge_state g_manifest PASS/48 员，跑时以活值为准）；
  - **G-EXCLUDE**：已判格排除清单装载（§1 排除律四源）+命中计数披露（排除>0 合法、排除=0 如实）。

## §3 方法学【冻结】

- **生成语法（全部冻结·零新信号发明——候选只从冻结规则原语组合生成）**：
  - 原语面=策略工厂 `strategies/` **86 函数/13 模块**（2026-09-28 r357 冻结时 import 实测计数；W1 时点 81/13）；族 A=在编六员工模板（low_vol_long/composite_top5/composite_top8/engulf_reversal/needle_probe/vol_drought_reversal）；族 B=其余工厂函数 **76**（86−6−4：grid 模块 4 业务函数排除——GRID 线专用判决线 GRID-SLEEVE-P1 机械不可由通用语法表达，W1 同律如实披露）；函数-参数空间=各函数签名参数+冻结值域（runner build 时逐函数枚举值域表随 w2_grammar.json 序列化冻结·W1 同款）。
  - 轴系（REFINE_BENCH_LAW §2 标准轴·离散网格+本波扩容面）：入场过滤 ∈ {none, depth_thresh, amplitude, liquidity, trend_slope, dual_window, fundamental_mask}（7·基本面闸=data/fundamental 掩码硬过滤·in-repo 确定性）× 出场 ∈ {template_default, CE 注册机, time_stop_5d/7d/10d/20d, trailing_stop, profit_ladder}（8·与 W1 同集）× 仓位 ∈ {equal_weight, inverse_vol, cap20, regime_delever}（4）× 时机 ∈ {daily_signal, weekly_grid}（2·T+1 开盘保守代理引擎原生 O-1132）× **初始止损叠加 ∈ {none, p3, p5, p8, p12, a15, a20, a25}（8·本波新增面 a）**——**3,584 轴组合/模板**（W1=448）。
  - **初始止损叠加层（扩容面 a·参数空间起草时定稿）**：入场日（T+1 开盘成交）武装，全程有效不重锚（区别于 trailing_stop 再锚面）；p3/p5/p8/p12=entry_open×(1−stop)（固定口径校准族）；a15/a20/a25=entry_open−mult×ATR20（ATR20=信号日 20 日平均真实波幅·波动自适应族，per-function 适配由 ATR 归一承载）；**多头面 stop=下方保护，空头暴露面（如个别 B 函数构造）对称镜像 entry_open×(1+offset)**；触发判定=日 low（镜像面 high）触价 → **次日开盘出场（T+1 保守·禁日内成交未来视）**；优先级=**止损保护优先于同日出场引擎信号**（物理正确性：价格击穿保护先于一切待定信号；engine/exit_rules.py 退出优先级铁律零触碰——本层=grammar 叠加面非引擎面）；initial_stop=none=W1 语义基线面。
  - 随机抽样（**扩容面 b·Sobol 升级 declare**）：**Sobol 低差异抽样**（TRIAL_LABOR_LAW/W1 声明「Sobol=wave-2 可选升级另declare」→ 本波 declare=Sobol，弃均匀腿）：**import-face 复用 MASS_TRIAL_W1 sample_draws 范式禁重写**——`scipy.stats.qmc.Sobol(参数维, scramble=True, seed=SEED_BASE+family_idx)` 归一化参数盒低差异 draw+轴组合独立 RNG 流（`default_rng([SEED_BASE+family_idx, 7919])` 整数轴抽）+**本波新增初始止损轴并入轴抽流**（五元组 R/X/S/T/STOP）；N=500/族 A（6 模板轮转确定性指派）+4,500/族 B（76 函数轮转）；**seed 基=`trial_labor_w2_gen`=20285500**（派生=Sobol seed 20285500+family_idx，A 族 idx 0-5·B 族 idx 6-81；轴 RNG 流=[20285500+family_idx, 7919]；零 band 占用·重跑字节恒等；SEED_REGISTRY 本冻结 commit 同步登记·R250 一步律）。
  - **去重门（T-84 s3 组合恒等坍缩律·强制·W1 同律）**：①持仓恒等指纹=sha256(逐再平衡日 sorted((sym, round(w,4)))) 全等→塌缩；②候选日收益序列两两 |corr|≥0.999→塌缩为一格（保留代表=确定性最低 candidate_id·原始变体入 audit 段全量保留）；**塌缩计数+保留/淘汰清单如实披露**；判读与账本按坍缩后格数记。
- **s2 初筛（廉价面先行·TRIAL_LABOR_LAW §2）**：每 distinct 候选=legacy 轴 leg-L 6m 全史一回测（V1 13bp base 面·T+1·初始止损面随格携带）→ beat6m=1,253 虚拟起点中「候选 6m 前向收益≥同窗被动」比例（完整窗子集·partial 窗计数如实披露）。
  - **初筛 null 族**：K=200 同结构随机信号候选（模板腿替换为随机信号日生成器·轴腿+止损腿同网格同参数空间 draw·同引擎同成本同面板——BACKTEST_PLAN 三铁律）；**seed=`trial_labor_w2_scrnull`=20286000**（派生 `[20286000, i]`·同 commit 登记）。
  - **初筛判线（跑前写死）**：**存活 iff beat6m > null 族 p95**（程序冻结·零手挑阈值·数据自适应刻度）；二项参照（p=0.5·n=1,253）z/p 值逐格披露列。初筛=漏斗阶段非判决（零注册效力，存活者仅获判决面入场券）。
- **s3 全量判决（存活者·TRIAL_LABOR_LAW §2/§3）**：双轴（P-5C 栅格 L/D×{6m,12m,24m} 起点）× 成本面 {base x1, x2=CostPatch(2.0)（t22 Erratum-1 multiplier 律·禁直引 COST_X2_RATE）} × 政体分段 bear/bull/chop+na（T-22 §3 冻结 3-way proxy 逐字）× **双 nulls**（RANDOM_LARGE_SAMPLE_LAW §3）：block bootstrap **B=2000**（block=20 交易日循环块·拼样截回 n 长）+ sign-flip 置换 **P=2000**（逐日符号独立翻转·双侧）；**seed=`trial_labor_w2_unc`=20286500**（派生 `[20286500, cell_idx]`·同 commit 登记）；rng 流仅限两重采样面禁挪用（census §9.1 用途钉死先例）。
  - **样本充足律**：n_eff≥500 起点 ∧ bear/bull/chop 三段各 ≥100 起点窗（na 桶披露）——不足→verdict=**insufficient-sample 禁算 pass**。
  - 描述条款（批级披露·不替代 v2 门）：年化>0·OOS(2025+ 恒盲)双正·回撤≥−35%·无崩年·x2 面逐年稳定。
- **成本口径**：V1 legacy 引擎面（13bp·T+1·退出优先级冻结禁改）+x2 压测面——与在册锚定/注册判读血统同源可比（注册面一致性优先）。
- **账本**：`science_gates.append_ledger("TRIAL_LAB_W2_SCREEN", <distinct 候选+200>, file, evidence_cutoff="2026-09-22")` + `science_gates.append_ledger("TRIAL_LAB_W2_JUDGE", <存活者数>, file, evidence_cutoff="2026-09-22")`（prev=数据驱动链头实读禁手抄）。

## §4 判据【跑前写死·禁看结果调线·共享库引用零手抄】

- **G1' v2 = `science_gates.g1_prime_v2(sharpe_full, returns, batch_cells, pool="core48", n_trades, n_entries)`**：全期 Sharpe>skill_line_v2（数据驱动=max(被动+0.10, μ_null+σ_null·√(2·ln N_eff))·N_eff=活链头+本批格）**且**平稳 bootstrap CI 下界>0 **且** entries≥30（F6 双口径 entries_ok 为准）；批报告逐列披露 skill_line/bootstrap_ci/trade_gate 全输入。
- **G2 注册资格 v2 = `science_gates.g2_registration_v2(g1_pass, dsr, pbo)`**：G1' 过线 **且** DSR≥0.95（`deflated_sharpe_ratio` 原始收益跑；**n_trials=累计账本总试验数**（活链头实读·**跨波不重置**·TRIAL_LABOR_LAW §4——r357 冻结时实读=**294,304**（含 W2A census 5,920；跑时以活值为准）+本波 SCREEN 格并入后折减）·禁 dsr_from_stats 充数）**且** 家族 PBO≤0.25（`screening/pbo.py` CSCV 8 块·**家族=策略模块**（12 非 grid 模块·族内全部波内候选 base 面 Sharpe 向量=同族竞争网格 g25_retro 先例；<8 格族=insufficient 如实 n/a→G2 不可过））；缺输入=诚实拒收（missing_inputs 机制）。
- **波级多重检验披露（O-2245 强制·护栏随 N 加码）**：①N_wave=SCREEN 格+JUDGE 格逐批披露；②**E[FP]=0.05×N_wave_judged_cells** 如实披露（DSR≥0.95 门即多重检验校正门，通过者=校正后存活非名义面）；③波级 PBO 聚合读数另列（跨族）；④语法消耗登记簿（research/TRIAL_GRAMMAR_LEDGER.md·append-only）落 wave-2 行（grammar sha16+w2_grammar.json 序列化时点+raw/dedup 计数+seeds+consumed 时点）——**同语法禁重跑**（防疏浚·TRIAL_LABOR_LAW §4）。
- **s4 intake（上岗线·O-2245 三.3）**：G2 eligible 存活者 → **D6 绑定门**（对在册六员+存活者两两 max|corr|·日收益口径·sleeve-tag 先例；≥0.7 拒收·存活者簇内塌缩留 DSR 最高者（平手=最低 candidate_id））→ STRATEGY_LIBRARY 注册行（带 evidence_cutoff+SIGNAL_BUILDERS 接线+smoke 锚定门复跑·模板 §8 律）+ **TRIAL-<FAMILY>-<NN> 纸盘上岗**（O-2045 PROSPECT 机器复用·观察车道）+ **48h 内 CEO 呈报**。**实际存活数按实际判（5000 底盘预计数十至上百·零存活=合法判读照报不翻案）**。

## §5 跑前预测【写死于跑前·≥3 条·含极端日先验】

1. **去重率**：raw 5,000 → distinct ∈ [3,600, 5,000]；Sobol 低差异+scramble → 精确重复抽≈0（sha256 恒等腿预期≈0）；corr≥0.999 近孪生塌缩随底盘放大（W1 1,000 底盘塌缩 34.2%→658；本波 5,000 底盘×止损面分裂孪生对 → 预期塌缩 10-35%）。
2. **null 底与初筛通过率**：null 族 beat6m 中位 <0.50（成本拖累方向·W1 同向）；p95 ∈ [0.42, 0.62]；初筛存活率 ∈ [2%, 15%]（W1 实证 14.9%（149/1000 已扣除 null）附近随止损面分布变化）→ 存活 [100, 750] 格。
3. **判决面**：G1'v2 过线 [0, 60]；**G2 eligible [0, 5]——模态结局=零或近零**（DSR 按累计 N≈294k+5,200 折减=极重校正·W1/MASS/T-87 五批判负同门实证；零存活=合法产出如实呈报）。
4. **初始止损面效应（本波新增面·方向预测）**：止损武装面 vs none 面——per-trade 左尾收窄但 whipsaw 摩擦+次日开盘跳空成本 → beat6m 中位预期**略降**（保险成本方向）；ATR 族在高波函数族存活率预期>pct 族（自适应口径）；方向预测错=大考面诚实读数不翻案。
5. **族间富集方向**：A 族初筛存活率预期>B 族（负先验函数占比·W1 同向预测）。
6. **极端日先验（硬界三件套(c)·D-20260925-01①）**：本波数据窗内潜在极端微观结构日=2015-07 救市（宽基单日 ±9~10%）、2016-01 熔断、2024-02 微盘崩、2024-09-24/09-30 政策脉冲（宽基单日 +10~20%）、2025-04-07 外生缺口、2026-01-19 极端溢价日——候选曲线尾部 |日收益|>8% 属市场真值非腐坏；**止损面新增披露**：极端缺口日止损触发→次日开盘出场=跳空损耗集中日（stop cascade 形态），判读面=整窗读数+dd 线非单点 max 检测线 → 极端日经整窗路径内化**无豁免路径需求**；危机日计数+止损触发日计数列随格披露。

## §6 产物

- runner：`scripts/trial_labor_w2.py`（subcommands: generate / screen / judge / intake / status / selftest；import-face 复用 trial_labor_w1.py 枚举/装载/锚门/包络原语+mass_trial_w1.py Sobol sample_draws 范式+strategies/ 工厂+engine/backtester 引擎·禁重写禁改；selftest=hermetic 合成面离线夹具 r116 律+B7b 契约腿 r297 律+确定性双跑字节恒等；**初始止损叠加层=grammar 层实现，engine/exit_rules.py 零触碰**）。
- 产物：`results/trial_labor_w2/`——w2_grammar.json（语法哈希+函数-参数值域表+轴网格含止损轴+去重审计）+ w2_candidates.json（全量候选+provenance+D6 披露列+止损面列）+ w2_screen.json（null 族+floor+全格 beat6m 分布·零选择性披露）+ w2_screen_cells.csv（小件入 git）+ w2_judge.json（判决全面+G1'/G2/DSR/PBO/E[FP]）+ w2_intake.json（上岗/D6 裁定）；全部顶层 evidence_cutoff+audit 段。
- 语法消耗登记簿：`research/TRIAL_GRAMMAR_LEDGER.md`（append-only·wave-2 行=语法哈希+raw/dedup 计数+seed+消耗时点）。
- 池路由：SCREEN/JUDGE 批 >5min 入池（O-2100）；**lane_owner=null**（core48+T-18 in-repo 双机可跑·judge 面 cache-less 机 in-runner exit 2 诚实秒级=W1 先例）；workers_plan ≤floor(核×0.8) BelowNormal；RAM 门禁 r354 三采样律（池条目 data_gates 注记）；**CPU 排队=池优先序自主调度**（当前 census W2B 燃批=优先级 1 在飞，SCREEN 入池后按 entered_at 优先序排后=物理依赖合法排序票内留痕）；C 族 when-ready 见 §9。

## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】

（一次定稿；工程修复重跑双跑留痕如实记账；确定性引擎产物写 bug 的合法重执行口径≠结果重跑）

## §8 批后复盘【必填·s7-T】

（预测对账+门禁链损耗账 results/gate_attrition.json 追加行+判线 v2 当批读数（skill_line_v2 数字）+回执入轮报告+CODELY.md 行级追加；若注册新员：注册件带 evidence_cutoff+live/paper SIGNAL_BUILDERS 接线+smoke 锚定门复跑；首波大考结果 48h 内呈 CEO）

## §9 追加冻结节【append-only·每 sub-wave 一冻·禁跑前另行冻结】

### §9.1 供给族 C（因子普查存活腿·when-ready 禁跑面·预declare）

- 门态（2026-09-28 r357 实况）：T-86 census **W2A 已 finalize**（r357 池翻 done·ledger 294,304·clean exit；家族聚合面=w2a_summary 五族统计+跨族 top10 已落盘）+**W2B 燃批在飞**（03:40 发射·双门修复后 probe 实弹绿·est ~10h）——**in-flight 跑禁重复**（票面 anti-dup hard law）；存活腿 roster 导出=T-23 intake funnel judged 消费面裁定后（W1 §9.1 同门）。
- C 族结构（预declare·跑前须 §9.2 append-confirm）：N_C=500 抽同轴系同机器同止损面；模板腿=census 存活融合腿（W2A+W2B finalize 后 §4 家族聚合 top 融合族清单出口·T-23 intake funnel judged 消费面裁定后导出 roster）；门=**W2A+W2B 双 finalize**+存活腿 roster 导出+**§9.2 append-confirm 冻结**（roster+参数值域+排除集逐项 declare）后才准 generate；**本 §9.1 零格已烧零授权跑**。

### §9.2 C 族 append-confirm【跑前另行冻结·占位】

（W2B finalize+C 族 roster 导出后由当值机起草冻结：精确腿清单+参数值域+已判格排除集+D8/热面边界披露·R99 每 sub-wave 一冻）
