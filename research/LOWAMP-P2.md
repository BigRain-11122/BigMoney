# LOWAMP-P2 预注册 · 低振幅横截面日再平衡族·出场轴显式门首个应用（T-2026-10-01-140 action-4 冻结件）

> 裁决血统：O-20261001-1108 §三 GM 裁决（CEO 反瞎搞令随令裁决）——LOWAMP-P1 verdict VOID-with-face-note（prereg 自相矛盾：ALWAYS-ON 家族定义×引擎缺省出场栈）；族按设计本意 **+15.9%/夏普 +1.16**（T-136 审计 Legs B/C）**非判负**，经本考卷回供给池。执行票=T-2026-10-01-140（bm-a 认领 2026-10-01 11:2x commit 3a842a79e）。
> 出场轴显式门：firm/TRIAL_LABOR_LAW.md §4（O-20261001-1108 立法·**首个应用**）——本件 §0.6 为强制节，spec 无出场轴声明=冻结门拒。
> 模板=research/PREREG_TEMPLATE.md；跑前 commit 冻结；跑后只回填 §7/§8，禁改判据禁重跑；LOWAMP-P1 批本身禁重跑不变（本批=新批非重跑·T-136 "Either way" 线）。
> 部门=dept:策略（族规格）+研究（judgment 面）；lane=Money02 deep 面板在位的任何机队机（P1 同门）。

## §0 批件身份【必填·跑前】

- 批名/批号：**LOWAMP-P2**。**N_eff=2,008**＝judged cells 4 × 判面 2（base+x2）+ same-mask null draws 2,000（P1 同式·CN 家族先例 null draws 计入）；sensitivity Sobol 腿=描述面**不计 N_eff**（§3）。扩容即买单。
- 账本面：finalize 步 `science_gates.append_ledger(batch_name="LOWAMP-P2", batch_trials=2008, file_name="results/lowamp_p2/lowamp_p2_results.json", evidence_cutoff="2026-09-22")`（dict schema 唯一禁手抄 prev；LOWAMP-P1 的 −2,008 补偿分录已在链=ledger_head void 面自动净额·本批 prev 从净额 head 起）。
- 算力预算：**长活入池**（>5min 一律 runnable_pool·O-20260924-2100 s2）——分片=4 cells × 2 axes × 2 faces=16 cell-shards + nulls 片 + sensitivity 片 + finalize 片；workers_plan={"workers": 12, "priority": "BelowNormal"}（O-2130 s1.1·CEO 10% 余量令）；checkpoint+逐片日志；**跑批宿主门=Money02 deep 面板在位**（dir_nonempty=Money02/data/cache/t18_deep_panel/ohlcv·48 文件）；批报告必带 audit 段。

## §0.5 禁开方向硬闸【必填·跑前】

- 跑前过闸：`python Tools/banned_direction_gate.py --prereg research/LOWAMP-P2.md` → 退出 0=放行（fail-closed）。
- 人工预读结论：**零命中**——本批机制与 LOWAMP-P1 冻结面逐字同族（横截面**风险度量（振幅升序）**选低＋**常开**零前置＋core48 ETF 宇宙＋日频再平衡），P1 裁决 VOID 后机制面零新增方向；与注册表 v1.0 九类已证伪机制面逐一对照零重叠；禁向词面不在本件复述（机器闸为准·防否证模式词面自撞·r483 清洗律）。

## §0.6 出场轴显式声明【O-20261001-1108 立法·TRIAL_LABOR_LAW §4·本批强制节】

