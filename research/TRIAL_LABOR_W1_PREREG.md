# TRIAL_LABOR_W1_PREREG — T-94 s1 千人试用期大考 wave-1 波级预注册（MASS CANDIDATE TRIAL PROGRAM 首波）

> 模板=research/PREREG_TEMPLATE.md（§0-§8 全节）；跑前 commit 冻结；跑后只回填 §7/§8，禁改判据禁重跑。
> 令源：CEO 直令 O-2026-09-27-2245（「测试的时候，把cpu算力吃满，多用试用期的交易员，哪怕一千个？五千个？只要能扛得住。科学理性的去尝试」）+ O-2026-09-27-2250 常设律（firm/TRIAL_LABOR_LAW.md v1.0）。票=T-2026-09-27-94 s1（bm-b r346 认领 22:48:57，本冻结=开动交付物）。
> 统摄律：firm/RANDOM_LARGE_SAMPLE_LAW v1.0（判决面）+ firm/REFINE_BENCH_LAW v1.0（轴系）+ TRIAL_LABOR_LAW §1-§6 + research/BACKTEST_SCIENCE.md v2（判据唯一权威）+ BACKTEST_PLAN.md 三铁律 + COMPUTE_AUDIT.md 批件纪律。
> **本件=波级（wave-level）预注册**：生成语法+漏斗规则+判据全冻结（R99）；sub-wave 追加面一律走 §9 append-confirm（每 sub-wave 一冻），禁用本冻结面跑追加波。

## §0 批件身份【跑前】

- 批名/批号：**TRIAL_LABOR_W1**（千人试用期大考 wave-1）。三层漏斗=批内分批入账（dict schema 唯一）：
  - **TRIAL_LAB_W1_SCREEN**（s2 初筛批）：batch_trials = 去重后候选数 + 200 null（每格 1 trial；raw 抽样 1,000 → 去重门后 ≤1,000 distinct——**1000=上限非凑数指标**，语义重复=无效人不计数·造数凑烧禁律）；
  - **TRIAL_LAB_W1_JUDGE**（s3 全量判决批）：batch_trials = 初筛存活者数（judged cells；双 nulls=B/P 重采样=derivation 面 ledger +0·census §9.2 NAV 推导面先例）；
  - 两批 evidence_cutoff 均=**2026-09-22**（统一 binding·深轴绑定制·T-34 先例；见 §2）。
- 认领：T-2026-09-27-94 s1 claimed bm-b r346（CEO 即时律·认领即开动）；F-04 先行=**MSG-20260927-2310-bmb-all-trial-labor-w1-prereg**（fleet/inbox/ 在制窗口声明·本冻结同窗）。
- 部门归属：dept:策略（生成引擎·供给面）+dept:研究（判决漏斗·判据面）joint（票面 note）。
- 算力预算：生成+去重=轻（分钟级单机）；初筛批≈1,200 格（≤1,000 候选+200 null）× 全史引擎回测——实测锚=~28s/候选单核（O-2245 产力账 616s/22），**估 1-3h @ ≤floor(核×0.8) workers 池批**（>5min 一律入 results/runnable_pool.json·O-2100 执行面分离；每 50 候选一 checkpoint 跨轮续跑·R41）；判决批=分钟级/格（双 nulls 向量化重采样）。批报告必带 audit 段（无 audit 段结果件不入账本）。
- **供给粒度如实披露**：RANDOM_LARGE_SAMPLE_LAW §2.2 N≥500/族——「族」=供给族（票面三分法）：A=在编六员工模板族 500 抽、B=流派战法模板族 500 抽（→wave-1 raw 1,000=票面 1000 目标）；C=因子普查存活腿族（when-ready·§9 禁跑面）。B 族内逐函数均摊 ≈7 抽/函数（71 函数）=广度优先薄覆盖——**5000 人 wave-2 才深化逐函数覆盖**（~70 抽/函数），本波粒度如实入账不掩饰。

## §1 α 机制段【四选一+论证·D6 门槛】

