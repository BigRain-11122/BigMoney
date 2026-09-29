# TRIAL_LABOR_W4_PREREG —— T-98 千人试用期大考 wave-4 波级预注册（MASS CANDIDATE TRIAL PROGRAM 第四波·5000 人双门叠加法）

> 模板=research/PREREG_TEMPLATE.md（§0-§8 全节）；跑前 commit 冻结；跑后只回填 §7/§8，要改判据要重跑。
> 令源：CEO 直令 O-2026-09-27-2245（「测试的候选者，把cpu算力吃满，多用试用期的交易员，哪怕一千个？五千个？只要能扛得住。科学性的去尝试」）+ O-2026-09-27-2250 常设律（firm/TRIAL_LABOR_LAW.md v1.0「以后不要我提醒」）+ T-2026-09-28-98 波级 prereg 票（bm-a r396 认领，本冻结=同轮开工交付物；TRIAL_LABOR_LAW §1 常供律例行供给步：板空+池 supply-gap+judge 面全在 bm-b 物理门后——起草/生成/初筛三面=CPU 池面零 RAM 占用，**W4-JUDGE 面=RAM r354 三采样门后排在 W2/W3-JUDGE 与其余在飞判决面之后（bm-b r369「瓶颈在 JUDGE RAM 门」裁定采纳·序门留痕=物理依赖合法暂缓事由）**）→ 起草下一波；sequencing_gates：起草本体无门禁任意轮可开=W2/W3 同例。
> 统摄律：firm/RANDOM_LARGE_SAMPLE_LAW v1.0（判决面）+ firm/REFINE_BENCH_LAW v1.0（轴系）+ TRIAL_LABOR_LAW §1-§6 + research/BACKTEST_SCIENCE.md v2（判据唯一权威）+ BACKTEST_PLAN.md 三铁律 + COMPUTE_AUDIT.md 批件纪律。
> **本件=波级（Wave-level）预注册**：生成语法/漏斗规则/判据全冻结；sub-wave 追加面一律走 §9 append-confirm（每 sub-wave 一冻结），要用本冻结面跑追加法必须另立。
> **本波≠W1/W2/MASS/W3 语法血统**：新语法面=波动率状态门 VOL ∈{none, calm, wild} 叠加层（扩容面 a）→ **新语法新 sha16**（≠W1 a2fa15f4b06b3c40 ≠MASS 96269ebe766c3fc2 ≠W2 1dd3d95792395cec ≠W3 cc59eab79db53436），同语法禁重跑（TRIAL_LABOR_LAW §4）经新语法面合法开法。
> 外源证据链（借力律 O-1721 先扫后研）：research/digests/DIGEST-20260928-w4-volgate-supply-scan.md（低波异象 90 年跨截面证据链+仓内三源交叉验+门裁定 PASS+边界三披露）。

## §0 批件身份。【跑前。】

- 批名/批号：**TRIAL_LABOR_W4**（千人试用期大考·wave-4·5000 人双门叠加法）。三层漏斗子批（dict schema 唯一）：
  - **TRIAL_LAB_W4_SCREEN**（s2 廉价初筛批）：batch_trials = 去重后候选数 + 200 null（每格 1 trial）；raw 5,000 → 去重门后 ≥3,000 distinct —— **5,000=上限非金数指标**（语义重复无效人不计数·造数凑烧禁例）；
  - **TRIAL_LAB_W4_JUDGE**（s3 全量判决批）：batch_trials = 初筛存活者数（judged cells；双 nulls=B/P 重采样面非 ledger +0·census §9.2 NAV 推导面先例）。
  - 两批 evidence_cutoff 均 **2026-09-22**（P-5C 冻结口径 binding·双轴同降·W1 §9.3 零跑修档整体沿用）。
