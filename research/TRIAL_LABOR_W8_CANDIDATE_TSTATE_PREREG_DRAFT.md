# TRIAL_LABOR_W8_CANDIDATE_TSTATE_PREREG_DRAFT —— TSTATE 时序态门 wave-8 候选泊位（转泊收执 2026-09-29 09:4x·bm-a r422）

> **【转泊收执（collision yield receipt·fleet/README.md §4 commit 时间序）】**本件原为 bm-a r421 起草+冻结的 TRIAL_LABOR_W7_PREREG（TSTATE 时序态门·本地 commit 2026-09-29 09:07:52·SEED 三键 20305000/20305500/20306000 同 commit 登记·T-118 开票认领·F-04 MSG-0905 声明——推送被拒未及上链）。W7 泊位三机同窗撞车：bm-c STREAK 稿 ba2653539 @09:07:05 先落 origin（r207 冻结上链 5de79413b）+bm-b AMP 稿 r417a 已让路转 W8 候选 → 本机后到让路：**W7=STREAK 版正典**（research/TRIAL_LABOR_W7_PREREG.md 现挂 bm-c 冻结版），本 TSTATE 版 **W7 冻结失效**——wave 号/SEED 三键/T-118 票全归 W7-STREAK；TSTATE 若立 W8 须另开票+种子撞带重取（三步律复验）+重走冻结四件套（prereg 冻结+SEED 同 commit+票同轮认领+F-04 MSG）。转泊后状态=**W8 候选备货泊位**（与 bm-b AMP 并列·W8 起草窗=W7 全链消费落地后·任何健康机可认领起草·起草面无门禁）。**供给侧事实全部保值有效**：TSTATE census 正信号主证（O-1855④ MAD60_q10 中位 t=+2.255·60% 工具 |t|>2 / RSV60_low<0.2 中位 t=+2.201·58%·20 日前瞻窗）+探针件 results/_r421bma_tstate_probe.py + _r421bma_tstate_probe_facts.json（含 pandas NaN 比较/bool first_valid_index 双伪影坑律修正面·九十五批）+§1-§9 全部冻结文语义。以下原文逐字保留（标题行 wave-7 字样=历史原貌不追改）。

# TRIAL_LABOR_W7_PREREG —— T-118 千人试用期大考 wave-7 波级预注册（MASS CANDIDATE TRIAL PROGRAM 第七波·5000 人量能确认门）

> **【状态：FROZEN——已冻结·2026-09-29 09:0x·bm-a r421（起草+冻结同窗·起草面无门禁任意轮可开）】冻结触发器（已满足·机械回执 2026-09-29 09:0x 实读）**=W6 全链消费落地（TRIAL-LABOR-W6-JUDGE judge-finalize 落地·results/trial_labor_w6/w6_judge.json generated 2026-09-29T08:14:22+08:00·**ledger head 实读 total=333,432**·E[FP]=14.65·四门面 G1 全零诚实负锚·w6_intake lawful-zero 同轮·48h CEO 呈报钟起计 deadline 10-01 08:14）**∧ 判官零在飞批**（池面机械核：runnable_pool 110/110 全 done·零非 done 条目）。冻结步四件齐套=commit 冻结+SEED_REGISTRY 三键同 commit（R250 一步律·**20305000/20305500/20306000 三步律复验全绿**：registry 102 键盘点带内零占用+首元素与全基互异+rg 全仓码面零种子面命中〔data/daily CSV 量列数值命中=数据面非种子面·W6「文档泊位声明≠种子面」同族判例〕）+波级票 T-2026-09-29-118 开票+同轮认领（O-1730）+F-04 MSG-20260929-0905 声明。**冻结时点起本件烧批效力生效**（fill_ladder prereq_frozen 门放行）。
> 模板=research/PREREG_TEMPLATE.md（§0-§8 全节）；跑前 commit 冻结；跑后只回填 §7/§8，要改判据要重跑。
> 令源：CEO 直令 O-2026-09-27-2245（千人试用期大考）+ O-2026-09-27-2250 常设律（firm/TRIAL_LABOR_LAW.md v1.0「以后不要我提醒」）+ O-20260928-1522（CEO 研究导向：国内民俗判据优先立项·科学照常验证·**时序门普查正信号→民俗判据形式化为数值门=1522 正例**）；波级票=冻结步开票（W6 先例 T-2026-09-29-117）；TRIAL_LABOR_LAW §1 常供律起草面无门禁任意轮可开=W2-W6 同例；**W7-JUDGE 面=RAM r354 三采样门+串行 flip 纪律（跑时零在飞判决面=队列面即时确认·序门留痕=物理依赖合法暂缓事由·bm-b r369 裁定族）**；起草/生成/初筛三面=CPU 池面零 RAM 占用合法。
> 统摄律：firm/RANDOM_LARGE_SAMPLE_LAW v1.0（判决面）+ firm/REFINE_BENCH_LAW v1.0（轴系）+ TRIAL_LABOR_LAW §1-§6 + research/BACKTEST_SCIENCE.md v2（判据唯一权威）+ BACKTEST_PLAN.md 三铁律 + COMPUTE_AUDIT.md 批件纪律 + **O-1820(3) consumer_plan 池 schema 必填律**。
> **本件=波级（Wave-level）预注册**：生成语法/漏斗规则/判据全冻结；sub-wave 追加面一律走 §9 append-confirm（每 sub-wave 一冻结），要用本冻结面跑追加法必须另立。
> **本波≠W1/MASS/W2-W6 语法血统**：新语法面=**时序态门 TSTATE ∈ {none, deep_pullback, oversold_rsv}** 叠加层（扩容面）→ **新语法新 sha16**（≠W1 a2fa15f4b06b3c40 ≠MASS 96269ebe766c3fc2 ≠W2 1dd3d95792395cec ≠W3 cc59eab79db53436 ≠W4 d498e9343ee57460 ≠W5 29720178c39425de ≠W6 2d395f5f8e7d16cb；W7 sha=w7_grammar.json 序列化时点新算·构造性相异），同语法禁重跑（TRIAL_LABOR_LAW §4）经新语法面合法开法。
> **主证供给源（TRIAL_LABOR_LAW §5 淬炼台/普查产出通道）**：时序门统计普查正信号（O-1855④·ETF/基金宇宙 1,724 码·**MAD60_q10 中位 t=+2.255〔60% 工具 |t|>2〕+RSV60_low<0.2 中位 t=+2.201〔58%〕·20 日前瞻窗**·工件=toolstack/research/GATE_CENSUS_SUPPLY.md·描述性普查非策略宣称）——「同族换用法」路线（Alpha158 截面族全判负×时序门用法正信号）的**民俗判据形式化第二例**：「跌深了/超卖才敢接」=A 股短期反转>动量民俗判据族；门定义逐字移植 census 脚本（gate_census.py instrument_gates 面）。外源证据链（借力律 O-1721）：A 股短期反转效应学术与民俗双重先例在册（普查件引证面）；**期限错位如实披露：普查正信号=20 日前瞻窗·本波引擎判决窗={6m,12m,24m}=方向先验弱锚非直接证据·两向殉死如实**。

