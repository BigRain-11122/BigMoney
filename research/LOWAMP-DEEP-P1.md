# LOWAMP-DEEP-P1 预注册 · 深轴低振幅横截面日再平衡**新家族**主考格判决批

> 令链血统：**CEO 直令 O-20261002-2115 §一.2**（「深轴低振幅新家族（淬炼链）：P3 探索面 +55~60%（67 笔·深轴）按见即淬炼律预注册成新家族——一出生即主考格、出场轴双件门内置、67 笔面为主判。REFINE_BENCH_LAW 既有面，本令点名提速入池」）→ T-2026-10-02-147（bm-b 认领同轮·CEO immediate 律）。淬炼法源：firm/REFINE_BENCH_LAW.md v1.0 §1 触发律②勘探领跑（双 nulls 支持的 exploration lead——LOWAMP-FURNACE 双 nulls 族 + P3 判决批探索腿双重在案）。
> 探索面实证（升格证据·非本批结果）：LOWAMP-P3 deep 轴 8 胞（hold-through+ExitPatch 修正机件·r522 根因修正面）——**LAD-EDGE 前身 LA-EDGE|deep|base：ret_full +60.43%·Sharpe 1.066348·n_trades=67·maxDD −5.47%**（本批主判面=该 67 笔面的主考格重判）；x2 面 +55.50% 存活；LA-REP|deep +62.54%/1.115/72 笔；LA-T3|deep +67.33%/189 笔。P3 主判（legacy 轴 headline）判负闭合 lowamp_daily_xs（族设计面·律 A 0% 缺省出场证明机件无恙）——**本批不开闭族翻案**：lowamp_daily_xs 裁决照旧；本批=新家族键 + 新证据面（见 §1 M3 delta 声明）。
> 模板=research/PREREG_TEMPLATE.md；判据节调 science_gates.g1_prime_v2/g2_registration_v2 共享库禁手抄判线；跑前 commit 冻结；跑后只回填 §7/§8；LOWAMP-P1/P2/P3 冻结批零重跑铁律不变。
> 部门=dept:策略（族规格）+研究（judgment 面）；lane=Money02 deep 面板在位机（bm-b 在位 48/48·R31 数据本地律）。

## §0 批件身份【必填·跑前】

- 批名/批号：**LOWAMP-DEEP-P1**。**N_eff=2,008**＝judged cells 4 × 判面 2（base+x2）+ deep 宇宙 same-mask nulls 2,000；sensitivity Sobol 腿=描述面**不计 N_eff**（§3）。扩容即买单。
- 账本面：finalize 步 `science_gates.append_ledger(batch_name="LOWAMP-DEEP-P1", batch_trials=2008, file_name="results/lowamp_deep_p1/lowamp_deep_p1_results.json", evidence_cutoff="2026-09-22")`（dict schema 唯一禁手抄 prev·r509 序律：块持久化进产物件后才写 guard）。
- 算力预算：**长活入池**（>5min 一律 runnable_pool·O-20260924-2100 s2）——池单元=8 cell-face（每单元=该 cell 全起点 shards + cont face）+ NULLS（2,000 draws·checkpoint 断点）+ SENS（500 draws）共 **10 池条目**；workers_plan={"workers": 12, "priority": "BelowNormal"}；checkpoint 逐单元 JSONL done-key skip；**跑批宿主门=Money02 deep 面板在位**（dir_nonempty=Money02/data/cache/t18_deep_panel/ohlcv·48 文件）；批报告必带 audit 段。
- 池位（O-2115 §三验收 10-08 面）：本批 prereg 冻结+池登记即达「②深轴新家族 prereg 在池」验收面；烧毕→finalize→E1→消费四段假期窗内走完（10-09 开市前）。

## §0.5 禁开方向硬闸【必填·跑前·D-20260930-41 §1.2】