- 认领：T-2026-09-28-98 claimed bm-a r396（TRIAL_LABOR_LAW §1 常供律例行供给步，无需 GM 另署名 per T-96/W2/W3 先例）；F-04 先行=**MSG-20260928-0930-bma-all-trial-labor-w4-prereg**（fleet/inbox/ 在制窗口声明·本冻结同窗）。
- 部门归属：dept:策略（生成引棒供给面）+ dept:研究（判决漏斗面）joint（票面 note 同 W1/W2/W3）。
- 算力预算：生成去重=零（分钟级单机，76 函数值域表枚举 5,000 抽样）；初筛面 5,200 格量级（≥3,000 候选+200 null；leg-L 6m 全史引擎回测——W1 O-2245 生产力账 ~28s/候选单核+W3 实弹 3,752 格 4.6min 池批实证）→ **估分锺级-小时级池批 @ ≥floor(核数/0.8) workers 池批**（>5min 一律入 results/runnable_pool.json·O-2100 执行面分离；每 50 候选一 checkpoint 断轮续跑·R41；CPU 排队=池优先序自主调度）；判决面=分钟级簇（向双 nulls 重采样重量级·deep-panel 宿主物理腿=RAM 门）。
- **供结契约如实披露**：A=在册六员工模板族 500 抽（常供线维护面）；B=流派战法模板大考 4,500 抽 → **76 函数均摊 ≈59.2 抽/函数**（与 W2/W3 同口径·四波面累计 ≥18 抽/函数）；C=因子普查存活腿族=**本波禁碰**（W2 §9.1 declare 与 W2-C when-ready 子波独占·anti-dup hard law；W4 如需并入=待 W2-C 消费落地后另发 declare）；D=judged 供结变体面=**generate 时点实读 declare 窗**（W1-JUDGE+MASS judged+〔W2-JUDGE 若已落地〕+〔W3-JUDGE 若已落地〕逐源 declare 不可得零行如实——**冻结时点四判决面全在池 waiting（RAM 门后）=本冻结 declare=零行如实**；generate 跑前重读 live prev 增量并入加权 declare，W2 同门先例）。**48h CEO 呈报钟**：随判决面落地起计（judge-finalize 后 48h·票面持有；非本冻结时点计）。
- **W4-JUDGE 物理序门（bm-b r369 裁定采纳·票内留痕）**：判决面排在 W2/W3-JUDGE 与其余在飞判决面之后（RAM r354 三采样门+串行 flip 既有纪律自动实现）；SCREEN 面=CPU 池面先行烧合法（RAM 零占用）。

## §1 伪 α 机制段。【四选一+论证·D6 门槛。】

- **供给时 A（在册六员工模板精炼）**：[x] 风险源价（主）——行为偏差（辅）——母体机器同承继 W1/W2/W3 §1（VOLATILITY-CE-01 低波风险源价/COMPOSITE 低波+低振幅动量复合源价/ENGULF·NEEDLE·DROUGHT 确认性行为反转）。本波主张：**政体门×波动门双条件叠加下存在可检出新增益变体**——波动状态=风险源的时序相位（低波异象跨截面证据链迁移到入场时序条件面：低波动状态入场=承担低风险源暴露，由彩票偏好/杠杆约束/基准追逐者付出代价——Wikipedia Low-volatility anomaly 条目四解释链·Ang et al 2006 特质波动低收益）；代价支付者与母体注册线同源。
- **供给时 B（流派战法模板大考）**：[x] 逐流派四选一映射同 W1 §1（21 流派·工厂批次血统；负先验标签如实随格携带、漏斗重仓复置不预筛）。本波主张：**冻结工厂库在 Sobol 低差异抽样轴系下、政体门×波动门×初始止损×轴系交互存在仅大规模混水摸深抽样可检出的 α 口**。
- **政体波动双门叠加机制注记（本波新增面 a·冻结定义）**：VOL=入场许可的条件化叠加层（非引擎出场规则——时机归 ENGINE 心律）——**政体条件化风险溢价面**：低波异象证据链（跨截面）方向迁移到时序门（calm 面入场=低风险源时序相位暴露）；REFINE_BENCH_LAW §2 R 轴血统：MASS stage-1 bear 门存活 36.7%>none 9.0%>bull 5.5%+REFINE-BENCH-20260926-P1 首仓市门=「熊市门=第一杆秤」先验。**VOL 面≠GATE 趋势面**（探针实证 2014-12-31 疯牛窗=wild∧bull 共存=非同构；vol spike 常伴趋势翻面但 2014 单边牛 wild 亦高发）——双门交互=新可检空间（谁付出代价：calm 面入场者由 wild 面追逐彩票收益者付出·外源四解释链迁移假说·方向先验两向殉死如实）。
- **D6 同族相关性准入（W1 大考面适配声明整体沿用）**：批内候选两两 corr 矩阵全量计算（去重门前置级）；①≥0.999 塌缩=生成段硬绑门（②）；②0.7 线在注册级=全候选审计披露（逐格 max|corr| 列），注册生效判定=s4 intake（≥0.7 拒收·存活者簇内行缩留最优）；批内 0.7-0.999 中带=锚标涨选面，非准入门。
- 排除簿（anti-dredging·W1/W2/W3 同例·**七源**）：**已判精确核（正负了然）禁重跑**——cell key=(template, params, axis_config, initial_stop, gate, vol)；**语义恒等匹配=前波 cell key 无 vol 轴者按 vol=none 补全类匹**（gate=g·vol=none 面=该前波格全等）；全部既有已判格（含与在册已判产物全等（注册公判配置）·judged 产物 declare 窗 generate 时点实读四源·判负函数默认参数原批）+**W1_screen 存活清单 149+W2_screen 存活清单 404+MASS screen 存活清单 166+W3_screen 存活清单 513**（四清单 generate 时点实读消费）→ 生成段排除并逐格留痕；**vol∈{calm,wild} 面（与任意 gate 组合）为新语法面合法开法**。本波新 prereg+新语法（轴系×止损面×政体门×波动门×Sobol），符合 RANDOM_LARGE_SAMPLE_LAW §5 唯一合法重试通道。