## §0 批件身份。【跑前。】

- 批名/批号：**TRIAL_LABOR_W7**（千人试用期大考·wave-7·5000 人量能确认门）。三层漏斗子批（dict schema 唯一）：
  - **TRIAL_LAB_W7_SCREEN**（s2 廉价初筛批）：batch_trials = 去重后候选数 + 200 null（每格 1 trial）；raw 5,000 → 去重门后 ≥3,000 distinct —— **5,000=上限非金数指标**（语义重复无效人不计数·造数凑烧禁例）；
  - **TRIAL_LAB_W7_JUDGE**（s3 全量判决批）：batch_trials = 初筛存活者数（judged cells；双 nulls=B/P 重采样面非 ledger +0·census §9.2 NAV 推导面先例）。
  - 两批 evidence_cutoff 均 **2026-09-22**（P-5C 冻结口径 binding·双轴同降·W1 §9.3 零跑修档整体沿用）。
- 认领：起草+冻结同窗（bm-a r421·触发器双门 MET 机械回执在册）；波级票 T-2026-09-29-118 开票+同轮认领（O-1730·W6 先例）；认领依据=TRIAL_LABOR_LAW §1 常供律例行供给步，无需 GM 另署名 per T-96/W2-W6 先例。
- 部门归属：dept:策略（生成引棒供给面）+ dept:研究（判决漏斗面）joint（票面 note 同 W1-W6）。
- 算力预算：生成去重=零（分钟级单机·76 函数值域表枚举 5,000 抽样）；初筛面 ≥5,200 格量级（≥3,000 候选+200 null；leg-L 6m 全史引擎回测——W1 ~28s/候选单核生产力账+W3 实弹 3,752 格 4.6min 池批+W6 4,152 格池批实证）→ **估分锺级-小时级池批 @ ≥floor(核数/0.8) workers**（>5min 一律入 results/runnable_pool.json·O-2100 执行面分离；每 50 候选一 checkpoint 断轮续跑·R41）；判决面=分钟级簇（双 nulls 重采样重量级·deep-panel 宿主物理腿=RAM 门）。
- **供结契约如实披露**：A=在册六员工模板族 500 抽（常供线维护面）；B=流派战法模板大考 4,500 抽 → 76 函数均摊 ≈59.2 抽/函数（与 W2-W6 同口径·七波面累计 ≥26 抽/函数下限沿 W6 六波面口径）；C=因子普查存活腿族=**本波禁碰**（W2 §9.1 declare 与 W2-C when-ready 子波独占·anti-dup hard law；W7 如需并入=待 W2-C 消费落地后另发 declare）；D=judged 供结变体面=**generate 时点实读 declare 窗**（**W1-JUDGE+MASS judged+W2-JUDGE+W3-JUDGE+W4-JUDGE+W5-JUDGE+W6-JUDGE 七源全部已落地**=七源逐源 declare 实读并入加权·**起草时点七源全在册零 declared-unavailable**——与 W2-W6 起草时点部分未落地面不同·如实注记）；generate 跑前重读 live prev 增量并入加权 declare，W2-W6 同门先例。**48h CEO 呈报钟**：随判决面落地起计（judge-finalize 后 48h·票面持有；非本起草时点计）。
- **W7-JUDGE 物理序门（bm-b r369 裁定族·票内留痕）**：跑时若任一判决面在飞=排其后（RAM r354 三采样门+串行 flip 既有纪律自动实现）；冻结时点零在飞判决面（池 110/110 done）=队列面即时确认在案；SCREEN 面=CPU 池面先行烧合法（RAM 零占用）。
- **consumer_plan（O-1820(3) 池 schema 必填·冻结步起生效）**：W7 产物消费面=TRIAL_LAB_W7_JUDGE verdict 面（G1'/G2/DSR/PBO 判定件）→ s4 intake（D6 绑定门→STRATEGY_LIBRARY 注册行+TRIAL-<FAMILY>-<NN> 纸盘上岗）→ 48h CEO 呈报面+scorecard/CEO 一页纸消费；SCREEN null p95=下一波 prereg 判读参照带（W1-W6 同例 0.5116/0.5164/0.5196 带内延续）。