- **供给族 A（在编六员工模板精炼）**：[x] 风险溢价（主）+行为偏差（辅）——母员机制继承：VOLATILITY-CE-01=低波风险溢价（彩票偏好者付出）、COMPOSITE-CE-01/02=低波+低振幅+动量复合溢价（追涨杀跌注意力梯度付出）、ENGULF/NEEDLE/DROUGHT=确认构造行为反转（恐慌抛售者付出）。本波主张=**母员 α 在 REFINE_BENCH 轴系精炼下可发现增益变体**；代价支付者与母员注册线同源。
- **供给族 B（流派战法模板大考）**：[x] 逐流派四选一（11 流派映射·工厂批次血统）：趋势跟踪/动量轮动=持续性风险溢价；均值回归/K线形态/民间手法/技术经典（确认构造）=行为偏差（处置效应/超卖过度）；波动率=风险溢价；情绪资金=行为偏差（注意力稀缺）；日历季节=结构性（月末/季末资金面节律）；宏观过滤=结构性（状态持续性）；事件缺口=行为偏差+微观结构；组合引擎=风险溢价+行为复合。**本波主张=冻结工厂库在随机参数×轴系下存在仅大规模抽样可检出的 α 口袋**；代价支付者随流派先验，负先验标签（34 判负函数）如实随格携带、漏斗平等处置不预筛。
- **D6 同族相关性准入【大考面适配声明·census §1 探索面先例+P4 锦标赛先例合成】**：批内 1,000 候选两两 corr 矩阵全量计算（去重门机器副产品）；**≥0.999 塌缩=生成段绑定门**（§3）；0.7 线对在册六员=**全候选计算+披露**（逐格 max|corr| 列），**绑定生效位=s4 intake**（≥0.7 拒收·存活者簇内 ≥0.7 塌缩留最优）；批内 0.7-0.999 中带=锦标赛选择面（漏斗+PBO 承担多重性），非准入门——与 census「相关性结构=产出面」先例一致，judged 注册效力只走到 s4 intake 时才发生。
- 排除律（反 dredging·判负族重试 §5 合法通道内）：**已判精确格（正负皆然）禁重跑**——同 (template, params, axis_config) 组合若已在在册判决产物中（注册六员注册配置、34 判负函数默认参数原批配置等），生成段排除并逐格留痕（grammar 消耗登记簿）；本波=新 prereg+更大 N+新方法（轴系组合），符合 RANDOM_LARGE_SAMPLE_LAW §5 唯一合法重试通道。

## §2 数据与面板【跑前探针事实，非结果】

- 宇宙/池：**core48**（ETF 交易线正典域·在册六员注册域；loader=引擎 T-22/T-34 血统 import-face 复用禁重写）+ 判决段深轴=**T-18 增长成员面板**（2013-06-17 起·manifest PASS·cutoff 2026-09-22）。
- **evidence_cutoff=2026-09-22（统一 binding·两轴同截）**：legacy 轴截断到 2026-09-22（弃 09-23/09-24 两 bar·与深轴对齐——T-34 binding 先例+PROS_REGIME_SEGMENTS uniform-cutoff 先例；换双轴齐截=G-CENSUS 对 t22 冻结记录逐位相等无需 probe-adjudication）；cutoff 后新 bar 锁定不得回流本批；结果 JSON 顶层必带 `science_gates.cutoff_meta("2026-09-22")`（缺字段=C2 VIOLATION）。
- 虚拟起点（RANDOM_LARGE_SAMPLE_LAW §2.1 K≥1000 ✓）：**legacy=1,255 + deep=1,506**（T-22 冻结记录 results/t22_virtual_timepoints.json 实读，禁手抄）；初筛面=legacy 单轴 1,255 起点（廉价单面）；判决面=双轴全量。
- 数据完备门（fail-closed，不过即 VOID 中止零产数）：
  - **G-PANEL**：core48 48/48 员·每员≥60 行·截断后末行日期==2026-09-22 逐员唯一·OHLCV 列齐；
  - **G-CENSUS**：冻结 cutoff 下重枚举起点集逐位==T-22 记录 {legacy: 1,255, deep: 1,506}（实读断言）；
  - **G-ANCHOR**：在册六员注册配置经本波 grammar 引擎默认轴路径（template_default+EW+daily）重放，IS/OOS Sharpe==live.paper 锚定门常数（import 实读零手抄；不等=管线漂移 VOID——本波核心完整性门）；
  - **G-MANIFEST**：深轴 manifest verdict==PASS 且 18 员（t34 in-runner 断言先例）；
  - **G-EXCLUDE**：已判格排除清单装载+命中计数披露（排除>0 合法、排除=0 如实）。

