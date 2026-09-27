# TRIAL_LABOR_W3_PREREG — T-97 千人试用期大考 wave-3 波级预注册（MASS CANDIDATE TRIAL PROGRAM 第三波·5000 人政体门深化波）

> 模板=research/PREREG_TEMPLATE.md（§0-§8 全节）；跑前 commit 冻结；跑后只回填 §7/§8，禁改判据禁重跑。
> 令源：CEO 直令 O-2026-09-27-2245（「测试的时候，把cpu算力吃满，多用试用期的交易员，哪怕一千个？五千个？只要能扛得住。科学理性的去尝试」）+ O-2026-09-27-2250 常设律（firm/TRIAL_LABOR_LAW.md v1.0「以后不要我提醒」）+ T-20260928-97 波级 prereg 票（bm-a r391 认领，本冻结=同轮开动交付物；TRIAL_LABOR_LAW §1 常供律默认动作：板空+池饿+零在飞判决批〔三判决批全在 RAM/物理门后非在飞·r391 实况〕→ 起草下一波；sequencing_gates：起草本体无门禁任意轮可开=W2 同律）。
> 统摄律：firm/RANDOM_LARGE_SAMPLE_LAW v1.0（判决面）+ firm/REFINE_BENCH_LAW v1.0（轴系）+ TRIAL_LABOR_LAW §1-§6 + research/BACKTEST_SCIENCE.md v2（判据唯一权威）+ BACKTEST_PLAN.md 三铁律 + COMPUTE_AUDIT.md 批件纪律。
> **本件=波级（wave-level）预注册**：生成语法+漏斗规则+判据全冻结；sub-wave 追加面一律走 §9 append-confirm（每 sub-wave 一冻），禁用本冻结面跑追加波。
> **本波与 W1/W2/MASS 语法血统**：新增政体入场门轴 GATE（§3 扩容面 a）→ **新语法新 sha16**（≠W1 a2fa15f4b06b3c40 ≠MASS 96269ebe766c3fc2 ≠W2 1dd3d95792395cec），同语法禁重跑律（TRIAL_LABOR_LAW §4）经新语法面合法开波。

## §0 批件身份【跑前】

- 批名/批号：**TRIAL_LABOR_W3**（千人试用期大考 wave-3·5000 人政体门深化波）。三层漏斗=批内分批入账（dict schema 唯一）：
  - **TRIAL_LAB_W3_SCREEN**（s2 初筛批）：batch_trials = 去重后候选数 + 200 null（每格 1 trial；raw 5,000 → 去重门后 ≤5,000 distinct——**5000=上限非凑数指标**，语义重复=无效人不计数·造数凑烧禁律）；
  - **TRIAL_LAB_W3_JUDGE**（s3 全量判决批）：batch_trials = 初筛存活者数（judged cells；双 nulls=B/P 重采样=derivation 面 ledger +0·census §9.2 NAV 推导面先例）；
  - 两批 evidence_cutoff 均=**2026-09-22**（P-5C 冻结栅格 binding·双轴同截·W1 §9.3 零跑修正案整体沿用——见 §2）。