## §2 数据与面板。【跑前探针事实，非结果。】

- 宽基/池：**core48**（ETF 交易线季风域·在册公判注册域；loader=引擎 T-22/T-34 血统 import-face 复用禁重写）+ 判决段深轴 **T-18 增长截面深面板**（Money02 t18_deep_panel cache 只读·WILD-S1/KLINE 只读先例禁写）。
- **VOL 门序列（本波新增面 a·跑前探针事实 r396 实读）**：510300 在 core48 面板在位（data/daily/sh510300.csv·3,483 行·2012-05-28→2026-09-22 cutoff 冻结）——ret(d)=close(d)/close(d-1)−1；vol20(d)=ret 滚动 20 bar 样本 std（ddof=1·min_periods=20·含 d）；med500(d)=vol20 序列滚动 500 观测中位（min_periods=500·全 ≤d 信息集）；**med500 首有效=第 519 bar=2014-07-17→vol-closed NaN 窗=519 bar（calm/wild 面禁入场诚实披露·none 面不受影响）**；开窗态分布 **calm 1,523 日/wild 1,441 日（51.4%/48.6%）**；七极端日（2015-07-27/2016-01-04/2024-02-28/2024-09-24/2024-09-30/2025-04-07/2026-01-19）探针全=wild；2014-12-31=wild∧（若按 GATE 判=bull）=VOL 面≠GATE 面非同构实证。探针代码=results/_r396bma_volgate_probe.py 留痕（探针事实面非结果面）。
- **GATE 门序列（W3 冻结定义整体继承）**：510300 close(d) vs MA200(d)（min_periods=200·首 199 bar NaN→bull/bear 面gate-closed 诚实）；GATE 态在**信号日 d 收盘**信息集上判定，入场=d+1 开盘（T+1 因果律·与信号同信息集零前瞻）。
- **evidence_cutoff=2026-09-22（P-5C 冻结口径 binding·双轴同降）**：整体沿用 W1 §9.3/W3 机械——**import `scripts/p5c_virtual_timepoint.py` 冻结口径禁重实现**：初筛面=leg-L 6m 面 census 限=FROZEN_CENSUS["L"]["6m"]=**1,253**；判决面=双腿窗口 {6m,12m,24m} 全网格逐面==FROZEN_CENSUS 对应窗值（L 1253/1127/875·D 3104/2978/2726）；被动=模块 passive_rel/passive-cell 机械。T-ANCHOR 一致律：live.paper 锚定门常数 cutoff=2026-09-22 与本批 binding 同锚=锚门复放语义自洽。Cutoff 后新 bar 锁定不得回流本批；结果 JSON 顶层必带 `science_gates.cutoff_meta("2026-09-22")`（缺字段=C2 VIOLATION）。
- 数据完备门（fail-closed，不过即 VOID 中止零产出）：
  - **G-PANEL**：core48 48/48 员每员 ≥60 行·截断后末行日期==2026-09-22 逐员唯一·OHLCV 列齐；
  - **G-CENSUS**：P-5C FROZEN_CENSUS 逐面实读断言（L/D×{6m,12m,24m} 六键逐位；import 实读禁手抄）；
  - **G-ANCHOR**：在册六员工注册配置经本波 grammar 引擎默认路线（template_default+EW+daily+initial_stop=none+gate=none+vol=none）重放，IS/OOS Sharpe==live.paper 锚定门常数（import 实读禁手抄；不等=基线漂移 VOID）；
  - **G-MANIFEST**：深轴 manifest verdict==PASS（48 员 twin cache 可核路·W1 §9.3 manifest_note 先例·**冻结时实读**=trial_labor_w3 judge_state g_manifest PASS/48 员在册·跑时以活值为准）；
  - **G-EXCLUDE**：已判格排除清单装载（七源）+命中计数披露（排除 0 合法·排除 0 如实）；
  - **G-VOL**（本波新增）：vol20/med500 序列点时完整性断言（med500 首有效 bar-idx==519·calm/wild 计数=={1523,1441} 探针锚定·截断后末行==cutoff）。**锚面定义四元组【G-ANCHOR-FACE·O-20260928-1712】**＝数据面路径 `data/daily/sh510300.csv`（git-tracked 原始全史成员件·非 W1-floored `load_core` 池面 2020-01-02 起）＋加载函数 raw `pd.read_csv` 直读截断 cutoff（runner `_vol_face_full` 同面）＋起算窗 2012-05-28 全史（3,483 bar）＋预热窗 vol20 min_periods=20→med500 min_periods=500（首有效第 519 bar）——探针加载路径≠锚声明路径=配置错配 VOID（报「面错配」非「数据腐坏」）。