- **出场轴=②持有到底（ALWAYS-ON hold-through）**：族定义=常开持有——成员**只因横截面选择轮换离场**（当日跌出 Top-N 最低振幅入选集=entry≤0 信号出场·t22 `_run_cell` exit_sig=entry<=0 惯例逐字），**无价格类出场**（无止盈/无止损/无衰减踢出/无亏损时限/无持有上限）。
- **引擎缺省出场栈显式禁用【runner config 逐键申报】**：runner 对每个 judged cell 显式传 params——`take_profit_levels=()`（空梯·P3 永不触发）·`trailing_stop_activate=1e12`（P2 trailing 永不激活）·`initial_stop=-1.0`（止损价=0·正价格永不触发）·`time_decay_period=10**9`（P4 永不）·`loss_time_days=10**9`（P5 永不）·`global_hard_limit=10**9`（P6 永不）；`exit_signal` 注入=entry≤0 全矩阵（P1 signal_reversal 通道=族自有选择出场·保留）；**engine/exit_rules.py 与 engine/backtester.py 零触碰**（params 全暴露面=引擎自有接口·T-136 审计 as-burned 腿实证的同一通道反向使用）；T+1 执行与成本模型=引擎正典不变。
- 判读律：出场轴声明三选一（①策略自有出场=本批选择轮换出场属之·②持有到底声明=本批主声明·③template_default）——本批=①+②合体（选择轮换=族自有机制、价格类出场=零）；缺本节=门拒。

## §1 α 机制段【必填·D6】

- 机制勾选：**行为偏差**（主：彩票偏好/注意力稀缺——市场对手盘系统性超配高振幅「彩票型」资产〔MAX 效应族〕，低振幅资产长期低配=低波动异象；代价支付者=追高波动的行为对手盘）＋**结构性**（辅：机构委托条款/跟踪误差约束令其无法超配低振幅成员——「基准即枷锁」）。
- **散户凭什么赢【§1.2】**：**制度/容量**——低振幅倾斜散户规模容量无限、零杠杆需求（低波动异象机构套利通道=加杠杆持有低波资产，散户直接持有即得）；RETAIL_QUANT_TRACK §三引用台账：不重跑任何机构结论（低波动异象=公开文献常识面引用）；例外三问=本账户独有约束（场内 ETF 零杠杆直接持有·真实成本·本市场 2020-2026 窗）成立。
- **同族相关性准入检查【必填·D6】**：入批前 probe 步计算 headline（LA-REP·hold-through 面）日收益序列 vs **在册六员全部成员**日收益序列逐对 max|corr|（日收益口径·sleeve-tag 先例）；**max|corr| ≥ 0.7 → 拒收 fail-closed 禁烧**（数值与逐对清单 probe 件落盘 results/lowamp_p2/probe.json 后方可点火）；P1 probe 先证=0.1688 admit（void 前同族面·出场轴变更后以本批 fresh probe 实测为准）。
- M1 t 面【必填申报】：`science_gates.t_from_sharpe(sharpe_full, n_periods)` 派生面（headline cell）；判据=`science_gates.m1_t_value_gate`（H/L/Z 门槛 **t≥3.0**）；缺面=missing_input 拒收。
- M3 闭合族对号：family_key=**lowamp_daily_xs**——CLOSED_FAMILIES 六在册键无一命中=open 照跑；**P1 判负已 VOID 不闭合本族**（O-20261001-1108 §三裁决指针）；族间对号同 P1（GRID-SLEEVE 带状执行族无关·CN-DIV-LOWVOL-ROT=monthly-rotation 族·本族=日频横截面振幅排序族）。

## §2 数据与面板【必填·跑前探针事实，非结果】

