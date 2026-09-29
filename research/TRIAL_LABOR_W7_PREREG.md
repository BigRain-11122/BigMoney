# TRIAL_LABOR_W7_PREREG —— T-99 千人试用期大考 wave-7 波级预注册（MASS CANDIDATE TRIAL PROGRAM 第七波·连涨连跌确认门）

> **【状态：DRAFT——泊位态·2026-09-29 09:0x·bm-c r206 起草·未冻结零烧批效力】**起草依据=TRIAL_LABOR_LAW §1 常供律（板空 0 open/池饿 110 done 0 ready/无在飞判决批=W6 全链消费落地 2026-09-29 08:14:22〔judge-finalize+w6_judge.json+ledger 333,139+293=333,432 linear 实核〕∧判官零在飞批→默认起草下一波）；起草面无门禁任意轮可开=W2-W6 同例。**冻结触发器（已满足·机械核 2026-09-29 09:0x）**：W6 全链消费落地 ✓（含 s4 intake 零存活合法照报 n_eligible=0+48h CEO 呈报钟 deadline 2026-10-01 08:14 在册=bm-b 票面持有）∧判官零在飞批 ✓（pool 110/110 done·零 ready）——**冻结步待开票**：commit 冻结+SEED_REGISTRY 三键同 commit（泊位 20305000/20305500/20306000·r206 三步律预检已过：registry 99 键全集盘点零占用+首元素互异+rg 全仓 2 命中=数据面 volume 列巧合非种子面如实披露）+波级票开票+同轮认领（O-1730）+F-04 MSG。冻结前本件零烧批效力（fill_ladder prereg_frozen 门拒 draft 头）。
> 模板=research/PREREG_TEMPLATE.md（§0-§8 全节）+ **W6 血统整体继承**（research/TRIAL_LABOR_W6_PREREG.md 冻结机械：§2 GATE/VOL/YANG/VCONF 四门序列定义+§3 生成/Sobol/去重/初筛/判决机械+§4 判据 G1'v2/G2v2/DSR/PBO 双 nulls+E[FP]+语法登记簿——**本件只写增量面，继承面按 W6 逐字引用**）；跑前 commit 冻结；跑后只回填 §7/§8，要改判据要重跑。
> 令源：CEO 直令 O-2026-09-27-2245（千人试用期大考）+ O-2026-09-27-2250 常设律（firm/TRIAL_LABOR_LAW.md v1.0「以后不要我提醒」）+ O-20260928-1522（CEO 研究导向：国内民俗判据优先立项·科学照常验证）；波级票=冻结步开票（W6 先例 T-2026-09-29-117）。
> 统摄律：firm/RANDOM_LARGE_SAMPLE_LAW v1.0 + firm/REFINE_BENCH_LAW v1.0 + TRIAL_LABOR_LAW §1-§6 + research/BACKTEST_SCIENCE.md v2 + BACKTEST_PLAN.md 三铁律 + COMPUTE_AUDIT.md 批件纪律 + O-1820(3) consumer_plan 池 schema 必填律。
> **本件=波级（Wave-level）预注册**：生成语法/漏斗规则/判据全冻结；sub-wave 追加面一律走 §9 append-confirm。
> **本波≠W1/MASS/W2-W6 语法血统**：新语法面=**连涨连跌确认门 STREAK ∈ {none, up_streak2, down_streak2}** 叠加层（扩容面）→ 新语法新 sha16（≠W1 a2fa15f4b06b3c40 ≠MASS 96269ebe766c3fc2 ≠W2 1dd3d9579235cec ≠W3 cc59eab79db53436 ≠W4 d498e9343ee57460 ≠W5 29720178c39425de ≠W6 2d395f5f8e7d16cb；W7 sha=w7_grammar.json 序列化时点新算·构造性相异），同语法禁重跑（TRIAL_LABOR_LAW §4）经新语法面合法开法。
> 外源证据链（借力律 O-1721 先扫后研）：research/digests/DIGEST-20260929-w7-streak-supply-scan.md（连涨连跌口诀族〔方向矛盾如实=两向殉死〕+仓内短期反转三源主证〔T-22 分段/T-73 s2 反转律/O-2330 CEO 超跌反弹实测〕+门裁定 PASS+边界三披露）。