## §1 伪 α 机制段。【四选一+论证·D6 门槛。】

- **供给时 A（在册六员工模板精炼）**：[x] 行为偏差（主）——风险源价（辅）——母体机器同承继 W1-W6 §1（VOLATILITY-CE-01 低波风险源价/COMPOSITE 复合源价/ENGULF·NEEDLE·DROUGHT 确认性行为反转+首阳确认+量能确认层）。本波主张：**深回撤/超卖时序态条件下存在可检出新增益变体**——「跌深了才敢接/超卖才买」=A 股短期反转>动量民俗判据族核心口诀（CEO 1522 导向：国内打法优先立项·民俗判据形式化为数值门正例·时序门普查正信号主证）：信号池溢价由「深回撤/超卖态入场者」向「任意态入场者」收取；**代价支付者=回撤/超卖极端日的恐慌性先卖者**（恐慌抛售尾部=行为面过度反应·修复性回补由深回撤买方收取；「谁付出代价」答案=极端日卖方）。
- **供给时 B（流派战法模板大考）**：[x] 逐流派四选一映射同 W1 §1（21 流派·工厂批次血统；负先验标签如实随格携带、漏斗重仓复置不预筛）。本波主张：**冻结工厂库在 Sobol 低差异抽样轴系下、政体门×波动门×阳线门×量能门×时序态门×初始止损×轴系交互存在仅大规模混水摸深抽样可检出的 α 口**。
- **时序态门机制注记（本波新增面·冻结定义）**：TSTATE=入场许可的条件化叠加层（非引擎出场规则——时机归 ENGINE 心律）——**回撤深度/超卖位置过滤面**：信号日价格相对自身 60 日趋势/区间的位置状态。**TSTATE 面≠GATE 趋势面（MA200 多空域）≠VOL 波动面（波动分位）≠YANG K 线面（单日颜色）≠VCONF 量能面（参与确认）**——探针实证（§2）：门态率在 bear 内 19.28%/33.44% vs bull 内 5.22%/5.62%（**政体载息=深度精化非独立维·如实注记·非 W6 VCONF 型近独立面**）；bull 侧存活面非空（mad60_q10∧bull 93 日/rsv60∧bull 100 日=bull 内深回撤日存在）；bear 内仅 19-33% 日开窗=**域内条件精化价值面**（谁付出代价：非深回撤日入场者由深回撤日入场者付出·行为假说·方向先验普查主证两向殉死如实·期限错位弱锚如实）。
- **D6 同族相关性准入（W1 大考面适配声明整体沿用）**：批内候选两两 corr 矩阵全量计算（去重门前置级）；①≥0.999 塌缩=生成段硬绑门（②）；②0.7 线在注册级=全候选审计披露（逐格 max|corr| 列），注册生效判定=s4 intake（≥0.7 拒收·存活者簇内行缩留最优）；批内 0.7-0.999 中带=锚标涨选面，非准入门。
- 排除簿（anti-dredging·W1-W6 同例·**judged 七源 declare 窗+screen 七清单**）：**已判精确核（正负了然）禁重跑**——cell key=(template, params, axis_config, initial_stop, gate, vol, yang, vconf, **tstate**)；**语义恒等匹配=前波 cell key 无 tstate 轴者按 tstate=none 补全类匹**（gate/vol/yang/vconf=none∩tstate=none 面=该前波格全等）；全部既有已判格（judged 产物 declare 窗 generate 时点实读七源=W1/MASS/W2/W3/W4/W5/W6·判负函数默认参数原批）+**W1_screen 存活 149+W2_screen 404+MASS screen 166+W3_screen 513+W4_screen 461+W5_screen 372+W6_screen 293**（七清单 generate 时点实读消费）→ 生成段排除并逐格留痕；**tstate∈{deep_pullback, oversold_rsv} 面（与任意 gate/vol/yang/vconf 组合）为新语法面合法开法**。本波新 prereg+新语法（轴系×止损面×政体门×波动门×阳线门×量能门×时序态门×Sobol），符合 RANDOM_LARGE_SAMPLE_LAW §5 唯一合法重试通道。

## §2 数据与面板。【跑前探针事实，非结果。】