## §3 方法学【冻结】

- **生成语法（全部冻结·零新信号发明——候选只从冻结规则原语组合生成）**：
  - 原语面=策略工厂 `strategies/` **81 函数/13 模块**（2026-09-27 实测 import 计数）；族 A=在编六员工模板（low_vol_long/composite_top5/composite_top8/engulf_reversal/needle_probe/vol_drought_reversal）；族 B=其余工厂函数 **71**（81−6−4：grid 模块 4 函数**排除**——GRID 线有专用判决线 GRID-SLEEVE-P1 且其机械不可由通用语法表达，如实披露）；函数-参数空间=各函数签名参数+冻结值域（runner build 时逐函数枚举值域表随 w1_grammar.json 序列化冻结）。
  - 轴系（REFINE_BENCH_LAW §2 标准轴·离散网格）：入场过滤 ∈ {none, depth_thresh, amplitude, liquidity, trend_slope, dual_window, fundamental_mask}（7·基本面闸=data/fundamental 掩码硬过滤·in-repo 确定性）× 出场 ∈ {template_default, CE 注册机, time_stop_5d/7d/10d/20d（纯时间止+TRIAL_LABOR_LAW §3 持有期族含 20d）, trailing_stop（移动止损）, profit_ladder（止盈阶梯）}（8·「再止损」需逐函数初止损参数定义=wave-2 语法扩容面·本波如实不编）× 仓位 ∈ {equal_weight, inverse_vol, cap20（单票帽）, regime_delever}（4）× 时机 ∈ {daily_signal, weekly_grid}（2·T+1 开盘保守代理引擎原生 O-1132）——**448 轴组合/模板**。
  - 随机抽样（RANDOM_LARGE_SAMPLE_LAW §2.2）：**均匀抽样**（律文「Sobol/均匀」二选一之均匀腿·依赖安全确定性 PCG64；Sobol=wave-2 可选升级另declare）；N=500/族（A 500+B 500=raw 1,000）；每抽=参数空间内均匀 draw+轴组合均匀 draw+模板轮转确定性指派（A=6 模板轮转、B=71 函数轮转）；**seed 基=`trial_labor_w1_gen`=20283500**（派生律=每候选 `np.random.default_rng([20283500, family_idx, draw_idx])` PCG64 双整派生·census §9.1 协议·零 band 占用·重跑字节恒等；SEED_REGISTRY 本冻结 commit 同步登记·R250 一步律）。
  - **去重门（T-84 s3 组合恒等坍缩律·强制）**：①持仓恒等指纹=`sha256(逐再平衡日 sorted((sym, round(w,4))))` 全等→塌缩；②候选日收益序列两两 `|corr|≥0.999`→塌缩为一格（坍缩裁定保留代表=确定性最低 candidate_id·原始变体入 audit 段全量保留）；**塌缩计数+保留/淘汰清单如实披露**（「N 变体塌缩=1 格」显式注记·V60_LESSONS_INTAKE §s3 逐字）；判读与账本按坍缩后格数记。
- **s2 初筛（廉价面先行·TRIAL_LABOR_LAW §2）**：每 distinct 候选=legacy 轴全史一回测（V1 13bp base 面·T+1）→日收益曲线→**beat6m=1,255 虚拟起点中「候选 6m 前向收益≥同窗被动（起点日已上市成员等额 EW buy&hold·零再平衡·T-22/T-34 C 臂同款）」比例**（完整窗子集·partial 窗计数如实披露）。
  - **初筛 null 族**：K=200 同结构随机信号候选（模板腿替换为随机信号日生成器·轴腿同网格同参数空间 draw·同引擎同成本同面板——BACKTEST_PLAN 三铁律「每批回测同跑随机信号基线」）；**seed=`trial_labor_w1_scrnull`=20284000**（派生 `[20284000, i]`·同 commit 登记）。
  - **初筛判线（跑前写死）**：**存活 iff beat6m > null 族 p95**（程序冻结·零手挑阈值·数据自适应刻度）；二项参照（p=0.5·n=1,255）z/p 值逐格披露列。初筛=**漏斗阶段非判决**（票面「disclosed as funnel stage」逐字）——零注册效力，存活者仅获判决面入场券。