## §0 批件身份。【跑前。】

- 批名/批号：**TRIAL_LABOR_W7**（千人试用期大考·wave-7·连涨连跌确认门）。三层漏斗子批（dict schema 唯一）：
  - **TRIAL_LAB_W7_SCREEN**（s2 廉价初筛批）：batch_trials = 去重后候选数 + 200 null（每格 1 trial）；raw 5,000 → 去重门后 ≥3,000 distinct——5,000=上限非凑数；
  - **TRIAL_LAB_W7_JUDGE**（s3 全量判决批）：batch_trials = 初筛存活者数。
  - 两批 evidence_cutoff 均 **2026-09-22**（P-5C 冻结口径 binding·双轴同降）。
- 认领：起草面无票无认领（本 draft）；冻结步开票+同轮认领（W5/W6 先例）；认领依据=TRIAL_LABOR_LAW §1 常供律例行供给步，无需 GM 另署名 per W2-W6 先例。
- 部门归属：dept:策略（生成引棒供给面）+ dept:研究（判决漏斗面）joint。
- 算力预算：生成去重=分钟级单机（76 函数值域表枚举 5,000 抽样）；初筛面 ≥5,200 格量级（leg-L 6m 全史）→ 估小时级池批 @ workers 池（>5min 一律入 results/runnable_pool.json·O-2100 执行面分离；每 50 候选一 checkpoint）；判决面=分钟级簇（双 nulls 重采样重量级·deep-panel 宿主物理腿=RAM 门 r354 三采样例）。
- **供结契约如实披露**：A=在册六员工模板族 500 抽（常供线维护面）；B=流派战法模板大考 4,500 抽 → 76 函数均摊 ≈59.2 抽/函数（六波面累计 ≥22 抽/函数下限沿 W5/W6 口径）；C=因子普查存活腿族=**本波禁碰**（W2 §9.1 declare 独占·anti-dup hard law）；D=judged 供结变体面=**generate 时点实读 declare 窗——七源**（W1-JUDGE+MASS judged+W2-JUDGE+W3-JUDGE+W4-JUDGE+W5-JUDGE+**W6-JUDGE 已落地**）逐源 declare 不可得零行如实（W6-JUDGE 0 存活+intake 零收录=变体供给零行如实）。**48h CEO 呈报钟**：随判决面落地起计（票面持有；非本起草时点计）。
- **W7-JUDGE 物理序门**：判决面排在其余在飞判决面之后（RAM r354 三采样门+串行 flip 既有纪律自动实现）；SCREEN 面=CPU 池面先行烧合法（RAM 零占用）。
- **consumer_plan（O-1820(3) 必填）**：W7 产物消费面=TRIAL_LAB_W7_JUDGE verdict 面 → s4 intake（D6 绑定门→STRATEGY_LIBRARY 注册行+TRIAL-<FAMILY>-<NN> 纸盘上岗）→ 48h CEO 呈报面+scorecard/CEO 一页纸消费；SCREEN null p95=下一波 prereg 判读参照带（W1-W6 0.5116/0.5164 带内延续）。

## §1 伪 α 机制段。【四选一+论证·D6 门槛。】