- 宇宙/池：**core48**（legacy 轴·48 员）＋ **T-18 增长成员面板**（deep 轴·manifest PASS·48 员·panel_start=2013-06-17）。
- **价格面=core48 adjusted face（P1 §2 逐字继承）**：两轴均以 T-19 复权视图为 19 受影响员价格源（振幅信号必须吃复权面）；raw 面权威性不动（D2 锁盒零改写）；t19 gates 既有 PASS 件只读引用。
- **数据锚面定义四元组【G-ANCHOR-FACE】**：legacy 轴=`data/daily/sh<code>.csv`＋`live.paper.load_core`＋起算 2020-01-02＋预热 252td（19 员 adjusted_view parquet 逐员替换）；deep 轴=`Money02/data/cache/t18_deep_panel/ohlcv/<code>.parquet`＋`pd.read_parquet`＋起算 2013-06-17＋预热 252td（GF 硬门 19/19；amount=volume×close disclosed proxy）；政体标签=`t22_virtual_timepoints.regime_proxy(close['510300'])`＋预热 200td。
- **探针-锚同面断言**：runner probe 实载路径与四元组逐位比对六断言 fail-closed；一面不符=**面错配 VOID**。
- 窗口与 **evidence_cutoff=2026-09-22**（前向锁盒 D2·两轴一律截 ≤cutoff 再联合；cutoff 后新 bar 锁定不得回流）；结果 JSON 顶层 `evidence_cutoff` + `science_gates.cutoff_meta("2026-09-22")`（缺字段=C2 VIOLATION）。
- 起点集：**T-22 冻结枚举律逐字**——`enumerate_starts`（pos≥252td ∧ ≥126td 前瞻 ∧ 当日上市成员数≥24）确定性全枚举；**G-CENSUS 门：起点数逐位=={legacy: 1,254, deep: 1,506}**（P1 零跑修正案后冻结读数·raw/adj 双面同读）。
- 数据完备门（不过门禁跑）：①legacy 48 员/adj 19/19；②deep manifest PASS ∧ 48 员 ∧ ohlcv 48 文件；③cutoff 截断后两轴末行==2026-09-22；④零重复日期+单调；⑤G-CENSUS。
- **流动性/可交易闸（票面 mandatory 继承）**：选择资格=有效 amp（满 W 窗史）∧ 当日 close notna ∧ volume>0 ∧ amount>0 ∧ **amt20_median ≥ ¥50,000,000**（deep 轴 amount=proxy 面如实披露）。
- DATA_GAP 对号：同 P1（缺项 5→legacy 2020 起为正典设计面、deep 2013 起在仓覆盖）。

## §3 方法学【必填·冻结】

- **信号定义（冻结·炉子血统参数带逐字·P1 同族）**：amp(t)＝近 W 交易日收盘-收盘日收益滚动标准差（`min_periods=W`·严格因果）；横截面升序排名取 **Top-N 最低振幅**；权重 **invvol**（w_i∝1/amp_i·归一）或 **eq**（1/N）；**常开**（零前置条件）；**日频再平衡**（信号日 T 收盘算、引擎正典 T+1 执行）。
- **judged cells 4（跑前写死·P1 同格·非结果驱动）**：①**LA-REP**：W=89·N=2·invvol（炉子代表格 C0096 逐字）；②**LA-EQ**：W=89·N=2·eq；③**LA-T3**：W=89·N=3·invvol；④**LA-EDGE**：W=104·N=2·invvol（带上缘）。
- **执行语义【§0.6 出场轴为本批唯一变更面】**：entry_signal=当日入选 ∧ exit_signal=entry≤0（选择轮换出场·全矩阵注入）→ `engine.run_backtest`（T+1·成本模型·§0.6 缺省栈显式禁用 params 逐键）→ **持有到底**（价格类出场零触发·成员仅因跌出 Top-N 离场）；x2 面=`CostPatch(2.0)` 乘数（r82 修正面）；每起点 fresh-entry 洁净切片（入场即目标权·孪生 naive 先例）。
- **窗族 {6m=126·12m=252·24m=504}**：最长窗一次跑+同曲线切片（P-5 律）；**主判窗=12m 完整窗**·partial 窗如实标记；被动基线=起点日已上市成员等权 B&H 同窗（t22 逐字）；beat_k=ret_k>p_ret_k。
- **null 对照（≥2,000 三族全律·P1 同式）**：①**null_pool（G1' skill line 源）**：K=2,000 **same-mask 随机选择 null**——每日同一资格掩码宇宙内均匀随机选 N 员（同 N·同窗·同执行·eq 权·**`rng([20334500, k])` 子流律·本批新种子带**），全面板模拟取 Sharpe 分布（μ_null/σ_null 入 skill_line_v2）；掩码恒等断言（G-MASK：null 日宇宙==真实 cell 日宇宙逐位）。②**block bootstrap B=2,000**（headline 日收益·块长 21td）＋③**sign-flip permutation P=2,000**（双法并列=RANDOM_LARGE_SAMPLE_LAW §3 逐字）。
- **sensitivity 腿（§2.2 履约·描述面零判定宣称）**：N=500 空间填充均匀抽取 over（W∈[77,104] 整数·N∈{2,3}·sizing∈{invvol,eq}·gate=常开固定·**出场轴=§0.6 hold-through 同面**），legacy 轴全面板单跑，产物=Sharpe/均值/maxDD 分布描述列，**不计 N_eff、不设门、禁幸存者宣称**；`rng([20333500, k])`；起点抽样=`rng([20334000, k])`。
- **政体分段**：每起点 regime 标签（t22 3-way proxy）→ 分段统计；**G-SEG 覆盖门：每轴 bear/bull/chop 各 ≥50 起点 ∧ ≥4 个历法分段披露**——不过=verdict=**insufficient-sample**。
- 成本口径声明【CN-C7】：**ETF=26.082bp/往返**（`knowledge/cost_spec.py X1_RATE=0.0013041` 单边 **import 派生禁手抄**·runner 断言恒等）；股票面 N/A（零个股）；¥1,000,000 账户口径申报；V2 ADV 滑点面对 ETF 日频零售量级=不适用如实注记。
- **闭合族对号声明【M3】**：open，无「新证据增量」义务。
- **反重复披露（票面 anti-dup）**：LOWAMP-P1 已烧批禁重跑（VOID 裁决不改变冻结批零重跑铁律）；本批=W∈[77,104] 带**唯一合法在烧面**（P1 判负 VOID→带消费回退→本批重开·TRIAL_GRAMMAR_LEDGER 2026-10-01 11:4x 翻面行在案）；炉子 1060 格勘探面零重烧（证据件在册引用）。