- 认领：T-20260928-97 claimed bm-a r391（TRIAL_LABOR_LAW §1 常供律例行供给步，无需 GM 另署名=W2 先例）；F-04 先行=**MSG-20260928-0755-bma-all-trial-labor-w3-prereg**（fleet/inbox/ 在制窗口声明·本冻结同窗）。
- 部门归属：dept:策略（生成引擎·供给面）+dept:研究（判决漏斗·判据面）joint（票面 note 同 W1/W2）。
- 算力预算：生成+去重=轻（分钟级单机，76 函数值域表枚举+5,000 抽样）；初筛批≈5,200 格（≤5,000 候选+200 null）× 全史引擎回测——实测锚=~28s/候选单核（W1 O-2245 产力账）+W2 实弹 3,124 格两分钟级池批（06:50-06:52 五五开实测·r389），**估分钟级-小时级 @ ≤floor(核×0.8) workers 池批**（>5min 一律入 results/runnable_pool.json·O-2100 执行面分离；每 50 候选一 checkpoint 跨轮续跑·R41；CPU 排队=池优先序自主调度）；判决批=分钟级/格（双 nulls 向量化重采样）。批报告必带 audit 段（无 audit 段结果件不入账本）。
- **供给粒度如实披露**：A=在编六员工模板族 500 抽（常供律维持面）；B=流派战法模板族 4,500 抽 → **76 函数均摊 ≈59.2 抽/函数**（与 W2 同口径·B 面累计 ≈118 抽/函数）；**C=因子普查存活腿族=本波禁碰**（W2 §9.1 已declare 为 W2-C when-ready 子波独占面·anti-dup hard law；W3 如需并入=待 W2-C 消费落地后另波 declare）。judged 存活变体供给面（TRIAL_LABOR_LAW §5）**declare 不可得**：三判决批（TRIAL_LAB_W1_JUDGE 149+MASS_TRIAL_W1_JUDGE 166+TRIAL_LABOR_W2_JUDGE 404）于本冻结时点全在池 waiting（RAM 序列化·r391 实况）→ **(d) 面如实降权为基线网格**（轴族均匀分配零 judged 加权，禁编造；**generate 时点实读重declare**=若届时已落地则按 §5 律并入加权，W2 同门先例）。
- 48h CEO 呈报钟：随判决面落地计（judge-finalize 后 48h·票面持有；非本冻结时点计）。

## §1 α 机制段【四选一+论证·D6 门槛】

- **供给族 A（在编六员工模板精炼）**：[x] 风险溢价（主）+行为偏差（辅）——母员机制继承同 W1/W2 §1（VOLATILITY-CE-01 低波风险溢价/COMPOSITE 低波+低振幅+动量复合溢价/ENGULF·NEEDLE·DROUGHT 确认构造行为反转）。本波主张=**母员 α 在 REFINE_BENCH 轴系+初始止损叠加层+政体入场门下可发现增益变体**；代价支付者与母员注册线同源。
- **供给族 B（流派战法模板大考）**：[x] 逐流派四选一映射同 W1 §1（11 流派·工厂批次血统；负先验标签如实随格携带、漏斗平等处置不预筛）。本波主张=**冻结工厂库在 Sobol 低差异抽样×轴系×止损面×政体门下存在仅大规模深化抽样可检出的 α 口袋**。
- **政体入场门机制注记（本波新增面 a）**：GATE=入场许可的条件化叠加层（非引擎出场规则）——机制归属=**政体条件化风险溢价面**（REFINE_BENCH_LAW §2 R 轴血统：bull/bear 政体下 α 的时变分布；REFINE-BENCH-20260926-P1 首炉定谳「熊市闸=第一杠杆」+MASS_TRIAL_W1 stage-1 复现〔bear 门行存活 119/324=36.7% vs none 29/322=9.0% vs bull 18/329=5.5%〕=本面最强先验）；trial-labor 谱系（W1/W2）此前未开此面=**GATE×初始止损×轴系交互为新增可检空间**。代价=政体错判暴露（MA200 滞后标签成本）+牛市缺席机会成本（bear 面）+熊市参与回撤（bull 面）——三面同网格平等受检，漏斗裁决不预筛方向。
- **D6 同族相关性准入（W1 大考面适配声明整体沿用）**：批内候选两两 corr 矩阵全量计算（去重门副产品）；≥0.999 塌缩=生成段绑定门（§3）；0.7 线对在册六员=全候选计算+披露（逐格 max|corr| 列），绑定生效位=s4 intake（≥0.7 拒收·存活者簇内 ≥0.7 塌缩留最优）；批内 0.7-0.999 中带=锦标赛选择面，非准入门。
- 排除律（反 dredging·W1/W2 同律·**六源**）：**已判精确格（正负皆然）禁重跑**——cell key=(template, params, axis_config, initial_stop, gate)：全部既有已判格隐含 gate=none；gate=none 面上与在册判决产物全等（注册六员配置、34 判负函数默认参数原批、w1_screen.json 存活清单 149+w2_screen.json 存活清单 404+MASS screen 存活清单 166〔三清单 generate 时点实读消费〕+judged 产物三源〔w1_judge+MASS judged+w2_judge：冻结时点全 declare 不可得零行如实·generate 时点实读重declare·W2 同门〕）→ 生成段排除并逐格留痕；**gate∈{bull,bear} 面=新语法面合法格**。本波=新 prereg+新语法（轴系×止损面×政体门×Sobol），符合 RANDOM_LARGE_SAMPLE_LAW §5 唯一合法重试通道。