- **供给时 A（在册六员工模板精炼）**：[x] 行为偏差（主）——风险源价（辅）——母体机器同承继 W1-W6 §1。本波主张：**连涨连跌日条件化入场许可下存在可检出新增益变体**——「三连阳」/「连跌必反弹」=A 股最典型连涨连跌民俗判据族（CEO 1522 导向：国内打法优先立项·民俗判据形式化为数值门正例）：信号池溢价由「顺连涨/逆连跌确认日入场者」向「未确认（无 streak 态）日入场者」收取；**代价支付者=无连续方向确认日的先入场者**（多日方向一致性=参与度/承诺度证据；「谁付出代价」答案）。
- **供给时 B（流派战法模板大考）**：[x] 逐流派四选一映射同 W1 §1（21 流派·负先验标签如实随格携带）。本波主张：冻结工厂库在 Sobol 低差异抽样轴系下、政体门×波动门×阳线门×量能门×**连涨连跌门**×初始止损×轴系交互存在仅大规模混水摸深抽样可检出的 α 口。
- **STREAK 门机制注记（本波新增面·冻结定义）**：STREAK=入场许可的条件化叠加层（非引擎出场规则）——**行为确认过滤面**：信号日连续同向收盘状态（close-over-close 两日连向=多日方向一致性确认）。**STREAK 面≠GATE 趋势面≠VOL 波动面≠YANG 阳线面（单日 intraday body）≠VCONF 量能面**——探针实证（r206）：yang∧up_streak 751/yang∧down_streak 104/red∧up_streak 93/red∧down_streak 713 **四格全非空非支配**（对角重合 751/713 vs 非对角 104/93=streak 载多日信息非 yang 单日 intraday 同构；103+93 格=纯新增可检空间）——**五门交互=新可检空间**。两向殉死如实：「三连阳追涨」（延续）vs「连涨三日不追高」（过热反转）/「连跌抢反弹」（反转）vs「下跌趋势不接飞刀」（延续）——方向先验两向开放，主证让位仓内探针+普查。
- **D6 同族相关性准入（W1 大考面适配声明整体沿用）**：①≥0.999 塌缩=生成段硬绑门；②0.7 线=注册级全候选审计披露；存活者簇内行缩留最优。
- 排除簿（anti-dredging·W1-W6 同例·**judged 七源 declare 窗+screen 七清单**）：**已判精确核禁重跑**——cell key=(template, params, axis_config, initial_stop, gate, vol, yang, vconf, **streak**)；**语义恒等匹配=前波 cell key 无 streak 轴者按 streak=none 补全类匹**；全部既有已判格（judged 七源=W1/MASS/W2/W3/W4/W5/W6·判负函数默认参数原批）+**七清单**（W1_screen 149+W2_screen 404+MASS 166+W3_screen 513+W4_screen 461+W5_screen 372+W6_screen 293）generate 时点实读消费→生成段排除并逐格留痕；**streak∈{up_streak2, down_streak2} 面（与任意四门组合）=新语法面合法开法**。

## §2 数据与面板。【跑前探针事实，非结果。】