- **s3 全量判决（存活者·TRIAL_LABOR_LAW §2/§3）**：双轴（legacy 1,255+deep 1,506 起点）× 窗口 {6m=126, 12m=252, 24m=504}（P-5 切片法）× 成本面 {base x1, x2=CostPatch(2.0)（t22 Erratum-1 multiplier 律·禁直引 COST_X2_RATE）} × 政体分段 bear/bull/chop+na（T-22 §3 冻结 3-way proxy 逐字）× **双 nulls**（RANDOM_LARGE_SAMPLE_LAW §3）：block bootstrap **B=2000**（block=20 交易日循环块·拼样截回 n 长）+ sign-flip 置换 **P=2000**（逐日符号独立翻转·双侧）；**seed=`trial_labor_w1_unc`=20284500**（派生 `[20284500, cell_idx]`·同 commit 登记）；rng 流仅限两重采样面禁挪用（census §9.1 用途钉死先例）。
  - **样本充足律**（RANDOM_LARGE_SAMPLE_LAW §3）：n_eff≥500 起点 ∧ bear/bull/chop 三段各 ≥100 起点窗（na 桶披露）——不足→verdict=**insufficient-sample 禁算 pass**。
  - 描述条款（批级披露·不替代 v2 门）：年化>0·OOS(2025+ 恒盲)双正·回撤≥−35%·无崩年·x2 面逐年稳定。
- **成本口径**：V1 legacy 引擎面（13bp·T+1·退出优先级冻结禁改）+x2 压测面——与在册锚定/注册判读血统同源可比（注册面一致性优先·V2 迁移=未来波次决策另declare）。
- **账本**：`science_gates.append_ledger("TRIAL_LAB_W1_SCREEN", <distinct 候选+200>, file, evidence_cutoff="2026-09-22")` + `science_gates.append_ledger("TRIAL_LAB_W1_JUDGE", <存活者数>, file, evidence_cutoff="2026-09-22")`（prev=数据驱动链头实读禁手抄）。

## §4 判据【跑前写死·禁看结果调线·共享库引用零手抄】

- **G1' v2 = `science_gates.g1_prime_v2(sharpe_full, returns, batch_cells, pool="core48", n_trades, n_entries)`**：全期 Sharpe>skill_line_v2（数据驱动=max(被动+0.10, μ_null+σ_null·√(2·ln N_eff))·N_eff=活链头+本批格）**且**平稳 bootstrap CI 下界>0 **且** entries≥30（F6 双口径 entries_ok 为准）；批报告逐列披露 skill_line/bootstrap_ci/trade_gate 全输入。
- **G2 注册资格 v2 = `science_gates.g2_registration_v2(g1_pass, dsr, pbo)`**：G1' 过线 **且** DSR≥0.95（`deflated_sharpe_ratio` 原始收益跑；**n_trials=累计账本总试验数**（活链头实读·**跨波不重置**·TRIAL_LABOR_LAW §4——当前链头 286,551（2026-09-27 实读·跑时以活值为准）+本波 SCREEN 格并入后折减）·禁 dsr_from_stats 充数）**且** 家族 PBO≤0.25（`screening/pbo.py` CSCV 8 块·**家族=策略模块**（12 非 grid 模块·族内全部波内候选 base 面 Sharpe 向量=同族竞争网格 g25_retro 先例；<8 格族=insufficient 如实 n/a→G2 不可过））；缺输入=诚实拒收（missing_inputs 机制）。
- **波级多重检验披露（O-2245 强制·护栏随 N 加码）**：①本波总试验数 N_wave=SCREEN 格+JUDGE 格逐批披露；②**预期假阳性数 E[FP]=0.05×N_wave_judged_cells**（判决面名义 α=5% 口径）如实披露——DSR≥0.95 门即多重检验校正门（按累计 N 折减后仍需 95% 把握），通过者=校正后存活非名义面；③波级 PBO 聚合读数另列（跨族）；④语法消耗登记簿（research/TRIAL_GRAMMAR_LEDGER.md·append-only）落 wave-1 语法哈希行——**同语法禁重跑**（防疏浚·TRIAL_LABOR_LAW §4）。
- **s4 intake（上岗线·O-2245 三.3）**：G2 eligible 存活者 → **D6 绑定门**（对在册六员+存活者两两 max|corr|·日收益口径·sleeve-tag 先例；≥0.7 拒收·存活者簇内塌缩留 DSR 最高者（平手=最低 candidate_id））→ STRATEGY_LIBRARY 注册行（带 evidence_cutoff+SIGNAL_BUILDERS 接线+smoke 锚定门复跑·模板 §8 律）+ **TRIAL-<FAMILY>-<NN> 纸盘上岗**（O-2045 PROSPECT 机器复用·观察车道）+ **48h 内 CEO 呈报**。**实际存活数按实际判（预计十至几十·零存活=合法判读照报不翻案）**。