## §2 数据与面板【跑前探针事实，非结果】

- 宇宙/池：**core48**（ETF 交易线正典域·在册六员注册域；loader=引擎 T-22/T-34 血统 import-face 复用禁重写）+ 判决段深轴=**T-18 增长成员面板**（Money02 t18_deep_panel cache 只读·WILD-S1/KLINE 只读先例禁写）。
- **GATE 门序列（本波新增面·跑前探针事实）**：510300 在 core48 面板在位（data/daily/sh510300.csv·3,483 行·2012-05-28→2026-09-22 cutoff 截·r391 实读）——MA200=收盘价 200 交易日简单均线（min_periods=200；首 199 bar NaN→bull/bear 面 gate-closed 保守披露）；GATE 态在**信号日 d 收盘**信息集上判定（510300 close(d) vs MA200(d)），入场于 d+1 开盘（T+1 因果律·与信号同信息集零前视）。
- **evidence_cutoff=2026-09-22（P-5C 冻结栅格 binding·双轴同截）**：整体沿用 W1 §9.3/W2 机械——**import `scripts/p5c_virtual_timepoint.py` 冻结栅格禁重实现**：初筛面=leg-L 6m 面 census 门==FROZEN_CENSUS["L"]["6m"]=**1,253**；判决面=双腿窗口 {6m,12m,24m} 全网格逐面==FROZEN_CENSUS 对应腿窗值（L 1253/1127/875·D 3104/2978/2726）；被动=模块 passive_rel/passive-cell 机械。G-ANCHOR 一致性：live.paper 锚定门常数 cutoff=2026-09-22 与本波 binding 同栅=锚门复放语义自洽。cutoff 后新 bar 锁定不得回流本批；结果 JSON 顶层必带 `science_gates.cutoff_meta("2026-09-22")`（缺字段=C2 VIOLATION）。
- 数据完备门（fail-closed，不过即 VOID 中止零产数）：
  - **G-PANEL**：core48 48/48 员·每员≥60 行·截断后末行日期==2026-09-22 逐员唯一·OHLCV 列齐；
  - **G-CENSUS**：P-5C FROZEN_CENSUS 逐面实读断言（L/D×{6m,12m,24m} 六值逐位；import 实读禁手抄）；
  - **G-ANCHOR**：在册六员注册配置经本波 grammar 引擎默认轴路径（template_default+EW+daily+initial_stop=none+gate=none）重放，IS/OOS Sharpe==live.paper 锚定门常数（import 实读零手抄；不等=管线漂移 VOID）；
  - **G-MANIFEST**：深轴 manifest verdict==PASS（48-member twin cache 口径·W1 §9.3 manifest_note 先例；**冻结时实读**——r391 实读=trial_labor_w2 judge_state g_manifest PASS/48 员在册，跑时以活值为准）；
  - **G-EXCLUDE**：已判格排除清单装载（§1 排除律六源）+命中计数披露（排除>0 合法、排除=0 如实）。

## §3 方法学【冻结】