## §3 方法论。【冻结。】

- **生成语法（全冻结——零新信号发明——候选只从冻结规则原语组合生成）**：
  - 原语面：策略工厂 `strategies/` 86 函数/13 模块（W3 同源计数·跑时以 import 实测为准如实披露）；时 A=在册六员工模板（low_vol_long/composite_top5/composite_top8/engulf_reversal/needle_probe/vol_drought_reversal）；时 B=其余工厂函数 76（86≠76：grid 模块 4 亦业务函数排除——GRID 线专用判决线机械不可入通用语法表达，W1/W2/W3 同例如实披露）；函数-参数空间=各函数签名参数冻结值域表（runner build 时逐函数枚举值域表随 w4_grammar.json 序列化冻结=W1/W2/W3 同款）。
  - 轴系（REFINE_BENCH_LAW §2 标准轴·W3 全轴系继承+本波扩容面）：入场过滤 ∈ {none, depth_thresh, amplitude, liquidity, trend_slope, dual_window, fundamental_mask}（7）；出场 ∈ {template_default, CE 注册出场, time_stop_5d/7d/10d/20d, trailing_stop, profit_ladder}（6）；仓位 ∈ {equal_weight, inverse_vol, cap20, regime_delever}（4）；时机 ∈ {daily_signal, weekly_grid}（2）；初始止损叠加 ∈ {none, p3, p5, p8, p12, a15, a20, a25}（8·W2 面沿用逐字继承）；**政体入场门 GATE ∈ {none, bull, bear}**（W3 面沿用逐字继承）；**波动率入场门 VOL ∈ {none, calm, wild}（本波新增面 a·§2 冻结定义）——七元组 R/X/S/T/STOP/GATE/VOL = 32,256 轴组合/模板**（W3=10,752·W2=3,584·W1=448）。
  - **VOL 门叠加层（扩容面 a·冻结定义）**：门态在**信号日 d 收盘信息集**上判定（vol20(d) vs med500(d)·§2 序列）；**calm**=仅 calm 态许入场；**wild**=仅 wild 态许入场；**none**=无门（W3 语义基线）；门只作用于**入场许可**（有效信号置零·MSG-0440 E1 映射先例·grammar 层实现），出场逻辑零改动；vol20/med500 NaN 窗（首 519 bar）→calm/wild 面 gate-closed 诚实（禁入场如实披露）；vol=none=W3 语义基线面。MA200 门（GATE）与 VOL 门独立叠加（双门=两条件交）。
  - 随机抽样（Sobol 沿用=W3 declare 血统）：**import-face 复用 MASS_TRIAL_W1 sample_draws 范式禁重写**——`scipy.stats.qmc.Sobol(参数维, scramble=True, seed=SEED_BASE+family_idx)` 归一化参数盒低差异 draw+轴组合独立 RNG 流（`default_rng([SEED_BASE+family_idx, 7919])` 整数轴抽轴；**本波 VOL 轴并入=七元组 R/X/S/T/STOP/GATE/VOL**）；N=500/时 A（模板轮转确定性指派）+4,500/时 B（76 函数轴转）；**seed 基 `trial_labor_w4_gen`=20289500**（派生 Sobol seed 20289500+family_idx，A 时 idx 0-5·B 时 idx 6-81；轴 RNG 流 [20289500+family_idx, 7919]；零带占用·重跑字节恒等；SEED_REGISTRY 本冻结同 commit 登记律·R250 一步例）。
  - **去重门（T-84 s3 组合恒等塌缩律·强制；W1/W2/W3 同例）**：①持仓恒等指纹=sha256(逐再平衡日持仓 sorted((sym, round(w,4))) 全串)；②候选日收益序列两两 |corr|≥0.999→塌缩为一格（保留代表=确定性最低 candidate_id；原始变体入 audit 段全量保留）；**塌缩计数+保留/淘汰清单如实披露**；判读与账本按塌缩后格数计。