- 宽基/池：**core48** + 判决段深轴 **T-18 增长截面深面板**（W6 §2 同源·loader import-face 复用禁重写）。
- **STREAK 门序列（本波新增面·跑前探针事实 r206 实读·探针件=results/_r206bmc_streakgate_probe.py+事实件 _r206bmc_streakgate_probe_facts.json）**：信号日连向态=**close(d) vs close(d-1) 与 close(d-1) vs close(d-2) 双重同向**；**up_streak2**=连涨两日收盘（d-1<d 且 d-2<d-1）/**down_streak2**=连跌两日收盘（镜像）/**neither**=无连续同向（含平盘/交替）=门关；判定在**信号日 d 收盘信息集**（T+1 因果律·零前瞻·入场=d+1 开盘）；**2 bar 预热窗 gate-closed 诚实**（首 2 bar 不可判——**全门族最短预热**：vs YANG 0/VCONF 19/VOL 519=GATE 199 结构性中间位改善面如实注记）。510300 全史面（3,483 行·2012-05-28→2026-09-22 cutoff·W4-W6 探针基同锚）：**可判日 3,481**；up_streak 844（可判日 24.2%）/down_streak 817（23.5%）/**neither 1,820（52.3%）=门关面过半如实披露（窄门面）**；streak 日内 up 率 50.81%（up/down 平衡面·近硬币）；政体条件面 bull up 率 60.44%（524 up/343 down）/bear up 率 40.3%（320/474）=**政体持续性结构**（bull 日连涨占优/bear 日连跌占优=streak×gate 非独立载信息）；波动条件面 calm 52.04%/wild 49.84%（近独立）；阳线条件面 yang 日 up_streak 751/down 104（87.84% up）/red 日 up 93/down 713（11.54% up）=**强共动但非同构**（非对角 197 格=独立信息实证）；量能条件面 surge 日 54.93% up/dry 日 46.37% up（弱共动）；**五门 32 格开窗计数全非空**（min 3〔bear|calm|yang|surge|down〕-max 150·区间 3-150=五门交互面可检空间实证·**min 3 格样本薄如实披露**）；**七极端日 4 down + 2 up + 1 neither**（down 面=2015-07-27/2016-01-04/2025-04-07/2026-01-19 危机日敞口在册；up 面=2024-09-24/09-30 政策脉冲日；例外 2024-02-28=neither 如实）——vs W6 VCONF 门 6 surge：**down_streak 面危机日敞口保持（反转候选）/up_streak 面脉冲日敞口保持（延续候选）**；core48 员级 up 率 min 40.95%/median 49.61%/max 66.15%（48 员全非退化·load_core() 真名册面）。
- **GATE/VOL/YANG/VCONF 门序列（W3/W4/W5/W6 冻结定义整体继承·逐字引用 W6 §2）**；**evidence_cutoff=2026-09-22**（P-5C 冻结口径 binding·双轴同降·W6 §2 机械整体沿用·import scripts/p5c_virtual_timepoint.py 禁重实现）。
- 数据完备门（fail-closed，不过即 VOID 中止零产出）：**G-PANEL/G-CENSUS/G-ANCHOR/G-MANIFEST/G-EXCLUDE/G-VOL/G-YANG/G-VCONF 整体继承 W6 §2**+**G-STREAK（本波新增）**：连向序列点时完整性断言（**预热窗==2 断言+可判日==3,481+up_streak 计数==844/down_streak==817/neither==1,820 探针锚定+yang×streak 交叉四格锚定 {yang∧up 751, red∧down 713} 下界+五门 32 格全非空断言+截断后末行==cutoff**）。

## §3 方法论。【冻结。】

- **生成语法（全冻结——零新信号发明）**：原语面同 W6 §3（strategies/ 86 函数/13 模块·grid 模块 4 业务函数排除如实披露·时 A=在册六员工模板·时 B=其余 76 函数）；轴系=W6 九元组全继承+本波扩容面：入场过滤 ∈ {none, depth_thresh, amplitude, liquidity, trend_slope, dual_window, fundamental_mask}（7）；出场 ∈ {template_default, CE 注册出场, time_stop_5d/7d/10d/20d, trailing_stop, profit_ladder}；仓位 ∈ {equal_weight, inverse_vol, cap20, regime_delever}（4）；时机 ∈ {daily_signal, weekly_grid}（2）；初始止损叠加 ∈ {none, p3, p5, p8, p12, a15, a20, a25}（8）；GATE ∈ {none, bull, bear}；VOL ∈ {none, calm, wild}；YANG ∈ {none, first_yang}；VCONF ∈ {none, volume_surge, volume_dry}；**连涨连跌确认门 STREAK ∈ {none, up_streak2, down_streak2}（本波新增面·§2 冻结定义）——十元组 R/X/S/T/STOP/GATE/VOL/YANG/VCONF/STREAK = 580,608 轴组合/模板**（W6=193,536·×3=扩容面）。
- **STREAK 门叠加层（扩容面·冻结定义）**：门态在**信号日 d 收盘信息集**上判定（§2 序列）；**up_streak2**=仅连涨两日收盘态许入场；**down_streak2**=仅连跌两日收盘态许入场；**none**=无门（W6 语义基线）；门只作用于**入场许可**（有效信号置零·grammar 层实现），出场逻辑零改动；**2 bar 预热窗 gate-closed 诚实**；五门独立叠加（**五门=五条件交**）。
- 随机抽样（Sobol 沿用=W3-W6 declare 血统）：MASS_TRIAL_W1 sample_draws 范式 import-face 复用禁重写；**十元组**轴组合独立 RNG 流；N=500/时 A+4,500/时 B；**seed 基草稿泊位 `trial_labor_w7_gen`=20305000 / `trial_labor_w7_scrnull`=20305500 / `trial_labor_w7_unc`=20306000**（起草时点三步律预检已过：registry 99 键零占用+首元素互异+全仓扫描 2 命中=data volume 列巧合非种子面；**冻结步依法复验**——撞带重取先例在册）；SEED_REGISTRY 本冻结同 commit 登记律·R250 一步例。
- **去重门（T-84 s3）**：W6 §3 逐字继承（持仓恒等指纹+|corr|≥0.999 塌缩+塌缩计数如实披露）。
- **s2 廉价初筛**：每 distinct 候选 leg-L 6m 全史一回测→beat6m（W1 13bp base·T+1·五门面随格携带）。
- **初筛 null 族**：K=200 同构随机信号候选（**streak 门腿并入同网格同参数空间 draw**·BACKTEST_PLAN 三铁律）；seed=`trial_labor_w7_scrnull`=20305500（派生 [20305500, i]）。
- **初筛判线（跑前写死）**：存活 iff beat6m > null 族 p95（程序冻结·零手挑阈）。
- **s3 全量判决**：双腿×成本 {base x1, x2}×政体分段+双 nulls（B=2000 block bootstrap+P=2000 sign-flip）·seed=`trial_labor_w7_unc`=20306000（派生 [20306000, cell_idx]）；**五门面新增披露列=gate×vol×yang×vconf×streak 交互分段计数**（W6 四门面扩容·面板级）+止损披露面（W5 judge 切片已接线面沿用）。
- **样本充足律**：n_eff≥100 起点×三段各≥100（na 桶诚实）——不越→insufficient-sample 禁判 pass。**窄门面注记**：streak 条件格（up_streak2/down_streak2）入场日 ~24%/23.5% 开窗率 vs VCONF ~50%——分段样本量按实际格面如实判读，insufficient 门槛不放松。
- 描述条款/成本口径/账本：W6 §3 逐字继承（append_ledger TRIAL_LAB_W7_SCREEN/TRIAL_LAB_W7_JUDGE·prev=活锚头实读禁手抄）。

## §4 判据。【跑前写死——共享库引用零手抄。】

- **G1' v2 = science_gates.g1_prime_v2(...)** 同 W6 逐字；**G2 注册资格 v2 = science_gates.g2_registration_v2(g1_pass, dsr, pbo)**——**n_trials=累计账本总试验数（活锚头实读·跨波不重置）——r206 起草时点活锚头实读 333,432**（W6-JUDGE 落地后链头·W6 双计污染已反转净·r206 复验 linear）+本波 SCREEN 格并入后折减。
- **波级多重检验税披露（O-2245 强制）**：N_wave 逐批披露+E[FP]=0.05×N_wave_judged_cells+波级 PBO 聚合读数另列+**语法消耗登记簿（research/TRIAL_GRAMMAR_LEDGER.md·append-only）wave-7 行**——同语法禁重跑。
- **s4 intake（上岗线）**：G2 eligible→D6 绑定门→STRATEGY_LIBRARY 注册行+TRIAL-<FAMILY>-<NN> 袖盘上岗+48h 内 CEO 呈报；**实际存活数按实际划（零存活=合法判决照报不翻案）**。

## §5 跑前预测。【写死于跑前·≥3 条·含极端日先验。】

1. **去重率**：raw 5,000 → distinct ∈ [2,800, 4,600]（W3-W6 同口径 3,552/3,810/3,926/3,952；streak∈{up,down} 占 2/3 新空间摊低跨波重复·streak=none∩前波已判面排除簿拦截→缩率预期 [8%, 44%]）。
2. **null 底与初筛通过率**：null 族 beat6m 中位 <0.50；p95 ∈ [0.42, 0.62]（六波带 0.5116-0.5196 内延续）；初筛存活率 ∈ [2%, 15%] → 存活 [100, 750] 格。
3. **判决面**：G1' 过线 [0, 60]；G2 eligible [0, 5]——模态结局=零或近零（DSR 累计 N≥333k+ 折减极重·七批同门实证；零存活=合法产出如实报）。
4. **STREAK 面方向先验（本波新增面·方向可证伪）**：up_streak2 与 down_streak2 双向开放读数——仓内主证=短期反转结构（T-22 分段/T-73 反转律/O-2330 CEO 超跌反弹实测=**down_streak→反弹候选面有直接仓内锚**）vs 延续面（bull 政体 up_streak 60.44% 政体持续性=risk-source 延续锚）；口诀族内部方向矛盾（「连跌抢反弹」vs「不接飞刀」）=两向殉死如实；**五门交互=开放面无直接外源证据**（gate×vol×yang×vconf×streak 叠加增益是否存在=本波真问题·读数非先验）。
5. **极端日先验（硬界三件套 c）**：数据窗内极端微观结构日在册（2015-07 股灾/2016-01 熔断/2024-02 微盘崩/2024-09-24·09-30 政策脉冲/2025-04-07 外生缺口/2026-01-19 极端量日）——**down_streak 面七极端日 4 在场**（危机日敞口保持）→整窗判读+dd 线非单点 max 检测线；**up_streak 面 2 在场**（脉冲日敞口）；例外 2024-02-28=neither 关门如实；危机日计数+止损触发日计数+五门面计数列随格披露。

## §6 产物

- runner：`scripts/trial_labor_w7.py`（subcommands: generate/screen/judge/intake/status/selftest；import-face 复用 trial_labor_w1-w6 全链+mass_trial_w1 Sobol+strategies/ 工厂+engine/backtester 引擎腿禁重写要改；selftest=hermetic 合成面离线腿+STREAK 门因果腿（信号日信息集·2 bar 预热窗 gate-closed·streak=none==W6 语义基线恒等腿）+五门交叠腿（五条件交正确性）+门序列点时完整性腿（G-STREAK 探针锚断言·up 844/down 817/neither 1,820/预热窗==2）；STREAK 门=grammar 层实现，engine/exit_rules.py 零触碰）。
- 产物：`results/trial_labor_w7/`——w7_grammar.json（语法全套·十元组轴网格+去重审计段）；w7_candidates.json（全量候选 provenance+D6 披露列+五门面序列+streak 面序列）；w7_screen.json（null 族 floor+全格 beat6m 分布+STREAK 面+五门交互分段存活统计）；w7_screen_cells.csv（小件入 git）；w7_judge.json（判决全面 G1'/G2/DSR/PBO/E[FP]·五门交互分段披露）；w7_intake.json（上岗 D6 裁定）；全部顶层 evidence_cutoff+audit 段。
- 语法消耗登记簿：`research/TRIAL_GRAMMAR_LEDGER.md`（append-only·wave-7 行）。
- 池路由：SCREEN/JUDGE >5min 入池（O-2100）；lane_owner=null（core48+T-18 in-repo 双机可跑）；workers_plan ≥floor(核数/0.8) BelowNormal；RAM 门禁 r354 三采样例；池条目必带 consumer_plan+前置产物同 commit 入仓（pit-90 律）。

## §7 跑后实证。【跑前必须为空——占位纪律：写数字即造假。】

（一次定稿；工程修复重跑双跑留痕如实账）

## §8 批后复盘。【必填 §7-T。】

（预测对账门禁链损耗账追加行；判决面结果 48h 内呈 CEO）

## §9 追加冻结节。【append-only·每 sub-wave 一冻。】

- **W2-C 族面交接注记（anti-dup·W6 同例沿用）**：因子普查存活腿族=W2 §9.1 declare 独占面——本波 §0 declare 禁碰。
- **judged 供结 generate 时点 declare 窗**：七判决批（W1/MASS/W2/W3/W4/W5/W6）+W6_screen 存活清单 293 落地后、本波 generate 跑前=declare 窗（实读产物并表·逐源行数披露）；generate 已跑后落地者不入本波。
- **runner 构建切片开放**（W3-W6 先例）：prereg 冻结后 runner build+语法序列化+TRIAL_GRAMMAR_LEDGER wave-7 行+池条目（TRIAL-LABOR-W7-GENERATE）=开放任何健康机器认领（单写者 per 产物件）；判决物理腿=deep-panel 宿主+RAM r354+W7-JUDGE 序门。
- **冻结触发器与步骤（本 draft 状态横幅）**：触发器=W6 全链消费落地（✓ 2026-09-29 08:14:22·judge+intake 零存活照报+ledger 333,432 linear）∧判官零在飞批（✓ pool 110/110 done）；冻结步=commit 冻结+SEED_REGISTRY 三键同 commit（泊位 20305000/20305500/20306000·冻结时点三步律复验·撞带重取+横幅注记）+波级票开票+同轮认领+F-04 MSG；冻结前本件零烧批效力。