- **生成语法（全部冻结·零新信号发明——候选只从冻结规则原语组合生成）**：
  - 原语面=策略工厂 `strategies/` 86 函数/13 模块（W2 r357 同源计数·跑时以 import 实测为准如实披露）；族 A=在编六员工模板（low_vol_long/composite_top5/composite_top8/engulf_reversal/needle_probe/vol_drought_reversal）；族 B=其余工厂函数 76（86−6−4：grid 模块 4 业务函数排除——GRID 线专用判决线机械不可由通用语法表达，W1/W2 同律如实披露）；函数-参数空间=各函数签名参数+冻结值域（runner build 时逐函数枚举值域表随 w3_grammar.json 序列化冻结·W1/W2 同款）。
  - 轴系（REFINE_BENCH_LAW §2 标准轴·离散网格+本波扩容面）：入场过滤 ∈ {none, depth_thresh, amplitude, liquidity, trend_slope, dual_window, fundamental_mask}（7）× 出场 ∈ {template_default, CE 注册机, time_stop_5d/7d/10d/20d, trailing_stop, profit_ladder}（8·与 W1/W2 同集）× 仓位 ∈ {equal_weight, inverse_vol, cap20, regime_delever}（4）× 时机 ∈ {daily_signal, weekly_grid}（2·T+1 开盘保守代理引擎原生 O-1132）× 初始止损叠加 ∈ {none, p3, p5, p8, p12, a15, a20, a25}（8·W2 面沿用·参数语义 W2 §3 逐字继承）× **政体入场门 GATE ∈ {none, bull, bear}（3·本波新增面 a）**——**10,752 轴组合/模板**（W2=3,584·W1=448）。
  - **政体入场门叠加层（扩容面 a·冻结定义）**：GATE 态=信号日 d 的 510300 close(d) vs MA200(d)（§2 门序列）；**bull**=close≥MA200 时许可入场（牛市参与面）；**bear**=close<MA200 时许可入场（熊市参与面）；**none**=无门（W1/W2 语义基线面）；gate-closed 信号日→**有效信号置零**（MSG-0440 E1 映射先例·grammar 层实现，engine/exit_rules.py 零触碰）；门只作用于**入场许开**，出场逻辑零改动；MA200 NaN 窗（首 199 bar）→bull/bear 面 gate-closed 保守（禁入场·如实披露）；gate=none=W1/W2 语义基线面。
  - 随机抽样（Sobol 沿用=W2 declare 血统）：**import-face 复用 MASS_TRIAL_W1 sample_draws 范式禁重写**——`scipy.stats.qmc.Sobol(参数维, scramble=True, seed=SEED_BASE+family_idx)` 归一化参数盒低差异 draw+轴组合独立 RNG 流（`default_rng([SEED_BASE+family_idx, 7919])` 整数轴抽）+**本波新增 GATE 轴并入轴抽流**（六元组 R/X/S/T/STOP/GATE）；N=500/族 A（6 模板轮转确定性指派）+4,500/族 B（76 函数轮转）；**seed 基=`trial_labor_w3_gen`=20287500**（派生=Sobol seed 20287500+family_idx，A 族 idx 0-5·B 族 idx 6-81；轴 RNG 流=[20287500+family_idx, 7919]；零 band 占用·重跑字节恒等；SEED_REGISTRY 本冻结 commit 同步登记·R250 一步律）。
  - **去重门（T-84 s3 组合恒等坍缩律·强制·W1/W2 同律）**：①持仓恒等指纹=sha256(逐再平衡日 sorted((sym, round(w,4)))) 全等→塌缩；②候选日收益序列两两 |corr|≥0.999→塌缩为一格（保留代表=确定性最低 candidate_id·原始变体入 audit 段全量保留）；**塌缩计数+保留/淘汰清单如实披露**；判读与账本按坍缩后格数记。