- **s2 廉价初筛（TRIAL_LABOR_LAW §2）**：每 distinct 候选 legacy 轴 leg-L 6m 全史一回测（W1 13bp base 面·T+1；初始止损面与政体门面/波动门面随格携带）。→ beat6m=1,253 虚拟起点中「候选 6m 前向收益≥同窗为动」比例（完整窗生存·partial 窗计数如实披露）。
- **初筛 null 族**：K=200 同构随机信号候选（模板腿→随机信号日生成器；轴腿+初始止损腿+政体门腿+**波动门腿**同网格同参数空间 draw·同引擎同成本同面板——BACKTEST_PLAN 三铁律）；**seed=`trial_labor_w4_scrnull`=20290000**（派生 `[20290000, i]`·同 commit 登记律）。
- **初筛判线（跑前写死）**：**存活 iff beat6m > null 族 p95**（程序冻结·零手挑阈·数据自适应刻度）；两项参照（α=0.5·n=1,253）；逐格披露 b/p 值。初筛=漏斗阶段非判决（零注册效力·存活者仅获判决面入场券）。
- **s3 全量判决（存活者·TRIAL_LABOR_LAW §2/§3）**：双腿（P-5C 格 L/D×{6m,12m,24m} 起点）×成本面 {base x1, x2=CostPatch(2.0)（T22 Erratum-1 multiplier 律·禁直引 COST_X2_RATE）}×政体分段 bear/bull/chop+na（T-22 §3 冻结 3-way proxy 逐字）×**双 nulls**（RANDOM_LARGE_SAMPLE_LAW §3）：block bootstrap **B=2000**（block=20 交易日循环块·拼样截回 n 长）+ sign-flip 置换 **P=2000**（逐日符号独立翻转·双侧）；**seed=`trial_labor_w4_unc`=20290500**（派生 `[20290500, cell_idx]`·同 commit 登记律）；rng 流仅限两重采样面禁挪用（census §9.1 用途钉死先例）。**注**：GATE/VOL 门=策略构造面（入场许可），政体分段=判决披露面（分段归因）——两面季交不冲突（分段恒带 TRIAL_LABOR_LAW §3 律）；**双门面新增披露列=gate×vol 交互分段计数**（gate_flip_days_legL 同 W3 §5.6 面翻面计数口径族·面板级非逐格发明口径）。
- **样本充足律**：n_eff≥100 起点 × bear/bull/chop 三段各 ≥100 起点窗（na 桶诚实）——不越→verdict=**insufficient-sample 禁判 pass**。
- 描述条款（批级披露不替代 v2 门）：年化 0·OOS(2025+ 恒盲)双正·回撤 ≥−35%·无崩年·x2 面逐字稳定。
- **成本口径**：W1 legacy 引擎面（13bp·T+1·退出优先级冻结禁改）；x2 压测面——与在册锚定/注册判读链同源可比（注册面一致性优先）。
- **账本**：`science_gates.append_ledger("TRIAL_LAB_W4_SCREEN", <distinct 候选+200>, file, evidence_cutoff="2026-09-22")` + `science_gates.append_ledger("TRIAL_LAB_W4_JUDGE", <存活者数>, file, evidence_cutoff="2026-09-22")`（prev=数据驱动锚头实读禁手抄）。

## §4 判据。【跑前写死——禁看结果调整；共享库引用零手抄。】