- 宽基/池：**core48**（ETF 交易线季风域·在册公判注册域；loader=引擎 T-22/T-34 血统 import-face 复用禁重写·tl1.load_core()）+ 判决段深轴 **T-18 增长截面深面板**（Money02 t18_deep_panel cache 只读·WILD-S1/KLINE 只读先例禁写）。
- **TSTATE 门序列（本波新增面·跑前探针事实 r421 实读·census 定义逐字移植）**：
  - **deep_pullback（MAD60_q10）**：dist(d)=close(d)/MA60(d)−1（MA60=close 滚动 60 bar 均值·min_periods=60）；门=dist(d) < dist 序列滚动 252 观测 20 分位（min_periods=120）——**价距 60 日均线下十分位=深回撤态**；判定在**信号日 d 收盘信息集**（T+1 因果律·与 GATE/VOL/YANG/VCONF 同信息集零前瞻·入场=d+1 开盘）；**178 bar 预热窗 gate-closed 诚实**（MA60 59 bar+分位 min_periods 120 bar→首可判 bar-idx==178——五门最长预热·vs YANG 零预热/VCONF 19/VOL 519 结构谱系如实注记）；
  - **oversold_rsv（RSV60_low<0.2）**：rsv(d)=(close(d)−low60(d))/(high60(d)−low60(d))（hh/ll=high/low 滚动 60 bar 极值·hh==ll→NaN）；门=rsv(d)<0.2——**60 日区间位<20%=超卖态**；**59 bar 预热窗 gate-closed 诚实**（首可判 bar-idx==59）。
  - 510300 全史锚面（data/daily/sh510300.csv·3,483 行·2012-05-28→2026-09-22 cutoff 冻结·W4/W5/W6 探针基同锚）：**零成交量行=0**；deep_pullback 可判 3,305 日·门真 383 日=**11.59% 开窗率**；oversold_rsv 可判 3,424 日·门真 632 日=**18.46%**；**面载息结构（独立维证伪面·如实注记）**：bear 内门率 19.28%/33.44% vs bull 内 5.22%/5.62%（政体载息=深度精化面）；wild 内 20.26%/20.68% vs calm 内 3.55%/15.04%；red 内 13.34%/23.56% vs yang 内 9.15%/12.79%（**弱面载息非独立维——vs W6 VCONF 四面近独立 50%±5% 结构性不同·TSTATE=条件精化门非正交维·机制注记 §1 同谳**）；**bull 侧存活面非空**：mad60_q10∧bull 93 日/rsv60∧bull 100 日；**五门 2^5=32 格交叉计数 29 非空 3 空**（空格全在 bull|calm|mad60 角〔bull∧calm∧mad60 三格零计数=深回撤∩牛市∩低波结构性稀有〕·min 非零 3/最大 96·**空角格由 G1' entries≥30 交易门自然筛除=诚实淘汰非预筛发明**）；交叉下界 {rsv60∧yang 224, mad60∧surge 213, mad60∧bull 93, rsv60∧bull 100}；**七极端日门态**：deep_pullback 真 2 日（2015-07-27 股灾日〔dist 极端〕+2025-04-07 外生缺口）/oversold_rsv 真 1 日（2025-04-07 rsv=0.1753）/其余 5 日双门关（2016-01-04 rsv=0.2583 关·2024-09-30 rsv=0.9932 高位关等）——**TSTATE 面危机日敞口结构性收敛（vs VCONF surge 面敞口保持=互补非同构）**；截断后 post-cutoff 行排除 3 行实证。探针代码=results/_r421bma_tstate_probe.py+事实件 _r421bma_tstate_probe_facts.json 留痕（探针事实面非结果面）。
- **GATE 门序列（W3 冻结定义整体继承）**：510300 close(d) vs MA200(d)（min_periods=200·首 199 bar NaN→bull/bear 面 gate-closed 诚实）；GATE 态在信号日 d 收盘信息集上判定。
- **VOL 门序列（W4 冻结定义整体继承）**：vol20(d)=ret 滚动 20 bar 样本 std（ddof=1·min_periods=20·含 d）；med500(d)=vol20 序列滚动 500 观测中位（min_periods=500）；calm=vol20≤med500/wild=vol20>med500；NaN 窗（首 519 bar）→calm/wild 面 gate-closed 诚实。
- **YANG 门序列（W5 冻结定义整体继承）**：信号日阳线=close(d)>open(d)（二元·零预热窗）；判定在信号日 d 收盘信息集；first_yang=仅信号日阳线日许入场。
- **VCONF 门序列（W6 冻结定义整体继承）**：信号日量能态=volume(d) vs med20(d)（med20=成交量滚动 20 bar 中位·min_periods=20·含 d）；volume_surge=volume>med20/volume_dry=volume≤med20；19 bar 预热窗 gate-closed 诚实。
- **evidence_cutoff=2026-09-22（P-5C 冻结口径 binding·双轴同降）**：整体沿用 W1 §9.3/W3-W6 机械——**import `scripts/p5c_virtual_timepoint.py` 冻结口径禁重实现**：初筛面=leg-L 6m 面 census 限=FROZEN_CENSUS["L"]["6m"]=**1,253**；判决面=双腿窗口 {6m,12m,24m} 全网格逐面==FROZEN_CENSUS 对应窗值（L 1253/1127/875·D 3104/2978/2726）；被动=模块 passive_rel/passive-cell 机械。Cutoff 后新 bar 锁定不得回流本批；结果 JSON 顶层必带 `science_gates.cutoff_meta("2026-09-22")`（缺字段=C2 VIOLATION）。
- 数据完备门（fail-closed，不过即 VOID 中止零产出）：
  - **G-PANEL**：core48 48/48 员每员 ≥60 行·截断后末行日期==2026-09-22 逐员唯一·OHLCV 列齐（volume 列在位=VCONF/TSTATE 面物理前提）；
  - **G-CENSUS**：P-5C FROZEN_CENSUS 逐面实读断言（L/D×{6m,12m,24m} 六键逐位；import 实读禁手抄）；
  - **G-ANCHOR**：在册六员工注册配置经本波 grammar 引擎默认路线（template_default+EW+daily+initial_stop=none+gate=none+vol=none+yang=none+vconf=none+**tstate=none**）重放，IS/OOS Sharpe==live.paper 锚定门常数（import 实读禁手抄；不等=基线漂移 VOID）；
  - **G-MANIFEST**：深轴 manifest verdict==PASS（48 员 twin cache 可核路·W1 §9.3 manifest_note 先例·冻结时实读=trial_labor_w6 judge_state g_manifest PASS/48 员在册·跑时以活值为准）；
  - **G-EXCLUDE**：已判格排除清单装载（judged 七源+screen 七清单）+命中计数披露（排除 0 合法·排除 0 如实）；
  - **G-VOL/G-YANG/G-VCONF**（W4/W5/W6 沿用）：点时完整性断言全锚（med500 首有效 bar-idx==519·calm/wild=={1523,1441}；yang 计数==1,751 零预热；med20 首有效 bar-idx==19·surge==1,741·零成交量行==0·交叉下界 {yang∧surge 924, red∧dry 904}·四门 16 格全非空）；
  - **G-TSTATE**（本波新增）：**深回撤门点时完整性断言（MA60 首有效 bar-idx==59·分位序列首可判 bar-idx==178 预热窗锚+门真计数==383 探针锚定+可判==3,305）+超卖门点时完整性断言（首可判 bar-idx==59+门真==632+可判==3,424+hh==ll 零除退化面 NaN gate-closed）+交叉下界锚定 {rsv60∧yang 224, mad60∧surge 213, mad60∧bull 93, rsv60∧bull 100}+五门 32 格计数披露（29 非空·3 空格名单逐格披露）+七极端日门态断言（2015-07-27 mad60 真/2025-04-07 双门真 rsv=0.1753/其余 5 日双门关）+截断后末行==cutoff**。