## §5 跑前预测【写死于跑前·≥3 条·含极端日先验】

1. **去重率**：raw 1,000 → distinct ∈ [800, 1,000]；塌缩主径=corr≥0.999 腿（近孪生轴/参数组合预期 0-20%），sha256 恒等腿≈0（确定性指派+Sobol 级去重抽样无重复点）。
2. **null 底与初筛通过率**：null 族 beat6m 中位 <0.50（成本拖累方向），p95 ∈ [0.42, 0.62]；初筛存活率 ∈ [2%, 15%]（噪声基率 5%±真信号增量）→ 存活 [20, 150] 格。
3. **判决面**：G1'v2 过线 [0, 30]；**G2 eligible [0, 3]——模态结局=零**（DSR 按累计 N≈287k+ 折减=极重校正·T-87 五批判负同门实证；零存活=合法产出如实呈报）。
4. **族间富集方向**：A 族（在册精炼）初筛存活率预期>B 族（负先验函数为主）——先验标签随格携带、漏斗零预筛，方向预测错=大考面诚实读数不翻案。
5. **极端日先验（硬界三件套(c)·D-20260925-01①）**：本波数据窗内潜在极端微观结构日=2015-07 救市（宽基单日 ±9~10%）、2016-01 熔断、2024-02 微盘崩、2024-09-24/09-30 政策脉冲（宽基单日 +10~20%）、2025-04-07 外生缺口、2026-01-19 极端溢价日——候选曲线在这些窗的尾部 |日收益|>8% 属市场真值非腐坏；本波判读面=整窗读数+dd 线（非单点 max 检测线）→ 极端日经整窗路径内化**无豁免路径需求**；危机日计数列随格披露。

## §6 产物

- runner：`scripts/trial_labor_w1.py`（subcommands: generate / screen / judge / intake / status / selftest；import-face 复用 T-22/T-34 枚举/装载/锚门/包络原语与 strategies/ 工厂·engine/backtester 引擎禁重写禁改；selftest=hermetic 合成面离线夹具 r116 律+B7b 契约腿 r297 律（下游消费键集 ⊆ 构造键集断言）+确定性双跑字节恒等）。
- 产物：`results/trial_labor_w1/`——w1_grammar.json（语法哈希+函数-参数值域表+轴网格+去重审计）+ w1_candidates.json（全量候选+provenance+D6 披露列）+ w1_screen.json（null 族+floor+全格 beat6m 分布·零选择性披露）+ w1_screen_cells.csv（小件入 git）+ w1_judge.json（判决全面+G1'/G2/DSR/PBO/E[FP]）+ w1_intake.json（上岗/D6 裁定）；全部顶层 evidence_cutoff+audit 段。
- 语法消耗登记簿：`research/TRIAL_GRAMMAR_LEDGER.md`（append-only·wave 行=语法哈希+raw/dedup 计数+seed+消耗时点）。
- 池路由：SCREEN/JUDGE 批 >5min 入池（O-2100）；**lane_owner=null**（core48+T-18 面板 in-repo 双机可跑）；workers_plan ≤floor(核×0.8) BelowNormal；**排队于 W2A/W2B census 燃批之后**（CPU 物理依赖·票内留痕合法排序——当前 W2A 燃烧中 no-kill carry）；C 族 when-ready 见 §9。

## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】

（一次定稿；工程修复重跑双跑留痕如实记账；确定性引擎产物写 bug 的合法重执行口径≠结果重跑）