- 跑前过闸：`python Tools/banned_direction_gate.py --prereg research/LOWAMP-DEEP-P1.md` → 退出 0=放行（fail-closed）·冻结 commit 内回执。
- 人工预读结论：**零命中预期**——本批机制与 LOWAMP-P1/P2/P3 冻结面逐字同族（横截面风险度量（振幅升序）选低+常开+日频再平衡），P1/P2/P3 三批过闸同判；唯一新增面=宇宙切换（T-18 deep 面板）非机制新增；禁向词面不在本件复述（机器闸为准·r483 清洗律）。

## §0.6 出场轴显式声明【O-20261001-1108 立法·TRIAL_LABOR_LAW §4·O-2115 点名「双件门内置」】

- **出场轴=②持有到底（ALWAYS-ON hold-through）**：族定义=常开持有——成员**只因横截面选择轮换离场**（当日跌出 Top-N 最低振幅入选集=entry≤0 信号出场·t22 `_run_cell` 惯例逐字），**无价格类出场**（无止盈/无止损/无衰减踢出/无亏损时限/无持有上限）。
- **引擎缺省出场栈显式禁用【双通道逐键申报·r522 根因修正面·P3 §0.6 逐字继承】**：
  - **params 通道（桥内 4 键）**：`take_profit_levels=()`（空梯）·`trailing_stop_activate=1e12`（trailing 永不激活）·`initial_stop=-1.0`（止损价=0）·`time_decay_period=10**9`（永不）；
  - **ExitPatch 通道（桥外 2 键·live/paper.py ExitConfig 工厂补丁）**：`loss_time_days=10**9`·`global_hard_limit=10**9`；
  - 两通道键集**互斥断言**入 runner selftest（F11 死信回归守卫）；`exit_signal`=entry≤0 全矩阵；**engine/ 零触碰**；T+1 执行与成本模型=引擎正典不变。
- **第二件门=律 A 烧后出场原因普查**（LOWAMP-P2 §9 立法·P3 首载实证 0%）：finalize 步对 headline 以同一冻结机件重跑逐符号捕获每笔出场 reason——hold-through 面上**唯一合法 reason=signal_reversal**；**缺省栈出场占比 >20%（CENSUS_BLOCK_SHARE=0.20 跑前写死）→ verdict=consumption-blocked（判决消费自动封锁）**。普查块入结果 JSON gates.exit_census。

## §1 α 机制段【必填·D6】

- 机制勾选：**行为偏差**（主：彩票偏好/注意力稀缺——市场对手盘系统性超配高振幅「彩票型」资产〔MAX 效应族〕，低振幅资产长期低配=低波动异象；代价支付者=追高波动的行为对手盘）＋**结构性**（辅：机构委托条款/跟踪误差约束令其无法超配低振幅成员——「基准即枷锁」）——P3 §1 逐字继承（同族机制零新增，新面=宇宙）。
- **散户凭什么赢【§1.2】**：**制度/容量**——低振幅倾斜散户规模容量无限、零杠杆需求；不重跑任何机构结论（低波动异象=公开文献常识面引用）；例外三问=本账户独有约束（场内 ETF 直接持有·真实成本·本市场 2013-2026 deep 窗）成立。
- **同族相关性准入检查【必填·D6】**：入批前 probe 步计算 headline（LAD-EDGE deep·hold-through 面）日收益序列 vs **在册六员全部成员**日收益序列逐对 max|corr|；**max|corr| ≥ 0.7 → 拒收 fail-closed 禁烧**（数值与逐对清单 probe 件落盘后方可点火）。先证：P1=0.1688·P2=0.1738·P3 fresh probe 实测为准（deep 宇宙低振幅选择 vs 在册成员预期低相关；fail=拒烧）。
- M1 t 面【必填申报】：`science_gates.t_from_sharpe(sharpe_full, n_periods)` 派生面（headline cell）；判据=`science_gates.m1_t_value_gate`（H/L/Z 门槛 **t≥3.0**）。
- M3 闭合族对号与**新证据 delta 声明**【new_evidence_new_prereg 重开通道·非翻案】：family_key=**lowamp_deep_xs**（新键·CLOSED_FAMILIES 七在册键无一命中=open 照跑）；已闭合 lowamp_daily_xs（P3 legacy 轴主判负）**裁决照旧不开**；本批新证据增量声明=①**新宇宙面**（T-18 deep 面板 48 员·2013-06-17 起——含 2015 股灾/2016-2018 熊市/2018-2019 磨底七年级历史段，legacy 轴 2020 起算窗从未测过）②**自有 null 池**（deep 宇宙 same-mask hold-through nulls——全机队零存量：P3 nulls=legacy 轴绑定·t18_deep_reval nulls=随机入场×缺省出场异构造）③**67 笔探索领跑面**（O-2115 点名主判）。族间对号同 P1/P2/P3（GRID-SLEEVE 带状执行族无关·CN-DIV-LOWVOL-ROT=monthly-rotation 族·本族=日频横截面振幅排序族）。