## §3 方法论。【冻结。】

- **生成语法（全冻结——零新信号发明——候选只从冻结规则原语组合生成）**：
  - 原语面：策略工厂 `strategies/` 86 函数/13 模块（W3-W6 同源计数·跑时以 import 实测为准如实披露）；时 A=在册六员工模板（low_vol_long/composite_top5/composite_top8/engulf_reversal/needle_probe/vol_drought_reversal）；时 B=其余工厂函数 76（86≠76：grid 模块 4 亦业务函数排除——GRID 线专用判决线机械不可入通用语法表达，W1-W6 同例如实披露）；函数-参数空间=各函数签名参数冻结值域表（runner build 时逐函数枚举值域表随 w7_grammar.json 序列化冻结=W1-W6 同款）。
  - 轴系（REFINE_BENCH_LAW §2 标准轴·W6 全轴系继承+本波扩容面）：入场过滤 ∈ {none, depth_thresh, amplitude, liquidity, trend_slope, dual_window, fundamental_mask}（7）；出场 ∈ {template_default, CE 注册出场, time_stop_5d/7d/10d/20d, trailing_stop, profit_ladder}；仓位 ∈ {equal_weight, inverse_vol, cap20, regime_delever}（4）；时机 ∈ {daily_signal, weekly_grid}（2）；初始止损叠加 ∈ {none, p3, p5, p8, p12, a15, a20, a25}（8·W2 面沿用逐字继承）；政体入场门 GATE ∈ {none, bull, bear}（W3 沿用）；波动率入场门 VOL ∈ {none, calm, wild}（W4 沿用）；阳线确认门 YANG ∈ {none, first_yang}（W5 沿用）；量能确认门 VCONF ∈ {none, volume_surge, volume_dry}（W6 沿用）；**时序态门 TSTATE ∈ {none, deep_pullback, oversold_rsv}（本波新增面·§2 冻结定义）——十元组 R/X/S/T/STOP/GATE/VOL/YANG/VCONF/TSTATE = 580,608 轴组合/模板**（W6=193,536·W5=64,512·W4=32,256·W3=10,752·W2=3,584·W1=448）。
  - **TSTATE 门叠加层（扩容面·冻结定义）**：门态在**信号日 d 收盘信息集**上判定（§2 序列）；**deep_pullback**=仅深回撤日（dist<滚动 252 分位 10%）许入场；**oversold_rsv**=仅超卖日（rsv60<0.2）许入场；**none**=无门（W6 语义基线）；门只作用于**入场许可**（有效信号置零·MSG-0440 E1 映射先例·grammar 层实现），出场逻辑零改动；**预热窗 gate-closed 诚实**（deep_pullback 首 178 bar/oversold_rsv 首 59 bar 不可判）；GATE 与 VOL 与 YANG 与 VCONF 与 TSTATE 门独立叠加（**五门=五条件交**）。
  - 随机抽样（Sobol 沿用=W3-W6 declare 血统）：**import-face 复用 MASS_TRIAL_W1 sample_draws 范式禁重写**——`scipy.stats.qmc.Sobol(参数维, scramble=True, seed=SEED_BASE+family_idx)` 归一化参数盒低差异 draw+轴组合独立 RNG 流（`default_rng([SEED_BASE+family_idx, 7919])` 整数轴抽轴；**本波 TSTATE 轴并入=十元组 R/X/S/T/STOP/GATE/VOL/YANG/VCONF/TSTATE**）；N=500/时 A（模板轮转确定性指派）+4,500/时 B（76 函数轴转）；**seed 基 `trial_labor_w7_gen`=20305000 / `trial_labor_w7_scrnull`=20305500 / `trial_labor_w7_unc`=20306000**（冻结时点三步律复验全绿：registry 102 键盘点 20305xxx-20306xxx 带零占用+新基首元素与全基互异+rg 全仓码面零种子面命中〔data/daily CSV 量列数值命中=数据面非种子面·W6 文档泊位声明同族判例〕·W5 撞带重取先例未触发泊位持有）；零带占用·重跑字节恒等；SEED_REGISTRY 本冻结同 commit 登记律·R250 一步例。
  - **去重门（T-84 s3 组合恒等塌缩律·强制；W1-W6 同例）**：①持仓恒等指纹=sha256(逐再平衡日持仓 sorted((sym, round(w,4))) 全串)；②候选日收益序列两两 |corr|≥0.999→塌缩为一格（保留代表=确定性最低 candidate_id；原始变体入 audit 段全量保留）；**塌缩计数+保留/淘汰清单如实披露**；判读与账本按塌缩后格数计。
