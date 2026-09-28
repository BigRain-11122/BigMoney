# TRIAL_LABOR_W6_PREREG —— T-99 千人试用期大考 wave-6 波级预注册（MASS CANDIDATE TRIAL PROGRAM 第六波·5000 人量能确认门）

> **【状态：DRAFTED——起草完成·冻结挂起·bm-a r410】**本件前史=TRIAL_LABOR_LAW §1 常供律例行供给步（板空/池饿/无在飞判决批=默认起草下一波·U222 禁待命）；**冻结触发器（未满足）**=W5 全链消费落地（TRIAL-LABOR-W5-JUDGE judge-finalize 落地·w5_judge.json 产物+ledger TRIAL_LAB_W5_JUDGE append·48h CEO 呈报钟起计）**∧ 判官零在飞批**（W5 r405 冻结步同构先例：W4 全链消费落地·judged 461 cell 判定件在册·判官零在飞）；冻结步=commit 冻结+SEED_REGISTRY 三键同 commit（R250 一步律）+波级票开票+同轮认领（O-1730）+F-04 MSG 声明。**冻结时点前本件零烧批效力**（fill_ladder prereg_frozen 门拒 draft 头先例在册）。
> 模板=research/PREREG_TEMPLATE.md（§0-§8 全节）；跑前 commit 冻结；跑后只回填 §7/§8，要改判据要重跑。
> 令源：CEO 直令 O-2026-09-27-2245（千人试用期大考）+ O-2026-09-27-2250 常设律（firm/TRIAL_LABOR_LAW.md v1.0「以后不要我提醒」）+ O-20260928-1522（CEO 研究导向：国内民俗判据优先立项·科学照常验证）；波级票=冻结步开票（W5 先例 T-2026-09-29-114）；TRIAL_LABOR_LAW §1 常供律起草面无门禁任意轮可开=W2-W5 同例；**W6-JUDGE 面=RAM r354 三采样门后排在 W5-JUDGE 与其余在飞判决面之后（序门留痕=物理依赖合法暂缓事由·bm-b r369 裁定族）**；起草/生成/初筛三面=CPU 池面零 RAM 占用合法。
> 统摄律：firm/RANDOM_LARGE_SAMPLE_LAW v1.0（判决面）+ firm/REFINE_BENCH_LAW v1.0（轴系）+ TRIAL_LABOR_LAW §1-§6 + research/BACKTEST_SCIENCE.md v2（判据唯一权威）+ BACKTEST_PLAN.md 三铁律 + COMPUTE_AUDIT.md 批件纪律 + **O-1820(3) consumer_plan 池 schema 必填律（bm-c r193 落地·autofill submit 断面）**。
> **本件=波级（Wave-level）预注册**：生成语法/漏斗规则/判据全冻结；sub-wave 追加面一律走 §9 append-confirm（每 sub-wave 一冻结），要用本冻结面跑追加法必须另立。
> **本波≠W1/W2/MASS/W3/W4/W5 语法血统**：新语法面=**量能确认门 VCONF ∈ {none, volume_surge, volume_dry}** 叠加层（扩容面）→ **新语法新 sha16**（≠W1 a2fa15f4b06b3c40 ≠MASS 96269ebe766c3fc2 ≠W2 1dd3d9579235cec ≠W3 cc59eab79db53436 ≠W4 d498e9343ee57460 ≠W5 29720178c39425de；W6 sha=w6_grammar.json 序列化时点新算·构造性相异），同语法禁重跑（TRIAL_LABOR_LAW §4）经新语法面合法开法。
> 外源证据链（借力律 O-1721 先扫后研）：research/digests/DIGEST-20260929-w6-volconf-supply-scan.md（GKM 2001 高量收益溢价弱直接锚+A 股量价民俗口诀族〔方向矛盾如实=条件化门价值非方向宣称〕+仓内三源主证+门裁定 PASS+边界三披露）。**主证供给源=TRIAL_LABOR_LAW §5「外源收割 digest」明列通道+仓内时序门普查量族先验（O-1855④ VSTD20_q20 中位 t=+1.746·61% 工具 |t|>2·ETF 宇宙正信号在册）**。

## §0 批件身份。【跑前。】

- 批名/批号：**TRIAL_LABOR_W6**（千人试用期大考·wave-6·5000 人量能确认门）。三层漏斗子批（dict schema 唯一）：
  - **TRIAL_LAB_W6_SCREEN**（s2 廉价初筛批）：batch_trials = 去重后候选数 + 200 null（每格 1 trial）；raw 5,000 → 去重门后 ≥3,000 distinct —— **5,000=上限非金数指标**（语义重复无效人不计数·造数凑烧禁例）；
  - **TRIAL_LAB_W6_JUDGE**（s3 全量判决批）：batch_trials = 初筛存活者数（judged cells；双 nulls=B/P 重采样面非 ledger +0·census §9.2 NAV 推导面先例）。
  - 两批 evidence_cutoff 均 **2026-09-22**（P-5C 冻结口径 binding·双轴同降·W1 §9.3 零跑修档整体沿用）。