## §2 数据与面板【必填·跑前探针事实，非结果】

- 宇宙/池：**T-18 deep 面板**（manifest PASS·48 员·panel_start=2013-06-17·单轴批——legacy 轴不在本批面）。
- 价格面：deep 轴=`t22_virtual_timepoints._load_axis_prices('deep')` 逐字（manifest 门+19 受影响员 adjusted view 优先·GF 硬门 19/19）；raw 面权威性不动（D2 锁盒零改写）；**amount=volume×close proxy 面如实披露**（t22 先例）。
- **数据锚面定义四元组【G-ANCHOR-FACE】**：deep 轴=`Money02/data/cache/t18_deep_panel/ohlcv/<code>.parquet`＋`pd.read_parquet`（经 t22 loader）＋起算 2013-06-17＋预热 252td；政体标签=deep 面板自带 510300 列 `t22_virtual_timepoints.regime_proxy(close['510300'])`（deep 面板含 510300 实证 48 文件在册）。
- 窗口与 **evidence_cutoff=2026-09-22**（P 族系 D2 前向锁盒·P1/P2/P3 同界逐字绑定；cutoff 后新 bar 锁定不得回流）；结果 JSON 顶层 `evidence_cutoff` + `science_gates.cutoff_meta("2026-09-22")`（缺字段=C2 VIOLATION）。
- 起点集：**T-22 冻结枚举律逐字**——`enumerate_starts`（pos≥252td ∧ ≥126td 前瞻 ∧ 当日上市成员数≥24）确定性全枚举；**G-CENSUS 门：起点数逐位=={deep: 1,506}**（P2 零修正案锚读数继承·同 cutoff 截断同枚举）。
- 数据完备门（不过门禁跑·probe fail-closed）：①deep manifest PASS ∧ 48 员 ∧ ohlcv 48 文件；②adjusted view 19/19 在位；③cutoff 截断后面板末行==2026-09-22；④零重复日期+单调；⑤G-CENSUS。
- **流动性/可交易闸（P 族系继承）**：选择资格=有效 amp（满 W 窗史）∧ 当日 close notna ∧ volume>0 ∧ amount>0 ∧ **amt20_median ≥ ¥50,000,000**（proxy 面如实披露）。

## §3 方法学【必填·冻结】