- **s2 廉价初筛（TRIAL_LABOR_LAW §2）**：每 distinct 候选 legacy 轴 leg-L 6m 全史一回测（W1 13bp base 面·T+1；初始止损面+政体门面+波动门面+阳线门面+量能门面+**时序态门面**随格携带）→ beat6m=1,253 虚拟起点中「候选 6m 前向收益≥同窗为动」比例（完整窗生存·partial 窗计数如实披露）。
- **初筛 null 族**：K=200 同构随机信号候选（模板腿→随机信号日生成器；轴腿+初始止损腿+政体门腿+波动门腿+阳线门腿+量能门腿+**时序态门腿**同网格同参数空间 draw·同引擎同成本同面板——BACKTEST_PLAN 三铁律）；**seed=`trial_labor_w7_scrnull`=20305500**（派生 `[20305500, i]`·同 commit 登记律）。
- **初筛判线（跑前写死）**：**存活 iff beat6m > null 族 p95**（程序冻结·零手挑阈·数据自适应刻度）；两项参照（α=0.5·n=1,253）；逐格披露 b/p 值。初筛=漏斗阶段非判决（零注册效力·存活者仅获判决面入场券）。
- **s3 全量判决（存活者·TRIAL_LABOR_LAW §2/§3）**：双腿（P-5C 格 L/D×{6m,12m,24m} 起点）×成本面 {base x1, x2=CostPatch(2.0)（T22 Erratum-1 multiplier 律·禁直引 COST_X2_RATE）}×政体分段 bear/bull/chop+na（T-22 §3 冻结 3-way proxy 逐字）×**双 nulls**（RANDOM_LARGE_SAMPLE_LAW §3）：block bootstrap **B=2000**（block=20 交易日循环块·拼样截回 n 长）+ sign-flip 置换 **P=2000**（逐日符号独立翻转·双侧）；**seed=`trial_labor_w7_unc`=20306000**（派生 `[20306000, cell_idx]`·同 commit 登记律）；rng 流仅限两重采样面禁挪用（census §9.1 用途钉死先例）。**注**：五门=策略构造面（入场许可），政体分段=判决披露面（分段归因）——两面季交不冲突（分段恒带 TRIAL_LABOR_LAW §3 律）；**五门面新增披露列=gate×vol×yang×vconf×tstate 交互分段计数**（W6 四门面翻面计数口径族扩容·面板级非逐格发明口径）+MSG-0450 annex-1 止损披露面（触发/成交日计数+D+1 出场日 close-vs-open 偏离分布·W5/W6 judge 切片已接线面沿用）。
- **样本充足律**：n_eff≥100 起点 × bear/bull/chop 三段各 ≥100 起点窗（na 桶诚实）——不越→verdict=**insufficient-sample 禁判 pass**；**深回撤 178 bar 预热窗+门开窗率 11.59%/18.46%=起点窗覆盖结构性收窄·insufficient 读数预期如实**（TSTATE 活格 n_eff 不足=诚实判读非故障）。
- 描述条款（批级披露不替代 v2 门）：年化 0·OOS(2025+ 恒盲)双正·回撤 ≥−35%·无崩年·x2 面逐字稳定。
- **成本口径**：W1 legacy 引擎面（13bp·T+1·退出优先级冻结禁改）；x2 压测面——与在册锚定/注册判读链同源可比（注册面一致性优先）。
- **账本**：`science_gates.append_ledger("TRIAL_LAB_W7_SCREEN", <distinct 候选+200>, file, evidence_cutoff="2026-09-22")` + `science_gates.append_ledger("TRIAL_LAB_W7_JUDGE", <存活者数>, file, evidence_cutoff="2026-09-22")`（prev=数据驱动锚头实读禁手抄）。

## §4 判据。【跑前写死——禁看结果调整；共享库引用零手抄。】