- 认领：**起草面无票无认领（本 draft）；冻结步开票+同轮认领**（W5 先例 r405）；认领依据=TRIAL_LABOR_LAW §1 常供律例行供给步，无需 GM 另署名 per T-96/W2/W3/W4/W5 先例。
- 部门归属：dept:策略（生成引棒供给面）+ dept:研究（判决漏斗面）joint（票面 note 同 W1-W5）。
- 算力预算：生成去重=零（分钟级单机·76 函数值域表枚举 5,000 抽样）；初筛面 ≥5,200 格量级（≥3,000 候选+200 null；leg-L 6m 全史引擎回测——W1 O-2245 生产力账 ~28s/候选单核+W3 实弹 3,752 格 4.6min 池批实证）→ **估分锺级-小时级池批 @ ≥floor(核数/0.8) workers 池批**（>5min 一律入 results/runnable_pool.json·O-2100 执行面分离；每 50 候选一 checkpoint 断轮续跑·R41）；判决面=分钟级簇（双 nulls 重采样重量级·deep-panel 宿主物理腿=RAM 门）。
- **供结契约如实披露**：A=在册六员工模板族 500 抽（常供线维护面）；B=流派战法模板大考 4,500 抽 → 76 函数均摊 ≈59.2 抽/函数（与 W2-W5 同口径·六波面累计 ≥22 抽/函数下限沿 W5 五波面口径）；C=因子普查存活腿族=**本波禁碰**（W2 §9.1 declare 与 W2-C when-ready 子波独占·anti-dup hard law；W6 如需并入=待 W2-C 消费落地后另发 declare）；D=judged 供结变体面=**generate 时点实读 declare 窗**（W1-JUDGE+MASS judged+W2-JUDGE+W3-JUDGE+W4-JUDGE+**〔W5-JUDGE 若已落地〕**六源逐源 declare 不可得零行如实——**起草时点 W5-JUDGE 池 ready 未烧=bmr404 flip 02:5x 后 bm-b autofill 待点火=本起草 declare=零行如实**；generate 跑前重读 live prev 增量并入加权 declare，W2-W5 同门先例）。**48h CEO 呈报钟**：随判决面落地起计（judge-finalize 后 48h·票面持有；非本起草时点计）。
- **W6-JUDGE 物理序门（bm-b r369 裁定族·票内留痕）**：判决面排在 W5-JUDGE 与其余在飞判决面（V3-TOURNAMENT bm-b 车道等）之后（RAM r354 三采样门+串行 flip 既有纪律自动实现）；SCREEN 面=CPU 池面先行烧合法（RAM 零占用）。
- **consumer_plan（O-1820(3) 池 schema 必填·冻结步起生效）**：W6 产物消费面=TRIAL_LAB_W6_JUDGE verdict 面（G1'/G2/DSR/PBO 判定件）→ s4 intake（D6 绑定门→STRATEGY_LIBRARY 注册行+TRIAL-<FAMILY>-<NN> 纸盘上岗）→ 48h CEO 呈报面+scorecard/CEO 一页纸消费；SCREEN null p95=下一波 prereg 判读参照带（W1-W5 同例 0.5116/0.5164 带内延续）。

## §1 伪 α 机制段。【四选一+论证·D6 门槛。】