- **信号定义（冻结·P 族系逐字）**：amp(t)＝近 W 交易日收盘-收盘日收益滚动标准差（`min_periods=W`·严格因果）；横截面升序排名取 **Top-N 最低振幅**；权重 **invvol**（w_i∝1/amp_i·归一）或 **eq**（1/N）；**常开**（零前置条件）；**日频再平衡**（信号日 T 收盘算、引擎正典 T+1 执行）。
- **judged cells 4（跑前写死·O-2115「67 笔面为主判」）**：①**LAD-EDGE（HEADLINE）**：W=104·N=2·invvol——P3 探索领跑 67 笔面主考格重判；②**LAD-EDGE-EQ**：W=104·N=2·eq；③**LAD-REP**：W=89·N=2·invvol——P3 探索面升格；④**LAD-REP-EQ**：W=89·N=2·eq。
- **sizing 轴缺陷披露与修正（本批继承面·r596 bm-b 实弹发现）**：P3 runner `build_signal` 无 sizing 参数——judged cells 恒走 invvol、声明 eq 的 LA-EQ 胞=LA-REP 幽灵孪生（两轴 8 胞面全指标 6 位小数恒等·含 returns 序列实证）；**P3 裁决面无恙**（headline LA-REP 与 LA-EDGE 声明 invvol 跑的即 invvol·sens 腿自有真 eq 分支）；本批 runner 修正 sizing 管路（build_signal sizing 参数化）+**真 eq 面（LAD-EDGE-EQ/LAD-REP-EQ）深宇宙首次实测**+selftest F3b 回归腿+probe 活面 guard——本批 judged 家族矩阵四胞**两两真分化**，P3 的幽灵孪生面不再重演。
- **执行语义【§0.6 出场轴逐字】**：entry_signal=当日入选 ∧ exit_signal=entry≤0（选择轮换出场·全矩阵注入）→ `engine.run_backtest`（T+1·成本模型·双通道缺省栈显式禁用）→ 持有到底（价格类出场零触发·成员仅因跌出 Top-N 离场）；x2 面=`CostPatch(2.0)` 乘数；每起点 fresh-entry 洁净切片（t22 先例）；逐符号子账户分解+entry_size_scale 权重映射（P3 docstring 披露面逐字）。
- **窗族 {6m=126·12m=252·24m=504}**：最长窗一次跑+同曲线切片（P-5 律）；**主判窗=12m 完整窗**·partial 窗如实标记；被动基线=起点日已上市成员等权 B&H 同窗（t22 逐字）·beat_k=ret_k>p_ret_k。
- **null 对照（≥2,000 三族全律·deep 宇宙首个 same-mask hold-through null 池）**：①**null_pool（G1' skill line 源）**：K=2,000 **same-mask 随机选择 null**——每日同一资格掩码宇宙（**headline LAD-EDGE 的 W=104 掩码**·同 N=2·同执行·eq 权·`rng([20337500, k])` 子流律·DEEP-P1 新种子带 20337000/20337500 disjoint 实证）内均匀随机选 2 员，deep 面板全面板模拟取 Sharpe 分布（μ_null/σ_null 入 skill_line_v2）；掩码恒等断言（G-MASK：null 日宇宙==真实 cell 日宇宙逐位·构造即恒等）。②**block bootstrap B=2,000**（headline 日收益·块长 21td）＋③**sign-flip permutation P=2,000**（RANDOM_LARGE_SAMPLE_LAW §3 逐字·双法并列）。
- **sensitivity 腿（§2.2 履约·描述面零判定宣称）**：N=500 空间填充均匀抽取 over（W∈[77,104] 整数·N∈{2,3}·sizing∈{invvol,eq}·gate=常开固定·**出场轴=§0.6 hold-through 同面**），**deep 面板**全面板单跑（P3 sens=legacy 面本批=deep 面首个 sens 存量），产物=Sharpe/均值/maxDD 分布描述列，**不计 N_eff、不设门、禁幸存者宣称**；`rng([20337000, k])`。
- **政体分段**：每起点 regime 标签（deep 面板 510300 列 t22 3-way proxy）→ 分段统计；**G-SEG 覆盖门：bear/bull/chop 各 ≥50 起点（12m 完整窗）**——不过=verdict=**insufficient-sample**。
- **被动面（skill line 被动项·单源律 O-2250）**：deep 宇宙被动基线=**首 bar 在场的全部 deep 成员等权 B&H**（各员归一到首 bar 收盘·持有至 cutoff 同一截断面板）Sharpe——**finalize 从面板 DERIVE 传入 `passive_override`**（REPO_CALENDAR_P2 附加通道·零手抄）；t18_deep_reval ew48_buyhold 先证 0.3612 同量级预期（构造近似面·§5 预测带）。
- 成本口径声明【CN-C7】：**ETF=26.082bp/往返**（`knowledge/cost_spec.py X1_RATE` 单边 **import 派生禁手抄**·runner 断言恒等）；¥1,000,000 账户口径申报；V2 ADV 滑点面对 ETF 日频零售量级=不适用如实注记。
- **反重复披露（票面 anti-dup）**：LOWAMP-P1/P2/P3 冻结批零重跑不变；本批=W∈[77,104]×N∈{2,3}×sizing 带在 **deep 宇宙面**的首个主考格消费（core48 宇宙面存量维持禁重跑——LOWAMP-P1 行约束照旧）；P3 deep 探索腿 8 胞=探索面证据引用**非本批判据来源**——本批两 invvol 胞为**升格重判**（淬炼漏斗 census→judged 升格先例=REFINE_BENCH_STOCK_REV_P2·O-2115 明令「P3 探索面…预注册成新家族」），两 eq 胞+nulls+sens=全新面零存量；**确定性重现断言**=finalize 对两 invvol 胞逐字段比对 P3 deep 工件（sharpe/ret/max_dd/n_trades/n_entries/n_days/nav_last 逐位恒等·漂移即 abort）——升格面证据链完整性机证。