- **G1' v2 = `science_gates.g1_prime_v2(sharpe_full, returns, batch_cells, pool="core48", n_trades, n_entries)`**：全期 Sharpe>skill_line_v2（数据审动线 max(被动+0.10, μ_null+σ_null·√(2·ln N_eff))·N_eff=活链头本批格数）**∧**平稳 bootstrap CI 下界>0 **∧** entries≥30（G6 双口径 entries_ok 为准）；批报告逐列披露 skill_line/bootstrap_ci/trade_gate 全输入。
- **G2 注册资格 v2 = `science_gates.g2_registration_v2(g1_pass, dsr, pbo)`**：G1' 过线 **∧** DSR≥0.95（`deflated_sharpe_ratio` 原始收益跑·**n_trials=累计账本总试验数**（活锚头实读·**跨波不重置**·TRIAL_LABOR_LAW §4——**r396 冻结时实读 301,180**（live head=trial_labor_w3/w3_screen.json trials_ledger.total·三判决面落地后随之增·跑时以活值为准）+本波 SCREEN 格并入后折减；禁 dsr_from_stats 充数）**∧** 审慎 PBO≤0.25（`screening/pbo.py` CSCV 8 块·**族=策略模块**（grid 业务模块=n/a）·族内全部波内候选/全史 base 面 Sharpe 向量=同机竞争网格 g25_retro 先例；模块数不足 8=insufficient 如实→G2 不可过）；缺输入诚实拒收（missing_inputs 机制）。
- **波级多重检验税披露（O-2245 强制·护栏随 N 加码）**：①N_wave=SCREEN 核+JUDGE 核逐批披露；②**E[FP]=0.05×N_wave_judged_cells** 如实披露（DSR≥0.95 门即多重检验校正门·通过者仍存活非否定面）；③波级 PBO 聚合读数另列（跨族）；④**语法消耗登记簿**（research/TRIAL_GRAMMAR_LEDGER.md·append-only）落 wave-4 行（grammar sha16+w4_grammar.json 序列化时点 raw/dedup 计数+seeds+consumed 时刻）——**同语法禁重跑**（防疏浚·TRIAL_LABOR_LAW §4）。
- **s4 intake（上岗线·O-2245 中 3）**：G2 eligible 存活者 → **D6 绑定门**（对在册公判+存活者两两 max|corr|·日收益口径=sleeve-tag 先例；≥0.7 拒收·存活者簇内行缩留 DSR 最高者（平手=最低 candidate_id））→ STRATEGY_LIBRARY 注册行（带 evidence_cutoff+SIGNAL_BUILDERS 接线+smoke 锚定门复跑·模板 §8 律）+ **TRIAL-<FAMILY>-<NN> 袖盘上岗**（O-2045 PROSPECT 机械复用·观察车道）+ **48h 内 CEO 呈报**（判决面落地起计）。**实际存活数按实际划（零存活=合法判决照报不翻案）**。

## §5 跑前预测。【写死于跑前·≥3 条·含极端日先验。】

1. **去重率**：raw 5,000 → distinct ∈ [2,800, 4,600]（W3 实弹缩 29% 基线；本波 vol∈{calm,wild} 占 2/3 新空间摊低跨波重复·vol=none 面 re-sample W3 空间部分已被七源排除簿拦截→缩率预期 [8%, 44%]）。
2. **null 底与初筛通过率**：null 族 beat6m 中位 <0.50（成我方摸索方向·W1/W2/W3 同向）；p95 ∈ [0.42, 0.62]（W1/W2/W3 三波同带 0.5116）；初筛存活率 ∈ [2%, 15%] → 存活 [100, 750] 格。
3. **判决面**：G1' 过线 [0, 60]；**G2 eligible [0, 5]——模态结局=零或近零**（DSR 按累计 N≥301k+ 折减=极重校正·五批判决同门实证；零存活=合法产出如实报）。
4. **VOL 面方向先验（本波新增面·方向可证伪）**：**calm 面存活率 ≥ none 面 ≥ wild 面** 预期（低波异象跨截面证据方向迁移·Who 支付=彩票偏好/杠杆约束者；**迁移不保证成立——跨截面≠时序·Moreira-Muir 时序面正文未取=无直接外源锚**→读数如实两向殉死）；面占比 calm/wild 近半开（51.4%/48.6%）→面样本充足性结构性占优（vs GATE bull 面策反极端稀缺）；**GATE×VOL 交互=开放面无外源直接证据**（双门叠加增益是否存在=本波真问题·读数非先验）。
5. **极端日先验（硬界三件套 c·D-20260925-01①）**：本波数据窗内处在极端微观结构日=2015-07 股灾（宽基单日 ±9~10%）、2016-01 熔断、2024-02 微盘崩、2024-09-24/09-30 政策脉冲（宽基单日 +10~20%）、2025-04-07 外生缺口、2026-01-19 极端缩量日——候选格曲线尾部|日收益|>8% 层级在场真值非腐坏；**VOL 门新增披露**：七极端日探针全=wild（§2 实读）→wild 面入场敞口在危机日集中→**整窗判读+dd 线非单点 max 检测线**→极端日经整窗路线径内化**无豁免路径需求**；危机日计数+止损触发日计数+**门面（gate×vol）计数列随格披露**。