## §4 判据【必填·跑前写死，禁看结果调线】

- **G1' v2 = `science_gates.g1_prime_v2(sharpe_full, returns, batch_cells=2008, pool='core48', n_trades, n_entries, null_pool=<本批 2,000 same-mask own 池>)`**（headline=LA-REP·**legacy 轴全面板** 2020-01-02→2026-09-22 连续单跑·hold-through 面）：全期 Sharpe > skill_line_v2（数据驱动=max(被动+0.10, μ_null+σ_null·√(2·ln N_eff))·**N_eff=净额账本 head+2,008**〔LOWAMP-P1 −2,008 void 已净·O-20261001-1108 §三〕）∧ 平稳 bootstrap CI 下界>0 ∧ entries≥30（F6 双口径）；逐列披露 skill_line/bootstrap_ci/trade_gate 全输入。
- **G2 = `science_gates.g2_registration_v2(g1_pass, dsr, pbo)`**：DSR≥0.95（`deflated_sharpe_ratio` 跑 LA-REP legacy 全面板原始日序列·禁 dsr_from_stats 充数）∧ **家族 PBO≤0.25**（judged 4 cells 带内格）——P1 同门逐字。
- **双轴确认**：deep 轴 LA-REP 同门重跑（CI 下界>0·方向一致）。
- **x2 成本压测存活**：LA-REP x2 面 Sharpe ≥ 0（成本翻倍不死）。
- **M1 t 值门**：`m1_t_value_gate`（t≥3.0·headline）。
- **G-SEG 覆盖门**：§3 政体分段门（不过=insufficient-sample 三态如实）。
- **族级 PASS（全合取）**：G1' ∧ G2 ∧ 双轴确认 ∧ x2 存活 ∧ M1 ∧ G-SEG 覆盖；任一不合=**judged-negative**（诚实出 POTENTIAL_WATCHLIST 名单·O-2230 fast-track law 逐字）；hold-through 面判负=族设计面真判负（出场轴已显式·无 prereg 自相矛盾面可归咎）。
- 下游：PASS → s4 intake（LOWAMP-* 纸盘提案 fast-track + STRATEGY_LIBRARY 注册 + POTENTIAL_WATCHLIST 状态翻面）；judged-negative → 如实出名单。

## §5-§8 预留

- §5 资源申报/§6 里程碑/§7 回填（全起点分布+预测对账+损耗账）/§8 结论三态：跑后回填，跑前留空。
- **跑前冻结=本件 commit**（freeze hash 入轮报告与 pool 票）；冻结后禁改判据（回填限 §7/§8）。