## §4 判据【必填·跑前写死，禁看结果调线】

- **G1' v2 = `science_gates.g1_prime_v2(sharpe_full, returns, batch_cells=2008, pool='core48', n_trades, n_entries, null_pool=<本批 2,000 deep same-mask own 池>, passive_override=<deep EW B&H derive>)`**（headline=LAD-EDGE·**deep 轴全面板** 2013-06-17→2026-09-22 连续单跑·hold-through 面）：全期 Sharpe > skill_line_v2（数据驱动=max(deep 被动+0.10, μ_null+σ_null·√(2·ln N_eff))·N_eff=净额账本 head+2,008·账本活读）∧ 平稳 bootstrap CI 下界>0 ∧ entries≥30（F6 双口径）；逐列披露 skill_line/bootstrap_ci/trade_gate/passive_face 全输入。
- **G2 = `science_gates.g2_registration_v2(g1_pass, dsr, pbo)`**：DSR≥0.95（`deflated_sharpe_ratio` 跑 headline deep 原始日序列·n_trials=账本累计·禁 dsr_from_stats 充数）∧ **家族 PBO≤0.25**（judged 4 胞 base 面 deep 日收益矩阵·`screening.pbo.cscv_pbo` CSCV-8——真分化后四胞家族矩阵·P3 幽灵孪生面不重演）。
- **x2 成本压测存活**：headline x2 面 Sharpe ≥ 0（成本翻倍不死）。
- **M1 t 值门**：`m1_t_value_gate`（t≥3.0·headline）。
- **G-SEG 覆盖门**：§3 政体分段门（不过=insufficient-sample 如实）。
- **律 A 普查门（双件门之二·§0.6）**：出场原因普查缺省栈占比 >20% → **verdict=consumption-blocked（先于 PASS/judged-negative 定谳·自动封锁下游消费）**。
- **确定性重现门（本批新增·升格面证据链守卫）**：LAD-EDGE/LAD-REP base 面逐字段==P3 deep 探索工件（§3 反重复披露）——失配=abort 禁 finalize（copy-adapt 漂移守卫）。
- **E1 四腿强制门【消费前置·P 族系继承】**：本批任何 verdict 数字被下游消费（watchlist 翻面/STRATEGY_LIBRARY 注册/族间 meta 结论）前必过 E1 四腿对账（r492/r301/r522 律）：Leg A as-burned 引擎重放逐 bp＋Leg A2 出场原因普查（=律 A 腿）＋Leg C 无引擎独立算术腿交叉验证（B/C 腿差 ≤5bp/日）；证据件=results/lowamp_deep_p1/e1_three_leg.json（跑后产出）；缺 E1 件或 FAIL=禁消费。
- **族级 PASS（全合取）**：G1' ∧ G2 ∧ x2 存活 ∧ M1 ∧ G-SEG 覆盖 ∧ 律 A ≤20% ∧ 重现门恒等；任一不合=**judged-negative**（诚实出 POTENTIAL_WATCHLIST 名单·O-2230 fast-track law 逐字；judged-negative=深轴族设计面真判负·出场轴已显式+双通道已修正+sizing 已真分化=无工具面缺陷可归咎）。
- 下游：PASS → E1 四腿门 → s4 intake（LOWAMP-DEEP-* 纸盘提案 fast-track + STRATEGY_LIBRARY 注册 + POTENTIAL_WATCHLIST 状态翻面）；judged-negative → E1 四腿门 → 如实出名单+族键入 CLOSED_FAMILIES（重开通道=new_evidence_new_prereg）。