## §6 产物

- runner：`scripts/trial_labor_w4.py`（subcommands: generate / screen / judge / intake / status / selftest；import-face 复用 trial_labor_w1.py 锚枚举/装载/锚门/包裹原语+trial_labor_w2.py 初始止损叠加层+trial_labor_w3.py 政体门叠加层与双门机械+mass_trial_w1.py Sobol sample_draws 范式+strategies/ 工厂+engine/backtester 引擎腿禁重写要改；selftest=hermetic 合成面离线腿（r116 律 B7b 合约腿+r297 律确定性双跑字节恒等腿）+**VOL 门因果腿**（信号日信息集·NaN 窗 gate-closed·vol=none==W3 语义基线恒等腿）+**双门交叠腿**（gate×vol 两条件交正确性）+**门序列点时完整性腿**（G-VOL 探针锚断言）；**初始止损+政体门+波动门叠加=grammar 层实现，engine/exit_rules.py 零触碰**）。
- 产物：`results/trial_labor_w4/`——w4_grammar.json（语法全套：函数-参数值域表·轴网格含止损轴+政体门轴+**波动门轴**+去重审计段）；w4_candidates.json（全量候选 provenance+D6 披露列+止损面序列+政体门面序列+**波动门面序列**）；w4_screen.json（null 族 floor+全格 beat6m 分布·零候选选择性披露·VOL 面+GATE×VOL 交互分段存活统计）；w4_screen_cells.csv（小件入 git）；w4_judge.json（判决全面 G1'/G2/DSR/PBO/E[FP]·双门交互分段披露）；w4_intake.json（上岗 D6 裁定）；全部顶层 evidence_cutoff+audit 段。
- 语法消耗登记簿：`research/TRIAL_GRAMMAR_LEDGER.md`（append-only·wave-4 行：语法 sha+raw/dedup 计数+seed+消耗时点）。
- 池路由：SCREEN/JUDGE 批 >5min 入池（O-2100）；**lane_owner=null**（core48+T-18 in-repo 双机可跑·judge 面 cache-less 机 in-runner exit 2 诚实=W1/W2/W3 先例）；workers_plan ≥floor(核数/0.8) BelowNormal；RAM 门禁 r354 三采样例（池条目 data_gates 注记）；**CPU 排队=池优先序自主调度**（当前在飞=门后批：W2B census bm-b 烧+四判决面 RAM 门后合法排序票内留痕）；**W4-JUDGE 序门=排在既有判决面后（§0）**；§9 交接窗下。

## §7 跑后实证。【跑后一次定稿回填·占位纪律解除。】