- **供给时 A（在册六员工模板精炼）**：[x] 行为偏差（主）——风险源价（辅）——母体机器同承继 W1-W5 §1（VOLATILITY-CE-01 低波风险源价/COMPOSITE 复合源价/ENGULF·NEEDLE·DROUGHT 确认性行为反转+首阳确认层）。本波主张：**信号日量能确认条件下存在可检出新增益变体**——「量增价涨才靠谱」=A 股量价民俗判据族核心口诀（CEO 1522 导向：国内打法优先立项·民俗判据形式化为数值门正例）：信号池溢价由「放量确认日入场者」向「未确认（缩量）日入场者」收取；**代价支付者=低参与度信号日的先入场者**（可见性缺失日=注意力/承诺人群缺席·GKM 2001 visibility 机制的行为面镜像；「谁付出代价」答案）。
- **供给时 B（流派战法模板大考）**：[x] 逐流派四选一映射同 W1 §1（21 流派·工厂批次血统；负先验标签如实随格携带、漏斗重仓复置不预筛）。本波主张：**冻结工厂库在 Sobol 低差异抽样轴系下、政体门×波动门×阳线门×量能门×初始止损×轴系交互存在仅大规模混水摸深抽样可检出的 α 口**。
- **量能确认门机制注记（本波新增面·冻结定义）**：VCONF=入场许可的条件化叠加层（非引擎出场规则——时机归 ENGINE 心律）——**行为确认过滤面**：信号日成交量相对近 20 bar 中位的状态（放量=参与确认/缩量=参与缺席）。**VCONF 面≠GATE 趋势面≠VOL 波动面≠YANG K 线面**（探针实证：GATE 态几乎不载 surge 率〔bull 49.66%/bear 50.89%〕、VOL 态几乎不载 surge 率〔calm 50.76%/wild 49.87%〕=第四独立条件维；VCONF×YANG 交叉四格全非空非支配〔924/819/817/904〕=价量同动结构事实非同构面）——**四门交互=新可检空间**（谁付出代价：缩量日入场者由放量日入场者付出·行为假说·方向先验两向殉死如实·外源 GKM 2001=美国个股截面月窗口径错位弱直接锚如实）。
- **D6 同族相关性准入（W1 大考面适配声明整体沿用）**：批内候选两两 corr 矩阵全量计算（去重门前置级）；①≥0.999 塌缩=生成段硬绑门（②）；②0.7 线在注册级=全候选审计披露（逐格 max|corr| 列），注册生效判定=s4 intake（≥0.7 拒收·存活者簇内行缩留最优）；批内 0.7-0.999 中带=锚标涨选面，非准入门。
- 排除簿（anti-dredging·W1-W5 同例·**judged 六源 declare 窗+screen 六清单**）：**已判精确核（正负了然）禁重跑**——cell key=(template, params, axis_config, initial_stop, gate, vol, yang, **vconf**)；**语义恒等匹配=前波 cell key 无 vconf 轴者按 vconf=none 补全类匹**（gate/vol/yang=none∩vconf=none 面=该前波格全等）；全部既有已判格（judged 产物 declare 窗 generate 时点实读六源=W1/MASS/W2/W3/W4/W5·判负函数默认参数原批）+**W1_screen 存活清单 149+W2_screen 存活清单 404+MASS screen 存活清单 166+W3_screen 存活清单 513+W4_screen 存活清单 461+W5_screen 存活清单 372**（六清单 generate 时点实读消费）→ 生成段排除并逐格留痕；**vconf∈{volume_surge, volume_dry} 面（与任意 gate/vol/yang 组合）为新语法面合法开法**。本波新 prereg+新语法（轴系×止损面×政体门×波动门×阳线门×量能门×Sobol），符合 RANDOM_LARGE_SAMPLE_LAW §5 唯一合法重试通道。

## §2 数据与面板。【跑前探针事实，非结果。】