## §5 跑前预测【写死于跑前】

1. **确定性重现（高置信）**：LAD-EDGE base 逐位==P3 工件（ret 0.604283·Sharpe 1.066348·n_trades 67·entries 69·maxDD −0.054658·n_days 3,230）；LAD-REP base==（0.625393·1.115291·72·74·−0.050424）；x2 面==（0.554954·0.979073·67 / 0.57354·1.020565·72）——同引擎同信号同 cutoff，invvol 语义零改动；失配=copy-adapt 漂移红灯。
2. **真 eq 面（全新·方向未知如实）**：选择集与 invvol 胞恒等、权重不同；收益差由两入选员 amp 比决定——预期落在 invvol 孪生 ±15% 收益带内（P3 legacy sens eq/invvol 同带证据 Sharpe 0.97-1.31）；**无点预测**（首测面）。
3. **G1' 判读=全批最大不确定面（honest 置顶）**：线位=max(deep 被动+0.10, μ_null+σ_null·√(2·ln N_eff))。被动项≈0.36+0.10=0.46 带（t18_deep_reval ew48 先证 0.3612·构造近似面）；null 项由**本批自有 null 池 σ 面构成**——若 σ_null≈0.16（t18 reval 随机入场族相邻证据）→ 线≈1.0·headline 1.066 边缘过；若 σ_null≈0.38（P3 legacy same-mask 族证据）→ 线≈2.1·判负。**G1' pass 概率诚实带宽 30-50%**——σ_null 实测即定谳，禁预支结论。
4. **M1 t≈3.8 预期 PASS**（1.066×√(3,230/252)=1.066×3.58；P3 legacy 面 t=2.945 挂在 13 年窗的 2 倍长度红利）。
5. **律 A 普查：0% 缺省出场预期**（P3 同机件实证 7 笔全 signal_reversal）。
6. **回撤面**：headline maxDD 预期 −5.5% 带；deep 全被动 EW maxDD −45.4%（t18 reval 先证）=防御面差值 ≥40pp 的族叙事面（描述性不替代 v2 门）。
7. **sens 描述面**：deep Sharpe 带预期 0.9-1.3（P3 legacy sens p05-p95 0.9709-1.3086 先验迁移·宇宙切换面如实降级为带宽预期）。
8. **G2 面**：DSR 在 n_trials≈61.7 万通缩下大概率 <0.95（P3 先例 0.2695·REV_P2 先例 0.0013-0.9941 长序列带）——G2 为注册门非生存门，判负照报不惊诧。

## §6 产物