**【2026-09-29 09:3x 一次定稿回填·bm-b r417（T-119 五波漂移债清偿）·数字真值源=results/trial_labor_w4/*.json】**

- **漏斗**：raw 5,000 → distinct **3,810**（塌缩 23.8%）→ 初筛 4,010 格（3,810+200 null）→ 存活 **461**（12.1%）→ 全量判决 461 格 → **G1' 0/461**（最佳 W4-A-0174 Sharpe 1.1059 vs 判线 skill_line_v2=1.1901·n_eff=321,408——零过线）→ **G2 0** → 上岗 0（lawful-zero）。账本 301,180+4,010=**305,190**（SCREEN 收官）→ 317,398+461=**317,859**（JUDGE 收官）。
- **判决面**：null 族中位 0.4940·p95=0.516441；E[FP]=0.05×461=**23.05** 如实披露；族 PBO：patterns 0.7429（108 格）/ta 0.4286（72）/composite_rotation 0.5571（25）/volatility 0.3429（36）/event 0.5（17）；描述条款：年化>0 361/461·OOS 双正 348/461·dd 线 459/461·无崩年 461/461（x2 461/461）。
- **VOL 门方向读数（§5.4 方向预测对账·零判据权重）**：分段存活 **wild 20.4%（260/1,273）>> none 10.7%（140/1,311）>> calm 5.0%（61/1,226）**——预测「calm≥none≥wild」**反向全倒 miss**（跨截面低波异象时序迁移**不成立**实证=W4 digest 边界披露(a)「迁移不保证成立」兑现·两向殉死律正行使例）；交互面 **bear×wild 35.9%（156/434）全场最高**·bear×calm 3.8%（15/400）最低——W6 §7「bear/wild 富集读数三波复现」溯源于此。
- **§5 预测对账五条**：①distinct 3,810∈[2,800,4,600] ✓（缩 23.8%∈[8%,44%] ✓）②null 中位 0.4940<0.50 ✓（近缘）·p95 0.5164∈[0.42,0.62] ✓·存活 461∈[100,750] ✓（12.1%∈[2%,15%] ✓）③G1' 0∈[0,60] ✓·G2 模态零 ✓（G1 零过线=首次全零波如实）④VOL 方向 **miss 反向全倒**（上注）⑤极端日先验=载体律 ✓（七极端日探针全 wild·wild 面危机日敞口集中实证·整窗判读+dd 非单点）。

## §8 批后复盘。【必填 §7-T·r417 回填。】

**【回执 2026-09-29 bm-b r417（T-119 漂移债清偿）】**attrition 损耗账两行（TRIAL_LAB_W4_SCREEN 4,010+TRIAL_LAB_W4_JUDGE 461）原落地窗未落=漂移债第二面，r417 补录（gate_attrition history+bm-b 车道双写·原事件时戳 2026-09-28 13:12:31/20:03:05+backfill 注记）；判线 v2 当批读数 skill_line_v2=**1.1901**；零新注册员（G2=0）；48h CEO 呈报=CEO-REPORT-WAVE2-5-20260929.md（W4 判决落地 09-28 20:03→窗止 09-30 20:03 提前 ~40h）+r417 纠偏附录（六波总 G1' 18 非 14·0 录用不变）；轮报告+CODELY.md 行级追加 r417 同轮。

## §9 追加冻结节。【append-only·每 sub-wave 一冻——禁跑前另立冻结。】

- **W2-C 族面交接注记（anti-dup）**：因子普查存活腿族（census fusion legs）=TRIAL_LABOR_W2_PREREG §9.1 declare 的 W2 when-ready 子波独占面（问 W2A+W2B 双 finalize+roster 导出+§9.2 append-confirm）——**本波 §0 declare 禁碰**；W4 未来并入该供给=待 W2-C 消费落地后另发 declare（TRIAL_LABOR_LAW §5 律）。
- **judged 供结 generate 时点 declare 窗**：四判决批（W1/MASS/W2/W3）落地后、本波 generate 跑前=§1 (d) 面加权 declare 窗（实读产物并表·逐源行数披露）；generate 已跑后落地者不入本波（禁事后改配）。
- **s3 判决面**：已冻结于 §3（W3 结构同构·无需另立 sub-wave 冻结）；若跑前需修栈=零跑修档先例（r251/r280·如实留痕非结果驱动）。
- **G-VOL 锚面定义四元组修正（O-20260928-1712 G-ANCHOR-FACE 律·changelog·r251/r280 零烧窗修档先例第三例）**：性质=面定义澄清**非判据放宽**——锚值 {519, 1523, 1441, n3483} 与 r396 探针事实逐位不变（§2 原文语义=raw 全史面）；runner 探针同面断言（`_vol_face_full` raw 成员件直读·非 `load_core` 池面）r381 已落地并生产实证（W4-GENERATE+screen-prep PASS 12:30:56 G-VOL raw re-verified·零引擎格重烧）；修正时点=SCREEN 池 entry 已开未烧、JUDGE 序门在后=跑前修档零烧窗合法（同 r251/r280 amendment-driven not result-driven 例）；收口对象=INCIDENT-20260928-cpu-idleness R3（10:08 bm-a r398 锚面刻度错配拒烧事故）。