- **s2 初筛（廉价面先行·TRIAL_LABOR_LAW §2）**：每 distinct 候选=legacy 轴 leg-L 6m 全史一回测（V1 13bp base 面·T+1·初始止损面+政体门面随格携带）→ beat6m=1,253 虚拟起点中「候选 6m 前向收益≥同窗被动」比例（完整窗子集·partial 窗计数如实披露）。
  - **初筛 null 族**：K=200 同结构随机信号候选（模板腿替换为随机信号日生成器·轴腿+止损腿+**政体门腿**同网格同参数空间 draw·同引擎同成本同面板——BACKTEST_PLAN 三铁律）；**seed=`trial_labor_w3_scrnull`=20288000**（派生 `[20288000, i]`·同 commit 登记）。
  - **初筛判线（跑前写死）**：**存活 iff beat6m > null 族 p95**（程序冻结·零手挑阈值·数据自适应刻度）；二项参照（p=0.5·n=1,253）z/p 值逐格披露列。初筛=漏斗阶段非判决（零注册效力，存活者仅获判决面入场券）。
- **s3 全量判决（存活者·TRIAL_LABOR_LAW §2/§3）**：双轴（P-5C 栅格 L/D×{6m,12m,24m} 起点）× 成本面 {base x1, x2=CostPatch(2.0)（t22 Erratum-1 multiplier 律·禁直引 COST_X2_RATE）} × 政体分段 bear/bull/chop+na（T-22 §3 冻结 3-way proxy 逐字）× **双 nulls**（RANDOM_LARGE_SAMPLE_LAW §3）：block bootstrap **B=2000**（block=20 交易日循环块·拼样截回 n 长）+ sign-flip 置换 **P=2000**（逐日符号独立翻转·双侧）；**seed=`trial_labor_w3_unc`=20288500**（派生 `[20288500, cell_idx]`·同 commit 登记）；rng 流仅限两重采样面禁挪用（census §9.1 用途钉死先例）。**注**：GATE 轴=策略构造面（入场许可），政体分段=判读披露面（分段归因）——两面正交不冲突（分段恒带=TRIAL_LABOR_LAW §3 律）。
  - **样本充足律**：n_eff≥500 起点 ∧ bear/bull/chop 三段各 ≥100 起点窗（na 桶披露）——不足→verdict=**insufficient-sample 禁算 pass**。
  - 描述条款（批级披露·不替代 v2 门）：年化>0·OOS(2025+ 恒盲)双正·回撤≥−35%·无崩年·x2 面逐年稳定。
- **成本口径**：V1 legacy 引擎面（13bp·T+1·退出优先级冻结禁改）+x2 压测面——与在册锚定/注册判读血统同源可比（注册面一致性优先）。
- **账本**：`science_gates.append_ledger("TRIAL_LAB_W3_SCREEN", <distinct 候选+200>, file, evidence_cutoff="2026-09-22")` + `science_gates.append_ledger("TRIAL_LAB_W3_JUDGE", <存活者数>, file, evidence_cutoff="2026-09-22")`（prev=数据驱动链头实读禁手抄）。

## §4 判据【跑前写死·禁看结果调线·共享库引用零手抄】