- 宽基/池：**core48**（ETF 交易线季风域·在册公判注册域；loader=引擎 T-22/T-34 血统 import-face 复用禁重写·tl1.load_core()）+ 判决段深轴 **T-18 增长截面深面板**（Money02 t18_deep_panel cache 只读·WILD-S1/KLINE 只读先例禁写）。
- **VCONF 门序列（本波新增面·跑前探针事实 r410 实读）**：信号日量能态=**volume(d) vs med20(d)**，med20=成交量序列滚动 20 bar 中位（min_periods=20·**含 d**）；**volume_surge=volume(d)>med20(d)**（放量确认）/**volume_dry=volume(d)≤med20(d)**（缩量）；判定在**信号日 d 收盘信息集**（T+1 因果律·与 GATE/VOL/YANG 同信息集零前瞻·入场=d+1 开盘）；**19 bar 预热窗 gate-closed 诚实**（med20 首有效 bar-idx==19——vs YANG 零预热/VOL 519 bar：结构性中间位如实注记）。510300 全史面（data/daily/sh510300.csv·3,483 行·2012-05-28→2026-09-22 cutoff 冻结·W4/W5 探针基同锚）：**零成交量行=0**（无退化面）；**surge 计数 1,741=50.26%**（3,464 可判日·近半开窗=面样本结构均衡；dry 1,723）；政体条件面 bull 49.66%（884/1,780）/bear 50.89%（857/1,684）；波动条件面 calm 50.76%（773/1,523）/wild 49.87%（968/1,941）；**K 线条件面 yang 53.01%（924/1,743）/red 47.47%（817/1,721）=价量同动不对称在册**；交叉表 yang∧surge 924/yang∧dry 819/red∧surge 817/red∧dry 904（四面全非空非支配）；**四门 16 格开窗计数全非空**（bull_calm_yang_surge 269…bear_wild_yang_surge 302/bear_wild_red_dry 298·区间 133-302=四门交互面可检空间实证）；**七极端日 6 surge**（2016-01-04 熔断 2.047x/2024-02-28 微盘崩 1.51x/2024-09-24 政策脉冲 3.212x/2024-09-30 5.058x/2025-04-07 外生缺口 7.78x/2026-01-19 极端量日 3.262x——**例外 2015-07-27=0.524x dry 停牌潮如实**）——vs W5 YANG 门 4 red 关/v4 VOL 门全 wild 开：**surge 面危机日敞口保持（与 VOL 互补同侧）、dry 面危机日结构性收敛（与 YANG 互补同侧）**；core48 员级 surge 率 min 45.83%/median 49.10%/max 55.27%（48 员全非退化·**load_core() 真实名册面=import 复用·非字母序近似**）。探针代码=results/_r410bma_volconf_probe.py+事实件 _r410bma_volconf_probe_facts.json 留痕（探针事实面非结果面）。
- **GATE 门序列（W3 冻结定义整体继承）**：510300 close(d) vs MA200(d)（min_periods=200·首 199 bar NaN→bull/bear 面 gate-closed 诚实）；GATE 态在信号日 d 收盘信息集上判定。
- **VOL 门序列（W4 冻结定义整体继承）**：vol20(d)=ret 滚动 20 bar 样本 std（ddof=1·min_periods=20·含 d）；med500(d)=vol20 序列滚动 500 观测中位（min_periods=500）；calm=vol20≤med500/wild=vol20>med500；NaN 窗（首 519 bar）→calm/wild 面 gate-closed 诚实。
- **YANG 门序列（W5 冻结定义整体继承）**：信号日阳线=close(d)>open(d)（二元·零预热窗）；判定在信号日 d 收盘信息集；first_yang=仅信号日阳线日许入场。
- **evidence_cutoff=2026-09-22（P-5C 冻结口径 binding·双轴同降）**：整体沿用 W1 §9.3/W3/W4/W5 机械——**import `scripts/p5c_virtual_timepoint.py` 冻结口径禁重实现**：初筛面=leg-L 6m 面 census 限=FROZEN_CENSUS["L"]["6m"]=**1,253**；判决面=双腿窗口 {6m,12m,24m} 全网格逐面==FROZEN_CENSUS 对应窗值（L 1253/1127/875·D 3104/2978/2726）；被动=模块 passive_rel/passive-cell 机械。T-ANCHOR 一致律：live.paper 锚定门常数 cutoff=2026-09-22 与本批 binding 同锚=锚门复放语义自洽。Cutoff 后新 bar 锁定不得回流本批；结果 JSON 顶层必带 `science_gates.cutoff_meta("2026-09-22")`（缺字段=C2 VIOLATION）。
- 数据完备门（fail-closed，不过即 VOID 中止零产出）：
  - **G-PANEL**：core48 48/48 员每员 ≥60 行·截断后末行日期==2026-09-22 逐员唯一·OHLCV 列齐（volume 列在位=VCONF 面物理前提）；
  - **G-CENSUS**：P-5C FROZEN_CENSUS 逐面实读断言（L/D×{6m,12m,24m} 六键逐位；import 实读禁手抄）；
  - **G-ANCHOR**：在册六员工注册配置经本波 grammar 引擎默认路线（template_default+EW+daily+initial_stop=none+gate=none+vol=none+yang=none+**vconf=none**）重放，IS/OOS Sharpe==live.paper 锚定门常数（import 实读禁手抄；不等=基线漂移 VOID）；
  - **G-MANIFEST**：深轴 manifest verdict==PASS（48 员 twin cache 可核路·W1 §9.3 manifest_note 先例·冻结时实读=trial_labor_w5 judge_state g_manifest PASS/48 员在册·跑时以活值为准）；
  - **G-EXCLUDE**：已判格排除清单装载（judged 六源+screen 六清单）+命中计数披露（排除 0 合法·排除 0 如实）；
  - **G-VOL**（W4 沿用）：vol20/med500 序列点时完整性断言（med500 首有效 bar-idx==519·calm/wild 计数=={1523,1441} 探针锚定·截断后末行==cutoff）；
  - **G-YANG**（W5 沿用）：yang 序列点时完整性断言（零预热窗 bar-0 起在位断言+yang 计数==1,751 探针锚定+交叉四格锚定 {yang∧bull 962, red∧bear 914} 下界+截断后末行==cutoff）；
  - **G-VCONF**（本波新增）：量能序列点时完整性断言（**零成交量行==0 断言+med20 首有效 bar-idx==19 预热窗锚+surge 计数==1,741 探针锚定+交叉四格锚定 {yang∧surge 924, red∧dry 904} 下界+四门 16 格全非空断言+截断后末行==cutoff**）。

## §3 方法论。【冻结。】

- **生成语法（全冻结——零新信号发明——候选只从冻结规则原语组合生成）**：
  - 原语面：策略工厂 `strategies/` 86 函数/13 模块（W3-W5 同源计数·跑时以 import 实测为准如实披露）；时 A=在册六员工模板（low_vol_long/composite_top5/composite_top8/engulf_reversal/needle_probe/vol_drought_reversal）；时 B=其余工厂函数 76（86≠76：grid 模块 4 亦业务函数排除——GRID 线专用判决线机械不可入通用语法表达，W1-W5 同例如实披露）；函数-参数空间=各函数签名参数冻结值域表（runner build 时逐函数枚举值域表随 w6_grammar.json 序列化冻结=W1-W5 同款）。
  - 轴系（REFINE_BENCH_LAW §2 标准轴·W5 全轴系继承+本波扩容面）：入场过滤 ∈ {none, depth_thresh, amplitude, liquidity, trend_slope, dual_window, fundamental_mask}（7）；出场 ∈ {template_default, CE 注册出场, time_stop_5d/7d/10d/20d, trailing_stop, profit_ladder}；仓位 ∈ {equal_weight, inverse_vol, cap20, regime_delever}（4）；时机 ∈ {daily_signal, weekly_grid}（2）；初始止损叠加 ∈ {none, p3, p5, p8, p12, a15, a20, a25}（8·W2 面沿用逐字继承）；政体入场门 GATE ∈ {none, bull, bear}（W3 面沿用逐字继承）；波动率入场门 VOL ∈ {none, calm, wild}（W4 面沿用逐字继承）；阳线确认门 YANG ∈ {none, first_yang}（W5 面沿用逐字继承）；**量能确认门 VCONF ∈ {none, volume_surge, volume_dry}（本波新增面·§2 冻结定义）——九元组 R/X/S/T/STOP/GATE/VOL/YANG/VCONF = 193,536 轴组合/模板**（W5=64,512·W4=32,256·W3=10,752·W2=3,584·W1=448）。
  - **VCONF 门叠加层（扩容面·冻结定义）**：门态在**信号日 d 收盘信息集**上判定（volume(d) vs med20(d)·§2 序列）；**volume_surge**=仅放量日（volume>med20）许入场；**volume_dry**=仅缩量日（volume≤med20）许入场；**none**=无门（W5 语义基线）；门只作用于**入场许可**（有效信号置零·MSG-0440 E1 映射先例·grammar 层实现），出场逻辑零改动；**19 bar 预热窗 gate-closed 诚实**（首 19 bar 不可判——vs VOL 519 bar/YANG 零预热：中间位如实注记）；MA200 门（GATE）与 VOL 门与 YANG 门与 VCONF 门独立叠加（**四门=四条件交**）。
  - 随机抽样（Sobol 沿用=W3-W5 declare 血统）：**import-face 复用 MASS_TRIAL_W1 sample_draws 范式禁重写**——`scipy.stats.qmc.Sobol(参数维, scramble=True, seed=SEED_BASE+family_idx)` 归一化参数盒低差异 draw+轴组合独立 RNG 流（`default_rng([SEED_BASE+family_idx, 7919])` 整数轴抽轴；**本波 VCONF 轴并入=九元组 R/X/S/T/STOP/GATE/VOL/YANG/VCONF**）；N=500/时 A（模板轮转确定性指派）+4,500/时 B（76 函数轴转）；**seed 基草稿泊位 `trial_labor_w6_gen`=20303500 / `trial_labor_w6_scrnull`=20304000 / `trial_labor_w6_unc`=20304500**（起草时点三步律预检已过：registry int 键全集盘点 20303xxx-20304xxx 零占用+新基首元素与全基互异+rg 全仓扫零命中〔2026-09-29 r410 实证〕；**冻结步依法复验**——W5 撞带重取先例在册，冻结时点若撞带=三步律重取+状态横幅注记）；零带占用·重跑字节恒等；SEED_REGISTRY 本冻结同 commit 登记律·R250 一步例。
  - **去重门（T-84 s3 组合恒等塌缩律·强制；W1-W5 同例）**：①持仓恒等指纹=sha256(逐再平衡日持仓 sorted((sym, round(w,4))) 全串)；②候选日收益序列两两 |corr|≥0.999→塌缩为一格（保留代表=确定性最低 candidate_id；原始变体入 audit 段全量保留）；**塌缩计数+保留/淘汰清单如实披露**；判读与账本按塌缩后格数计。
- **s2 廉价初筛（TRIAL_LABOR_LAW §2）**：每 distinct 候选 legacy 轴 leg-L 6m 全史一回测（W1 13bp base 面·T+1；初始止损面+政体门面+波动门面+阳线门面+**量能门面**随格携带）→ beat6m=1,253 虚拟起点中「候选 6m 前向收益≥同窗为动」比例（完整窗生存·partial 窗计数如实披露）。
- **初筛 null 族**：K=200 同构随机信号候选（模板腿→随机信号日生成器；轴腿+初始止损腿+政体门腿+波动门腿+阳线门腿+**量能门腿**同网格同参数空间 draw·同引擎同成本同面板——BACKTEST_PLAN 三铁律）；**seed=`trial_labor_w6_scrnull`=20304000**（派生 `[20304000, i]`·同 commit 登记律）。
- **初筛判线（跑前写死）**：**存活 iff beat6m > null 族 p95**（程序冻结·零手挑阈·数据自适应刻度）；两项参照（α=0.5·n=1,253）；逐格披露 b/p 值。初筛=漏斗阶段非判决（零注册效力·存活者仅获判决面入场券）。
- **s3 全量判决（存活者·TRIAL_LABOR_LAW §2/§3）**：双腿（P-5C 格 L/D×{6m,12m,24m} 起点）×成本面 {base x1, x2=CostPatch(2.0)（T22 Erratum-1 multiplier 律·禁直引 COST_X2_RATE）}×政体分段 bear/bull/chop+na（T-22 §3 冻结 3-way proxy 逐字）×**双 nulls**（RANDOM_LARGE_SAMPLE_LAW §3）：block bootstrap **B=2000**（block=20 交易日循环块·拼样截回 n 长）+ sign-flip 置换 **P=2000**（逐日符号独立翻转·双侧）；**seed=`trial_labor_w6_unc`=20304500**（派生 `[20304500, cell_idx]`·同 commit 登记律）；rng 流仅限两重采样面禁挪用（census §9.1 用途钉死先例）。**注**：GATE/VOL/YANG/VCONF 门=策略构造面（入场许可），政体分段=判决披露面（分段归因）——两面季交不冲突（分段恒带 TRIAL_LABOR_LAW §3 律）；**四门面新增披露列=gate×vol×yang×vconf 交互分段计数**（W5 三门面翻面计数口径族扩容·面板级非逐格发明口径）+MSG-0450 annex-1 止损披露面（触发/成交日计数+D+1 出场日 close-vs-open 偏离分布·W5 judge 切片已接线面沿用）。
- **样本充足律**：n_eff≥100 起点 × bear/bull/chop 三段各 ≥100 起点窗（na 桶诚实）——不越→verdict=**insufficient-sample 禁判 pass**。
- 描述条款（批级披露不替代 v2 门）：年化 0·OOS(2025+ 恒盲)双正·回撤 ≥−35%·无崩年·x2 面逐字稳定。
- **成本口径**：W1 legacy 引擎面（13bp·T+1·退出优先级冻结禁改）；x2 压测面——与在册锚定/注册判读链同源可比（注册面一致性优先）。
- **账本**：`science_gates.append_ledger("TRIAL_LAB_W6_SCREEN", <distinct 候选+200>, file, evidence_cutoff="2026-09-22")` + `science_gates.append_ledger("TRIAL_LAB_W6_JUDGE", <存活者数>, file, evidence_cutoff="2026-09-22")`（prev=数据驱动锚头实读禁手抄）。

## §4 判据。【跑前写死——禁看结果调整；共享库引用零手抄。】

- **G1' v2 = `science_gates.g1_prime_v2(sharpe_full, returns, batch_cells, pool="core48", n_trades, n_entries)`**：全期 Sharpe>skill_line_v2（数据审动线 max(被动+0.10, μ_null+σ_null·√(2·ln N_eff))·N_eff=活链头本批格数）**∧**平稳 bootstrap CI 下界>0 **∧** entries≥30（G6 双口径 entries_ok 为准）；批报告逐列披露 skill_line/bootstrap_ci/trade_gate 全输入。
- **G2 注册资格 v2 = `science_gates.g2_registration_v2(g1_pass, dsr, pbo)`**：G1' 过线 **∧** DSR≥0.95（`deflated_sharpe_ratio` 原始收益跑·**n_trials=累计账本总试验数**（活锚头实读·**跨波不重置**·TRIAL_LABOR_LAW §4——**r410 起草时点实读 328,615**（live head=W5-SCREEN append 后 bm-c r193 在册值；W5-JUDGE 落地后随之增·冻结与跑时以活值为准）+本波 SCREEN 格并入后折减；禁 dsr_from_stats 充数）**∧** 审慎 PBO≤0.25（`screening/pbo.py` CSCV 8 块·**族=策略模块**（grid 业务模块=n/a）·族内全部波内候选/全史 base 面 Sharpe 向量=同机竞争网格 g25_retro 先例；模块数不足 8=insufficient 如实→G2 不可过）；缺输入诚实拒收（missing_inputs 机制）。
- **波级多重检验税披露（O-2245 强制·护栏随 N 加码）**：①N_wave=SCREEN 核+JUDGE 核逐批披露；②**E[FP]=0.05×N_wave_judged_cells** 如实披露（DSR≥0.95 门即多重检验校正门·通过者仍存活非否定面）；③波级 PBO 聚合读数另列（跨族）；④**语法消耗登记簿**（research/TRIAL_GRAMMAR_LEDGER.md·append-only）落 wave-6 行（grammar sha16+w6_grammar.json 序列化时点 raw/dedup 计数+seeds+consumed 时刻）——**同语法禁重跑**（防疏浚·TRIAL_LABOR_LAW §4）。
- **s4 intake（上岗线·O-2245 中 3）**：G2 eligible 存活者 → **D6 绑定门**（对在册公判+存活者两两 max|corr|·日收益口径=sleeve-tag 先例；≥0.7 拒收·存活者簇内行缩留 DSR 最高者（平手=最低 candidate_id））→ STRATEGY_LIBRARY 注册行（带 evidence_cutoff+SIGNAL_BUILDERS 接线+smoke 锚定门复跑·模板 §8 律）+ **TRIAL-<FAMILY>-<NN> 袖盘上岗**（O-2045 PROSPECT 机械复用·观察车道）+ **48h 内 CEO 呈报**（判决面落地起计）。**实际存活数按实际划（零存活=合法判决照报不翻案）**。

## §5 跑前预测。【写死于跑前·≥3 条·含极端日先验。】

1. **去重率**：raw 5,000 → distinct ∈ [2,800, 4,600]（W3 实弹缩 29%/W4 3,810/W5 3,926 同口径；本波 vconf∈{surge,dry} 占 2/3 新空间摊低跨波重复·vconf=none∩前波已判面已被排除簿拦截→缩率预期 [8%, 44%]）。
2. **null 底与初筛通过率**：null 族 beat6m 中位 <0.50（成我方摸索方向·W1-W5 同向）；p95 ∈ [0.42, 0.62]（W1/W2/W3/W4/W5 五波同带 0.5116/0.5164）；初筛存活率 ∈ [2%, 15%] → 存活 [100, 750] 格。
3. **判决面**：G1' 过线 [0, 60]；**G2 eligible [0, 5]——模态结局=零或近零**（DSR 按累计 N≥328k+ 折减=极重校正·六批判决同门实证；零存活=合法产出如实报）。
4. **VCONF 面方向先验（本波新增面·方向可证伪）**：**volume_surge 面与 volume_dry 面双向开放读数**——外源 GKM 2001 高量溢价=surge 面 LONG 方向弱直接锚（美国个股截面月窗口径错位如实）；A 股口诀族内部方向矛盾（「量增价涨才靠谱」vs「放量上涨必回调」）=**两向殉死如实·主证让位仓内探针+普查**（VSTD20 量族时序门正信号在册）；面开窗率 50.26% 近半开=面样本充足性结构性占优（19 bar 预热窗 vs VOL 519 bar=改进面）；yang 日 surge 率 53.01% vs red 日 47.47% 共动结构=VCONF×YANG 交叉面载信息（读数非先验）；**四门交互=开放面无直接外源证据**（gate×vol×yang×vconf 叠加增益是否存在=本波真问题·读数非先验）。
5. **极端日先验（硬界三件套 c·D-20260925-01①）**：本波数据窗内处在极端微观结构日=2015-07 股灾、2016-01 熔断、2024-02 微盘崩、2024-09-24/09-30 政策脉冲、2025-04-07 外生缺口、2026-01-19 极端量日——候选格曲线尾部|日收益|>8% 层级在场真值非腐坏；**VCONF 门新增披露**：七极端日 **6 surge**（surge 面危机日敞口保持——放量日=恐慌/脉冲参与日在册；vs W5 YANG 门 4 red 关=互补非同构）→surge 面危机日暴露非零→**整窗判读+dd 线非单点 max 检测线**；**dry 面七极端日 6 关**（2015-07-27 0.524x 例外在册）→dry 面危机日暴露结构性收敛；危机日计数+止损触发日计数+**四门面（gate×vol×yang×vconf）计数列随格披露**。

## §6 产物

- runner：`scripts/trial_labor_w6.py`（subcommands: generate / screen / judge / intake / status / selftest；import-face 复用 trial_labor_w1.py 锚枚举/装载/锚门/包裹原语+trial_labor_w2.py 初始止损叠加层+trial_labor_w3.py 政体门叠加层+trial_labor_w4.py 波动门叠加层+trial_labor_w5.py 阳线门叠加层与三门机械+mass_trial_w1.py Sobol sample_draws 范式+strategies/ 工厂+engine/backtester 引擎腿禁重写要改；selftest=hermetic 合成面离线腿（r116 律 B7b 合约腿+r297 律确定性双跑字节恒等腿）+**VCONF 门因果腿**（信号日信息集·19 bar 预热窗 gate-closed·vconf=none==W5 语义基线恒等腿）+**四门交叠腿**（gate×vol×yang×vconf 四条件交正确性）+**门序列点时完整性腿**（G-VCONF 探针锚断言·surge 计数 1,741·零成交量行==0·med20 首有效 bar-19）；**初始止损+政体门+波动门+阳线门+量能门叠加=grammar 层实现，engine/exit_rules.py 零触碰**）。
- 产物：`results/trial_labor_w6/`——w6_grammar.json（语法全套：函数-参数值域表·轴网格含止损轴+政体门轴+波动门轴+阳线门轴+**量能门轴**+去重审计段）；w6_candidates.json（全量候选 provenance+D6 披露列+止损面序列+政体门面序列+波动门面序列+阳线门面序列+**量能门面序列**）；w6_screen.json（null 族 floor+全格 beat6m 分布·零候选选择性披露·VCONF 面+四门交互分段存活统计）；w6_screen_cells.csv（小件入 git）；w6_judge.json（判决全面 G1'/G2/DSR/PBO/E[FP]·四门交互分段披露）；w6_intake.json（上岗 D6 裁定）；全部顶层 evidence_cutoff+audit 段。
- 语法消耗登记簿：`research/TRIAL_GRAMMAR_LEDGER.md`（append-only·wave-6 行：语法 sha+raw/dedup 计数+seed+消耗时点）。
- 池路由：SCREEN/JUDGE 批 >5min 入池（O-2100）；**lane_owner=null**（core48+T-18 in-repo 双机可跑·judge 面 cache-less 机 in-runner exit 2 诚实=W1-W5 先例）；workers_plan ≥floor(核数/0.8) BelowNormal；RAM 门禁 r354 三采样例（池条目 data_gates 注记）；**池条目必带 consumer_plan**（§0 消费面·O-1820(3) autofill submit 断面律）；**CPU 排队=池优先序自主调度**；**W6-JUDGE 序门=排在 W5-JUDGE 及其余在飞判决面后（§0）**；§9 交接窗下。
- **池条目 consumer_plan 草案（冻结步随池条目落地）**：`TRIAL-LABOR-W6-GENERATE/SCREEN/JUDGE → judged verdict face (w6_judge.json) → s4 intake → STRATEGY_LIBRARY + TRIAL-* paper accounts → 48h CEO report + scorecard CEO face; screen null p95 → next-wave prereg reference band (W1-W5 0.5116/0.5164 lineage)`。

## §7 跑后实证。【跑前必须为空——占位纪律：写数字即造假。】

（一次定稿；工程修复重跑双跑留痕如实账；确定性引擎产物写 bug 的合法重执行口径≠结果重跑）

## §8 批后复盘。【必填 §7-T。】

（预测对账门禁链损耗账 results/gate_attrition.json 追加行·判线 v2 当批读数·回执入轮报告+CODELY.md 行级追加；若注册新员：注册件带 evidence_cutoff+live/paper SIGNAL_BUILDERS 接线+smoke 锚定门复跑；判决面结果 48h 内呈 CEO。）

## §9 追加冻结节。【append-only·每 sub-wave 一冻——禁跑前另立冻结。】

- **W2-C 族面交接注记（anti-dup·W5 同例沿用）**：因子普查存活腿族（census fusion legs）=TRIAL_LABOR_W2_PREREG §9.1 declare 的 W2 when-ready 子波独占面——**本波 §0 declare 禁碰**；W6 未来并入该供给=待 W2-C 消费落地后另发 declare（TRIAL_LABOR_LAW §5 律）。
- **judged 供结 generate 时点 declare 窗**：六判决批（W1/MASS/W2/W3/W4/W5）+W5_screen 存活清单 372 落地后、本波 generate 跑前=§1 (d) 面加权 declare 窗（实读产物并表·逐源行数披露）；generate 已跑后落地者不入本波（禁事后改配）。
- **s3 判决面**：已冻结于 §3（W5 结构同构·四门叠加=三门机械+一条件交·无需另立 sub-wave 冻结）；若跑前需修栈=零跑修档先例（r251/r280·如实留痕非结果驱动）。
- **runner 构建切片开放**（W3/W4/W5 先例）：prereg 冻结后 runner build+语法序列化+TRIAL_GRAMMAR_LEDGER wave-6 行+池条目（TRIAL-LABOR-W6-GENERATE）=开放任何健康机器认领（单写者 per 产物件·W2-W5 先例）；判决物理腿=deep-panel 宿主+RAM r354+W6-JUDGE 序门（§0）。
- **冻结触发器与步骤（本 draft 状态横幅）**：触发器=W5 全链消费落地（W5-JUDGE judge-finalize+w5_judge.json+ledger append）∧判官零在飞批；冻结步=commit 冻结+SEED_REGISTRY 三键同 commit（草稿泊位 20303500/20304000/20304500 冻结时点三步律复验·撞带重取+横幅注记）+波级票开票+同轮认领+F-04 MSG；冻结前本件零烧批效力（fill_ladder prereg_frozen 门拒 draft 头）。