## §8 批后复盘【必填·s7-T】

（预测对账+门禁链损耗账 results/gate_attrition.json 追加行+判线 v2 当批读数（skill_line_v2 数字）+回执入轮报告+CODELY.md 行级追加；若注册新员：注册件带 evidence_cutoff+live/paper SIGNAL_BUILDERS 接线+smoke 锚定门复跑；首波大考结果 48h 内呈 CEO）

## §9 追加冻结节【append-only·每 sub-wave 一冻·禁跑前另行冻结】

### §9.1 供给族 C（因子普查存活腿·when-ready 禁跑面·预declare）

- 门态（2026-09-27 实况）：T-86 census W2A 燃烧中（本机 no-kill carry）+W2B waiting（D8 已收·候 W2A finalize）——**in-flight 跑禁重复**（票面 anti-dup hard law）；W1 census 已交=EXPLORATION 面（家族清单出口）。
- C 族结构（预declare·跑前须 §9.2 append-confirm）：N_C=500 抽同轴系同机器；模板腿=census 存活融合腿（§4 家族聚合 top 融合族清单出口·T-23 intake funnel judged 消费面裁定后导出 roster）；门=W2A+W2B finalize+存活腿 roster 导出+**§9.2 append-confirm 冻结**（roster+参数值域+排除集逐项 declare）后才准 generate；**本 §9.1 零格已烧零授权跑**。

### §9.2 C 族 append-confirm【跑前另行冻结·占位】

（W2 finalize+C 族 roster 导出后由当值机起草冻结：精确腿清单+参数值域+已判格排除集+D8/热面边界披露·R99 每 sub-wave 一冻）

### §9.3 零跑修正案：census 口径绑定 P-5C 冻结栅格（bm-b r347 · 虚假前提实证 · 零格已烧合法窗）

- **触发**（起草面事实·非结果驱动）：§2 原文以 T-22 记录 {legacy: 1,255, deep: 1,506} 为 census 门——该记录是 **09-23 栅格**口径（t22 文件 legacy cutoff=2026-09-23）；本波 binding cutoff=**2026-09-22** 恰为 **P-5C 冻结栅格**（`scripts/p5c_virtual_timepoint.py` `EVIDENCE_CENSUS_GRID=EVIDENCE_CUTOFF_GRID="2026-09-22"`·两腿共用·`FROZEN_CENSUS`（p5c_grid_probe.json r105）=L {6m: **1253**, 12m: 1127, 24m: 875}+D {6m: 3104, 12m: 2978, 24m: 2726}），在 09-22 栅格上重枚举「逐位==1255」=构造性假红（G-V3 leg-2 虚假前提同族·DECISION_CHAIN §9.3 先例）。
- **修正**：本波**整体绑定 P-5C 冻结栅格机械**（import 禁重实现·反重复铁律）：①初筛面=leg-L 6m 面，census 门==`FROZEN_CENSUS["L"]["6m"]`=**1,253**（模块自带 in-runner census abort 门逐字复用）；②判决面=双腿窗口 {6m,12m,24m} 全网格，census 门逐面==FROZEN_CENSUS 对应腿窗值（L 1253/1127/875·D 3104/2978/2726）；③被动=模块 `passive_rel`/passive-cell 机械（起点日已上市成员 EW buy&hold·零再平衡·语义与 §3 原文同）；④leg-L 宇宙口径=模块 `MIN_LISTED=24`（census caliber never binds·模块原文注记）；⑤深腿=Money02 t18_deep_panel cache 只读（WILD-S1/KLINE 只读先例·禁写）。RANDOM_LARGE_SAMPLE_LAW §2.1 K≥1000 判定不受影响（初筛 1,253 ✓）。
- **G-ANCHOR 一致性注记**：live.paper 锚定门常数 cutoff=2026-09-22（smoke 实测「cutoff 2026-09-22」）与本波 binding 同栅=锚门复放语义自洽，§2 G-ANCHOR 原文零改动。
- **反 dredging 合规**：修正时点=零格已烧（runner 未建、generate 未跑、池零入口）——非结果驱动；§2/§3 原文不删留档（append-only）；判据语义（G1'v2/G2/DSR/PBO/E[FP]/去重门/初筛 null-p95 线）零触碰。