- **G1' v2 = `science_gates.g1_prime_v2(sharpe_full, returns, batch_cells, pool="core48", n_trades, n_entries)`**：全期 Sharpe>skill_line_v2（数据驱动=max(被动+0.10, μ_null+σ_null·√(2·ln N_eff))·N_eff=活链头+本批格）**且**平稳 bootstrap CI 下界>0 **且** entries≥30（F6 双口径 entries_ok 为准）；批报告逐列披露 skill_line/bootstrap_ci/trade_gate 全输入。
- **G2 注册资格 v2 = `science_gates.g2_registration_v2(g1_pass, dsr, pbo)`**：G1' 过线 **且** DSR≥0.95（`deflated_sharpe_ratio` 原始收益跑；**n_trials=累计账本总试验数**（活链头实读·**跨波不重置**·TRIAL_LABOR_LAW §4——r391 冻结时实读=**297,428**（live head=trial_labor_w2/w2_screen.json trials_ledger.total；跑时以活值为准·三判决批落地后随之增）+本波 SCREEN 格并入后折减）·禁 dsr_from_stats 充数）**且** 家族 PBO≤0.25（`screening/pbo.py` CSCV 8 块·**家族=策略模块**（12 非 grid 模块·族内全部波内候选 base 面 Sharpe 向量=同族竞争网格 g25_retro 先例；<8 格族=insufficient 如实 n/a→G2 不可过））；缺输入=诚实拒收（missing_inputs 机制）。
- **波级多重检验披露（O-2245 强制·护栏随 N 加码）**：①N_wave=SCREEN 格+JUDGE 格逐批披露；②**E[FP]=0.05×N_wave_judged_cells** 如实披露（DSR≥0.95 门即多重检验校正门，通过者=校正后存活非名义面）；③波级 PBO 聚合读数另列（跨族）；④语法消耗登记簿（research/TRIAL_GRAMMAR_LEDGER.md·append-only）落 wave-3 行（grammar sha16+w3_grammar.json 序列化时点+raw/dedup 计数+seeds+consumed 时点）——**同语法禁重跑**（防疏浚·TRIAL_LABOR_LAW §4）。
- **s4 intake（上岗线·O-2245 三.3）**：G2 eligible 存活者 → **D6 绑定门**（对在册六员+存活者两两 max|corr|·日收益口径·sleeve-tag 先例；≥0.7 拒收·存活者簇内塌缩留 DSR 最高者（平手=最低 candidate_id））→ STRATEGY_LIBRARY 注册行（带 evidence_cutoff+SIGNAL_BUILDERS 接线+smoke 锚定门复跑·模板 §8 律）+ **TRIAL-<FAMILY>-<NN> 纸盘上岗**（O-2045 PROSPECT 机器复用·观察车道）+ **48h 内 CEO 呈报**（判决面落地起计）。**实际存活数按实际判（零存活=合法判读照报不翻案）**。

## §5 跑前预测【写死于跑前·≥3 条·含极端日先验】

1. **去重率**：raw 5,000 → distinct ∈ [3,000, 5,000]；Sobol 低差异+scramble+新 seed 基 → 精确重复抽≈0；GATE 面三分分裂孪生对（同参数不同门=收益序列近孪生但 gate=none/bull/bear 面有效信号集不同→corr 高但大概率 <0.999 不塌缩）→ 塌缩率预期 10-35% 同 W2 量级（W2 实弹 5,000→2,924 塌缩 41.5%·W1 1,000→658 塌缩 34.2%——**上限预测带 [2,900, 4,600]** 如实放宽披露）。
2. **null 底与初筛通过率**：null 族 beat6m 中位 <0.50（成本拖累方向·W1/W2 同向）；p95 ∈ [0.42, 0.62]（W1 0.5116/W2 0.5116 双波同带）；初筛存活率 ∈ [2%, 15%] → 存活 [100, 750] 格。
3. **判决面**：G1'v2 过线 [0, 60]；**G2 eligible [0, 5]——模态结局=零或近零**（DSR 按累计 N≈297k+ 折减=极重校正·五批判负同门实证；零存活=合法产出如实呈报）。
4. **GATE 面效应（本波新增面·方向预测）**：stage-1 存活率 bear 门面 > none 面 > bull 门面（先验=MASS stage-1 36.7%/9.0%/5.5%+REFINE-BENCH 首炉定谳「熊市闸=第一杠杆」；反转构造密集的 B 族方向预期强于 A 族）；**口径差异诚实注记**：MASS stage-1 判线与本波 beat6m>null-p95 刻度不同构造，方向先验跨刻度迁移不保证成立——读数如实两向皆可、错即诚实读数不翻案。GATE=bull 面在政策脉冲极端日（2024-09-24/09-30）暴露、bear 面缺席=已知不对称（§5.6 披露）。
5. **族间富集方向**：A 族初筛存活率预期>B 族（负先验函数占比·W1/W2 同向预测）。
6. **极端日先验（硬界三件套(c)·D-20260925-01①）**：本波数据窗内潜在极端微观结构日=2015-07 救市（宽基单日 ±9~10%）、2016-01 熔断、2024-02 微盘崩、2024-09-24/09-30 政策脉冲（宽基单日 +10~20%）、2025-04-07 外生缺口、2026-01-19 极端溢价日——候选曲线尾部 |日收益|>8% 属市场真值非腐坏；**GATE 面新增披露**：MA200 门在极端日邻域的翻面滞后（政体切换滞后标签）→ gate 翻面邻域窗=跳空暴露集中窗，判读面=整窗读数+dd 线非单点 max 检测线 → 极端日经整窗路径内化**无豁免路径需求**；危机日计数+止损触发日计数+gate 翻面日计数列随格披露。