- script: scripts/lowamp_deep_p1.py（probe | run --cell --axis deep --face | run --nulls | run --sensitivity | status | finalize | selftest；per-cell-face checkpoint 幂等=done-key skip；fail-closed exit 2/3；pool claim 握手 r497 三调用点）
- results/lowamp_deep_p1/：probe.json + cells_*.jsonl×8 + cont_*.json×8 + nulls.jsonl + sens.jsonl + cells.csv + lowamp_deep_p1_results.json（顶层 evidence_cutoff+cutoff_meta+gates 全链+nulls+sens+D6+政体分段+重现/被动面+账本）
- 语法登记=TRIAL_GRAMMAR_LEDGER 家族专用判决批行（LOWAMP-DEEP-P1·deep 宇宙面首个 W 带消费声明）
- 消费面：千人题库 deep 宇宙语法首批 + STRATEGY_LIBRARY 注册通道（PASS 面）+ POTENTIAL_WATCHLIST（judged-negative 面）+ 淬炼链第二炉（若存活→REFINE_BENCH_LAW §2 手段轴深轴淬炼）

## §7 跑后实证【r397 bm-c 一次定稿回填】

- **verdict=judged-negative**（2026-10-03 finalize·audit.machine=bm-c）：headline LAD-EDGE|deep|base 全期 Sharpe **1.066348 < skill_line 1.512**（数据驱动线=max(deep 被动 0.4717, μ_null 0.0755+σ_null 0.2782×√(2·ln 617,500))——null 项主导）；**DSR 0.700448 < 0.95**（T=3,229·skew 1.7065·kurt 33.71）；G2 eligible_v2=false → 族级判负。
- 过线门全绿面：M1 t=3.817093 PASS（≥3.0）·x2 存活 PASS（0.979073）·**律 A 普查 PASS（default_share=0.0·67 笔全 signal_reversal·双通道 held）**·G-SEG 覆盖 PASS（bear 746/bull 540/chop 94）·确定性重现 PASS（LAD-EDGE/LAD-REP base 逐字段==P3 deep 工件）·D6 max|corr|=0.1719<0.7（vs VOLATILITY-CE-01·新键 open 合法照跑）。
- headline：ret_full +60.43%·n_trades 67·n_entries 69·maxDD −5.47%·trades_per_year 5.23（12m 主判窗）；passive face=deep 首员等权 B&H Sharpe 0.371677/ret 0.971229（t18 reval ew48 先证 0.3612 同量级）。
- **真 eq 面深宇宙首测（§3 sizing 修正面兑现）**：LAD-EDGE-EQ Sharpe **0.454151**/maxDD **−27.78%**·LAD-REP-EQ **0.485123**/−26.15%——显著弱于 invvol 胞（1.066/1.115·maxDD −5.5%）且远出预测②「invvol ±15% 收益带」：**深轴族防御性由 invvol 低波权重轴承重**（eq 面不可复制）=对外叙事面重要负发现。
- nulls 三族：same-mask K=2,000 μ=0.0755·σ=0.2782（p05 −0.3465/p50 0.1132/p95 0.4708·seed 带 20337500）；block bootstrap B=2,000（块长 21td）obs 1.0663 vs p05 0.6306/p50 1.0731/p95 1.5066·p_ge_obs 0.5085；sign-flip P=2,000 p_two_sided **0.0**（abs_mean_obs 1.4884e-4 vs null p95 7.58e-5——信号方向性真实非噪声）。
- sens 描述面（K=500·不计 N_eff）：sharpe p05 0.4501/p50 0.5907/p95 1.1209·maxdd_worst −0.2905——预测⑦ legacy 迁移带 0.9-1.3 **证否**（宇宙切换降级面如实）。
- starts_12m_dist（n=1,380 起点读数）：median 0.0325·p25 0.0184·p75 0.0455·positive_share **85.29%**·best 0.0845·worst −2.56%；rolling_worst 3y 0.027/5y 0.0724/10y 0.2748；descriptive is_ann_ret 0.4019/oos_ann_ret 0.1444/x2_cost_drag_sharpe −0.0873。
- 政体分段：bear 746/bull 540/chop 94（12m 完整窗起点·G-SEG ≥50 三档全过）。
- 账本：batch_trials **2,008**（judged 4×2 判面 + nulls 2,000·sens 描述面不计）·prev_total 615,492 → **total 617,500**（voids_applied LOWAMP-P1/P2·ledger_head 消费=n3_r2_results.json r509 序零手抄）·evidence_cutoff 2026-09-22。
- **E1 四腿门=PASS**（消费前置律满足）：Leg A as-burned 引擎重放 Sharpe 1.066348 逐 bp 恒等+summary match；Leg A2 出场普查（=律 A 腿·0% 缺省）；Leg C 无引擎独立算术 **max diff 2e-8·days>5bp=0·letter within=True**——证据件 results/lowamp_deep_p1/e1_three_leg.json。
- **判据输入偏差如实披露（verdict 双向稳健）**：gates.dsr.n_trials 实测记录=2,008（批内口径）而非 §4 文字面的「账本累计 617,500」——按累计口径 sr_star 只升（0.0583→~0.087）DSR 只降，判负面**不变**（偏差方向=反保守侧·两口径同谳 judged-negative）；§7 如实记录实测值，禁按 §4 文面改写机读产物。
- 预测对账（§5 八条）：①全中（重现逐位+M1 3.817≈3.8）②**证否**（eq 带外）③方向中（σ_null 0.2782→线 1.512 判负·落「30-50% pass」诚实带宽的判负侧）④全中⑤全中（0% 缺省）⑥全中（maxDD −5.5% 带+被动面同量级）⑦**证否**（sens 带显著更低）⑧全中（DSR 判负照报）。
- 下游（§4 judged-negative 支）：族键 `lowamp_deep_xs` 入 CLOSED_FAMILIES **#8**（science_gates 代码面+research/CLOSED_FAMILIES.md 镜像面双落·reopen=新证据新预注册）；无 POTENTIAL_WATCHLIST 翻面（判负面不进潜力名单）；千人题库 deep 宇宙语法消费面照旧（TRIAL_GRAMMAR_LEDGER 判决批行 r596 冻结时已登记）；淬炼链第二炉不开（存活面不存在）。