- **G1' v2 = `science_gates.g1_prime_v2(sharpe_full, returns, batch_cells, pool="core48", n_trades, n_entries)`**：全期 Sharpe>skill_line_v2（数据审动线 max(被动+0.10, μ_null+σ_null·√(2·ln N_eff))·N_eff=活链头本批格数）**∧**平稳 bootstrap CI 下界>0 **∧** entries≥30（G6 双口径 entries_ok 为准）；批报告逐列披露 skill_line/bootstrap_ci/trade_gate 全输入。
- **G2 注册资格 v2 = `science_gates.g2_registration_v2(g1_pass, dsr, pbo)`**：G1' 过线 **∧** DSR≥0.95（`deflated_sharpe_ratio` 原始收益跑·**n_trials=累计账本总试验数**（活锚头实读·**跨波不重置**·TRIAL_LABOR_LAW §4——**冻结时点实读 333,432**（live head=W6-JUDGE append 后 bm-b r415 在册值）+本波 SCREEN 格并入后折减；禁 dsr_from_stats 充数）**∧** 审慎 PBO≤0.25（`screening/pbo.py` CSCV 8 块·**族=策略模块**（grid 业务模块=n/a）·族内全部波内候选/全史 base 面 Sharpe 向量=同机竞争网格 g25_retro 先例；模块数不足 8=insufficient 如实→G2 不可过）；缺输入诚实拒收（missing_inputs 机制）。
- **波级多重检验税披露（O-2245 强制·护栏随 N 加码）**：①N_wave=SCREEN 核+JUDGE 核逐批披露；②**E[FP]=0.05×N_wave_judged_cells** 如实披露（DSR≥0.95 门即多重检验校正门·通过者仍存活非否定面）；③波级 PBO 聚合读数另列（跨族）；④**语法消耗登记簿**（research/TRIAL_GRAMMAR_LEDGER.md·append-only）落 wave-7 行（grammar sha16+w7_grammar.json 序列化时点 raw/dedup 计数+seeds+consumed 时刻）——**同语法禁重跑**（防疏浚·TRIAL_LABOR_LAW §4）。
- **s4 intake（上岗线·O-2245 中 3）**：G2 eligible 存活者 → **D6 绑定门**（对在册公判+存活者两两 max|corr|·日收益口径=sleeve-tag 先例；≥0.7 拒收·存活者簇内行缩留 DSR 最高者（平手=最低 candidate_id））→ STRATEGY_LIBRARY 注册行（带 evidence_cutoff+SIGNAL_BUILDERS 接线+smoke 锚定门复跑·模板 §8 律）+ **TRIAL-<FAMILY>-<NN> 袖盘上岗**（O-2045 PROSPECT 机械复用·观察车道）+ **48h 内 CEO 呈报**（判决面落地起计）。**实际存活数按实际划（零存活=合法判决照报不翻案）**。

## §5 跑前预测。【写死于跑前·≥3 条·含极端日先验。】

1. **去重率**：raw 5,000 → distinct ∈ [2,800, 4,600]（W3 29%/W4 3,810/W5 3,926/W6 3,952 同口径；本波 tstate∈{deep_pullback, oversold_rsv} 占 2/3 新空间摊低跨波重复·tstate=none∩前波已判面已被排除簿拦截→缩率预期 [8%, 44%]）。
2. **null 底与初筛通过率**：null 族 beat6m 中位 <0.50（成我方摸索方向·W1-W6 同向）；p95 ∈ [0.42, 0.62]（W1-W6 六波同带 0.5116/0.5164/0.5196 带内延续）；初筛存活率 ∈ [2%, 15%] → 存活 [100, 750] 格；**TSTATE 活格面修正预期：深回撤/超卖门开窗率 11.59%/18.46%=入场机会结构性收窄→TSTATE 活格 beat6m 覆盖窗数低于 null 族→初筛存活率面 TSTATE 格预期低于 none 格（结构性预期非判据）**。
3. **判决面**：G1' 过线 [0, 60]；**G2 eligible [0, 5]——模态结局=零或近零**（DSR 按累计 N≥333k+ 折减=极重校正·七批判决同门实证；零存活=合法产出如实报）。
4. **TSTATE 面方向先验（本波新增面·方向可证伪）**：**deep_pullback 与 oversold_rsv 双向开放读数**——普查主证 20 日前瞻正 t（+2.255/+2.201·方向先验 LONG）**与引擎判决窗 {6m,12m,24m} 期限错位=弱锚非直接证据**（20 日反转溢价在 6m 窗内可被趋势段吃回=两向殉死如实）；政体载息结构（bear 内 19-33% 开窗）→TSTATE 格 bear 段 n_eff 结构性收窄=insufficient 读数预期在案；**五门交互=开放面无直接外源证据**（gate×vol×yang×vconf×tstate 叠加增益是否存在=本波真问题·读数非先验）。
5. **极端日先验（硬界三件套 c·D-20260925-01①）**：本波数据窗内处在极端微观结构日=2015-07 股灾、2016-01 熔断、2024-02 微盘崩、2024-09-24/09-30 政策脉冲、2025-04-07 外生缺口、2026-01-19 极端量日——候选格曲线尾部|日收益|>8% 层级在场真值非腐坏；**TSTATE 门新增披露**：七极端日 deep_pullback 真 2（2015-07-27/2025-04-07）/oversold_rsv 真 1（2025-04-07）/其余 5 日双门关——**TSTATE 面危机日敞口结构性收敛（vs VCONF surge 面 6/7 敞口保持=互补非同构）→危机日保护面预期（读数非先验）**；危机日计数+止损触发日计数+**五门面（gate×vol×yang×vconf×tstate）计数列随格披露**。

## §6 产物