## §6 产物

- runner：`scripts/trial_labor_w3.py`（subcommands: generate / screen / judge / intake / status / selftest；import-face 复用 trial_labor_w1.py 枚举/装载/锚门/包络原语+trial_labor_w2.py 初始止损叠加层+mass_trial_w1.py Sobol sample_draws 范式+strategies/ 工厂+engine/backtester 引擎·禁重写禁改；selftest=hermetic 合成面离线夹具 r116 律+B7b 契约腿 r297 律+确定性双跑字节恒等；**初始止损+政体门叠加层=grammar 层实现，engine/exit_rules.py 零触碰**）。
- 产物：`results/trial_labor_w3/`——w3_grammar.json（语法哈希+函数-参数值域表+轴网格含止损轴+政体门轴+去重审计）+ w3_candidates.json（全量候选+provenance+D6 披露列+止损面列+政体门面列）+ w3_screen.json（null 族+floor+全格 beat6m 分布·零选择性披露+GATE 面分段存活统计）+ w3_screen_cells.csv（小件入 git）+ w3_judge.json（判决全面+G1'/G2/DSR/PBO/E[FP]）+ w3_intake.json（上岗/D6 裁定）；全部顶层 evidence_cutoff+audit 段。
- 语法消耗登记簿：`research/TRIAL_GRAMMAR_LEDGER.md`（append-only·wave-3 行=语法哈希+raw/dedup 计数+seed+消耗时点）。
- 池路由：SCREEN/JUDGE 批 >5min 入池（O-2100）；**lane_owner=null**（core48+T-18 in-repo 双机可跑·judge 面 cache-less 机 in-runner exit 2 诚实秒级=W1/W2 先例）；workers_plan ≤floor(核×0.8) BelowNormal；RAM 门禁 r354 三采样律（池条目 data_gates 注记）；**CPU 排队=池优先序自主调度**（当前在飞/门后批=W2B census bm-b 燃+三判决批 RAM 门=物理依赖合法排序票内留痕）；§9 交接见下。

## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】

（一次定稿；工程修复重跑双跑留痕如实记账；确定性引擎产物写 bug 的合法重执行口径≠结果重跑）

## §8 批后复盘【必填·s7-T】

（预测对账+门禁链损耗账 results/gate_attrition.json 追加行+判线 v2 当批读数（skill_line_v2 数字）+回执入轮报告+CODELY.md 行级追加；若注册新员：注册件带 evidence_cutoff+live/paper SIGNAL_BUILDERS 接线+smoke 锚定门复跑；判决面结果 48h 内呈 CEO）

## §9 追加冻结节【append-only·每 sub-wave 一冻·禁跑前另行冻结】

- **W2-C 族面交接注记（anti-dup）**：因子普查存活腿族（census fusion legs）=TRIAL_LABOR_W2_PREREG §9.1 已declare 的 W2 when-ready 子波独占面（门=W2A+W2B 双 finalize+roster 导出+§9.2 append-confirm）——**本波 §0 已declare 禁碰**；W3 未来并入该供给=待 W2-C 消费落地后另波 declare（TRIAL_LABOR_LAW §5 律）。
- **judged 供给 generate 时点重declare 窗**：三判决批（W1/MASS/W2）落地后、本波 generate 跑前=§1 (d) 面加权 declare 窗口（实读产物并入 B 族加权·W2 同门先例）；generate 已跑后落地者=不入本波（禁事后改配）。
- **s3 判决面**：已冻结于 §3（W2 结构同构·无需另行 sub-wave 冻结）；若跑前需修正=零跑修正案先例（r251/r280·如实留痕非结果驱动）。