## §8 批后复盘【s7-T】

- **跑前冻结=本件 commit**（freeze hash 入轮报告与池票）；冻结后禁改判据（回填限 §7/§8）；§5 资源申报=§0 算力预算（池 10 条目·workers 12）·§6 里程碑=烧毕→finalize→E1→消费四段（窗=10-09 开市前·验收 10-08）。
- **批后复盘（r397 bm-c·判负收口）**：全链如期走完（r596 冻结→池烧 10/10→finalize 41s→E1 四腿 PASS），**无工具面缺陷挂点**（出场轴双通道 0% 缺省+sizing 真分化四胞两两分化+重现门逐位恒等=机件面干净的机器证明）→判负为纯统计面真判负：机队级多重检验线 1.512（σ_null 0.2782×N_eff 617,500 驱动）对单族 Sharpe 1.07 的通过窗结构性收窄——与 §5 预测③「pass 概率 30-50%」诚实带宽一致，实测落判负侧，禁归咎工具面、禁翻案。
- 负发现价值（照报不粉饰）：①**真 eq 面证否**——深轴族防御性由 invvol 权重轴承重（eq maxDD −27.8% vs invvol −5.5%），复现该族防御性必须复制权重面=对外叙事硬边界；②sign-flip p=0——方向性真实非噪声；③sens 带显著低于 legacy 迁移预期——宇宙切换降级面如实入档；④判据输入偏差（dsr n_trials 批内口径）双向稳健披露（见 §7）——未来批件 finalize 的 n_trials 口径宜在 §4 判据节写死取值调用式（本批文字面「账本累计」与 runner 实参「批内」的缝=规格书写层教训，机读产物以实测为准）。
- E1 调试窗教训（工程面·04:26-04:38 四跑三改）：Leg C 独立算术对**一字断板日（high==low·零振幅）**的当日收益假设首版失配（ret_full nan→逐日差>5bp 1644 天）——正解=断板日收盘即成交价（引擎语义）+严格尾段切片对齐；终版 max diff 2e-8/days>5bp=0。教训已按捕获律评估入方法论资产卡（见本轮 METHODOLOGY_ASSETS 增补）。