- runner：`scripts/trial_labor_w7.py`（subcommands: generate / screen / judge / intake / status / selftest；import-face 复用 trial_labor_w1.py 锚枚举/装载/锚门/包裹原语+trial_labor_w2.py 初始止损叠加层+trial_labor_w3.py 政体门叠加层+trial_labor_w4.py 波动门叠加层+trial_labor_w5.py 阳线门叠加层+trial_labor_w6.py 量能门叠加层与四门机械+mass_trial_w1.py Sobol sample_draws 范式+strategies/ 工厂+engine/backtester 引擎腿禁重写要改；selftest=hermetic 合成面离线腿（r116 律 B7b 合约腿+r297 律确定性双跑字节恒等腿）+**TSTATE 门因果腿**（信号日信息集·178/59 bar 预热窗 gate-closed·tstate=none==W6 语义基线恒等腿）+**五门交叠腿**（gate×vol×yang×vconf×tstate 五条件交正确性）+**门序列点时完整性腿**（G-TSTATE 探针锚断言·mad60 门真 383/rsv60 门真 632/首可判 178/59/零成交量行==0）+**bool 序列 NaN 比较伪影腿**（r421 探针坑律：NaN<x 比较产 False 非可判——decidable 面必须用底层面值 notna 派生·bool 序列 first_valid_index 全真伪影禁用·argmax 取首真）；**初始止损+政体门+波动门+阳线门+量能门+时序态门叠加=grammar 层实现，engine/exit_rules.py 零触碰**）。
- 产物：`results/trial_labor_w7/`——w7_grammar.json（语法全套：函数-参数值域表·轴网格含止损轴+政体门轴+波动门轴+阳线门轴+量能门轴+**时序态门轴**+去重审计段）；w7_candidates.json（全量候选 provenance+D6 披露列+止损面序列+政体门面序列+波动门面序列+阳线门面序列+量能门面序列+**时序态门面序列**）；w7_screen.json（null 族 floor+全格 beat6m 分布·零候选选择性披露·TSTATE 面+五门交互分段存活统计）；w7_screen_cells.csv（小件入 git）；w7_judge.json（判决全面 G1'/G2/DSR/PBO/E[FP]·五门交互分段披露）；w7_intake.json（上岗 D6 裁定）；全部顶层 evidence_cutoff+audit 段。
- 语法消耗登记簿：`research/TRIAL_GRAMMAR_LEDGER.md`（append-only·wave-7 行：语法 sha+raw/dedup 计数+seed+消耗时点）。
- 池路由：SCREEN/JUDGE 批 >5min 入池（O-2100）；**lane_owner=null**（core48+T-18 in-repo 双机可跑·judge 面 cache-less 机 in-runner exit 2 诚实=W1-W6 先例）；workers_plan ≥floor(核数/0.8) BelowNormal；RAM 门禁 r354 三采样例（池条目 data_gates 注记）；**池条目必带 consumer_plan**（§0 消费面·O-1820(3) autofill submit 断面律）；**CPU 排队=池优先序自主调度**；**W7-JUDGE 序门=跑时在飞判决面后（§0）**；§9 交接窗下。
- **池条目 consumer_plan 草案（冻结步随池条目落地）**：`TRIAL-LABOR-W7-GENERATE/SCREEN/JUDGE → judged verdict face (w7_judge.json) → s4 intake → STRATEGY_LIBRARY + TRIAL-* paper accounts → 48h CEO report + scorecard CEO face; screen null p95 → next-wave prereg reference band (W1-W6 0.5116/0.5164/0.5196 lineage)`。

## §7 跑后实证。【跑前必须为空——占位纪律：写数字即造假。】

（一次定稿；工程修复重跑双跑留痕如实账；确定性引擎产物写 bug 的合法重执行口径≠结果重跑）

## §8 批后复盘。【必填 §7-T。】

（预测对账门禁链损耗账 results/gate_attrition.json 追加行·判线 v2 当批读数·回执入轮报告+CODELY.md 行级追加；若注册新员：注册件带 evidence_cutoff+live/paper SIGNAL_BUILDERS 接线+smoke 锚定门复跑；判决面结果 48h 内呈 CEO。）

## §9 追加冻结节。【append-only·每 sub-wave 一冻——禁跑前另立冻结。】

- **W2-C 族面交接注记（anti-dup·W5/W6 同例沿用）**：因子普查存活腿族（census fusion legs）=TRIAL_LABOR_W2_PREREG §9.1 declare 的 W2 when-ready 子波独占面——**本波 §0 declare 禁碰**；W7 未来并入该供给=待 W2-C 消费落地后另发 declare（TRIAL_LABOR_LAW §5 律）。
- **judged 供结 generate 时点 declare 窗**：七判决批（W1/MASS/W2/W3/W4/W5/W6）全已落地+**W6_screen 存活清单 293 已落地**=generate 时点七源七清单实读并表（逐源行数披露）；generate 跑前若新判决面落地（W7 窗内他批）=§1 (d) 面加权 declare 增量并入；generate 已跑后落地者不入本波（禁事后改配）。
- **s3 判决面**：已冻结于 §3（W6 结构同构·五门叠加=四门机械+一条件交·无需另立 sub-wave 冻结）；若跑前需修栈=零跑修档先例（r251/r280·如实留痕非结果驱动）。
- **runner 构建切片开放**（W3-W6 先例）：prereg 冻结后 runner build+语法序列化+TRIAL_GRAMMAR_LEDGER wave-7 行+池条目（TRIAL-LABOR-W7-GENERATE）=开放任何健康机器认领（单写者 per 产物件·W2-W6 先例）；判决物理腿=deep-panel 宿主+RAM r354+W7-JUDGE 序门（§0）。
- **冻结触发器与步骤（本件状态横幅=已执行回执）**：触发器=W6 全链消费落地（judge-finalize+intake+ledger append 333,432）∧判官零在飞批（池 110/110 done）——**2026-09-29 09:2x 双门 MET 实读在案**；冻结步=commit 冻结+SEED_REGISTRY 三键同 commit（20305000/20305500/20306000 三步律复验全绿·泊位持有）+波级票 T-2026-09-29-118 开票+同轮认领+F-04 MSG-20260929-0905——**四件齐套本窗完成**。
